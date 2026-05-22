# repositories/static_repository.py
import pandas as pd
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from typing import Dict, Any, Tuple
import logging

from models.common_model import (
    TypesModel, SubTypeModel, Size1Model, Size2Model,
    MaterialModel, DescriptionModel, TypeModel, UomModel, StockDataModel
)
from repositories.common_repository import CheckAdminManagerAuthorize

# Setup logging
log_filename = f'stock_import_errors_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    filename=log_filename,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class ExcelStockImporter:

    def __init__(self, db_session: AsyncSession, excel_path: str, user_id: int):
        self.db_session = db_session
        self.excel_path = excel_path
        self.user_id = user_id
        self.stats = {
            "total_rows": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "log_file": log_filename
        }

    async def get_or_create_type_lookup(self, model_class, name: str, field_name: str):
        """Generic method to get or create lookup records"""
        if not name or pd.isna(name):
            return None

        name_upper = str(name).strip().upper()

        # Check if exists
        result = await self.db_session.execute(
            select(model_class).where(model_class.name == name_upper)
        )
        record = result.scalar_one_or_none()

        if record:
            return record

        # Create new
        record = model_class(name=name_upper)
        self.db_session.add(record)
        await self.db_session.flush()
        return record

    async def get_or_create_type_model(self, row: Dict[str, Any]) -> Tuple[int, bool]:
        """Get or create TypeModel based on combination"""

        # Get all lookup IDs
        types = await self.get_or_create_type_lookup(TypesModel, row.get('TYPE'), 'TYPE')
        subtype = await self.get_or_create_type_lookup(SubTypeModel, row.get('SUB-TYPE'), 'SUB-TYPE')
        size1 = await self.get_or_create_type_lookup(Size1Model, row.get('SIZE1'), 'SIZE1')
        size2 = await self.get_or_create_type_lookup(Size2Model, row.get('SIZE2'), 'SIZE2')
        material = await self.get_or_create_type_lookup(MaterialModel, row.get('MATERIAL'), 'MATERIAL')
        description = await self.get_or_create_type_lookup(DescriptionModel, row.get('DESCRIPTION'), 'DESCRIPTION')

        # Get thickness values
        thickness_1 = str(row.get('THK1', '')).strip().upper() if row.get('THK1') and not pd.isna(
            row.get('THK1')) else None
        thickness_2 = str(row.get('THK2', '')).strip().upper() if row.get('THK2') and not pd.isna(
            row.get('THK2')) else None

        # Check if TypeModel already exists with this combination
        query = select(TypeModel).where(
            TypeModel.type_id == types.id,
            TypeModel.subtype_id == subtype.id if subtype else TypeModel.subtype_id.is_(None),
            TypeModel.size1_id == size1.id,
            TypeModel.size2_id == size2.id if size2 else TypeModel.size2_id.is_(None),
            TypeModel.material_id == material.id,
            TypeModel.description_id == description.id,
            TypeModel.thickness_1 == thickness_1,
            TypeModel.thickness_2 == thickness_2
        )

        result = await self.db_session.execute(query)
        type_model = result.scalar_one_or_none()

        if type_model:
            return type_model.id, True  # Reused

        # Create new TypeModel
        type_model = TypeModel(
            type_id=types.id,
            subtype_id=subtype.id if subtype else None,
            size1_id=size1.id,
            size2_id=size2.id if size2 else None,
            material_id=material.id,
            description_id=description.id,
            thickness_1=thickness_1,
            thickness_2=thickness_2
        )
        self.db_session.add(type_model)
        await self.db_session.flush()
        return type_model.id, False  # New created

    async def import_excel(self):
        """Main method to import Excel data"""

        if not os.path.exists(self.excel_path):
            raise HTTPException(404, f"Excel file not found: {self.excel_path}")

        # Read Excel
        df = pd.read_excel(self.excel_path)
        self.stats["total_rows"] = len(df)

        print(f"Starting import of {self.stats['total_rows']} rows...")
        print(f"Log file: {log_filename}")

        for index, row in df.iterrows():
            try:
                await self.import_row(row, index + 2)
            except Exception as e:
                self.stats["failed"] += 1
                error_msg = f"Row {index + 2}: {str(e)}"
                logging.error(error_msg)
                print(error_msg)
                continue

        # Final commit
        await self.db_session.commit()

        # Print summary
        print(f"\n=== Import Summary ===")
        print(f"Total rows: {self.stats['total_rows']}")
        print(f"Success: {self.stats['success']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Skipped (duplicate stock_code): {self.stats['skipped']}")
        print(f"Log file: {self.stats['log_file']}")

        return self.stats

    async def import_row(self, row: pd.Series, row_num: int):
        """Import single row"""

        # Extract stock_code (required)
        stock_code = str(row.get('STOCK CODE', '')).strip().upper()
        if not stock_code or pd.isna(stock_code):
            raise ValueError("STOCK CODE is required")

        # Check if stock_code already exists
        existing = await self.db_session.execute(
            select(StockDataModel).where(StockDataModel.stock_code == stock_code)
        )
        if existing.scalar_one_or_none():
            self.stats["skipped"] += 1
            print(f"Row {row_num}: Stock code '{stock_code}' already exists - SKIPPED")
            return

        # Get UOM
        uom_name = str(row.get('UOM', '')).strip().upper()
        if not uom_name or pd.isna(uom_name):
            raise ValueError(f"UOM is required for stock code: {stock_code}")

        uom = await self.get_or_create_type_lookup(UomModel, uom_name, 'UOM')

        # Get or create TypeModel combination
        type_id, reused = await self.get_or_create_type_model(row)

        # Create StockDataModel
        stock_data = StockDataModel(
            stock_code=stock_code,
            alternative_id=str(row.get('ALTERNATIVE ID', '')).strip().upper() if row.get(
                'ALTERNATIVE ID') and not pd.isna(row.get('ALTERNATIVE ID')) else None,
            old_code=str(row.get('OLD CODE', '')).strip().upper() if row.get('OLD CODE') and not pd.isna(
                row.get('OLD CODE')) else None,
            comment=str(row.get('COMMENT', '')).strip() if row.get('COMMENT') and not pd.isna(
                row.get('COMMENT')) else None,
            type_id=type_id,
            uom_id=uom.id
        )

        self.db_session.add(stock_data)
        self.stats["success"] += 1

        status = "REUSED" if reused else "NEW"
        print(f"Row {row_num}: Imported '{stock_code}' (Type combination: {status})")