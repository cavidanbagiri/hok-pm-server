# repositories/static_repository.py
import pandas as pd
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from typing import Dict, Any, Tuple, Optional
import logging

from models.common_model import (
    TypesModel, SubTypeModel, Size1Model, Size2Model,
    MaterialModel, DescriptionModel, TypeModel, UomModel, StockDataModel, LocationModel, AreaModel, MtoModel
)
from repositories.common_repository import CheckAdminManagerAuthorize

# Setup logging
log_filename = f'stock_import_errors_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
# logging.basicConfig(
#     filename=log_filename,
#     level=logging.ERROR,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )


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



# Setup logging
# log_filename = f'mto_import_errors_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
# logging.basicConfig(
#     filename=log_filename,
#     level=logging.ERROR,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )


class ExcelMTOALLImporter:

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

        # Cache for lookups to reduce database queries
        self.location_cache = {}
        self.area_cache = {}
        self.description_cache = {}
        self.stock_data_cache = {}
        self.uom_cache = {}
        self.iso_stock_kod_cache = set()  # Track unique ISO_STOCK_KOD values

    async def get_or_cache_location(self, name: str) -> Optional[int]:
        """Get location ID from cache or database"""
        if not name or pd.isna(name):
            return None

        name_upper = str(name).strip().upper()

        # Check cache first
        if name_upper in self.location_cache:
            return self.location_cache[name_upper]

        # Query database
        result = await self.db_session.execute(
            select(LocationModel).where(LocationModel.name == name_upper)
        )
        location = result.scalar_one_or_none()

        if location:
            self.location_cache[name_upper] = location.id
            return location.id
        else:
            raise ValueError(f"Location not found: {name}")

    async def get_or_cache_area(self, name: str, description: str = None) -> Optional[int]:
        """Get area ID from cache or database"""
        if not name or pd.isna(name):
            return None

        name_upper = str(name).strip().upper()
        cache_key = name_upper

        # Check cache first
        if cache_key in self.area_cache:
            return self.area_cache[cache_key]

        # Query database
        query = select(AreaModel).where(AreaModel.name == name_upper)
        if description and not pd.isna(description):
            desc_upper = str(description).strip().upper()
            query = query.where(AreaModel.description == desc_upper)

        result = await self.db_session.execute(query)
        area = result.scalar_one_or_none()

        if area:
            self.area_cache[cache_key] = area.id
            return area.id
        else:
            raise ValueError(f"Area not found: {name} (description: {description})")

    async def get_or_cache_description(self, name: str) -> Optional[int]:
        """Get description ID from cache or database"""
        if not name or pd.isna(name):
            return None

        name_upper = str(name).strip().upper()

        # Check cache first
        if name_upper in self.description_cache:
            return self.description_cache[name_upper]

        # Query database
        result = await self.db_session.execute(
            select(DescriptionModel).where(DescriptionModel.name == name_upper)
        )
        description = result.scalar_one_or_none()

        if description:
            self.description_cache[name_upper] = description.id
            return description.id
        else:
            raise ValueError(f"Description not found: {name}")

    async def get_or_cache_stock_data(self, stock_code: str) -> Optional[int]:
        """Get stock_data ID from cache or database"""
        if not stock_code or pd.isna(stock_code):
            return None

        stock_code_upper = str(stock_code).strip().upper()

        # Check cache first
        if stock_code_upper in self.stock_data_cache:
            return self.stock_data_cache[stock_code_upper]

        # Query database
        result = await self.db_session.execute(
            select(StockDataModel).where(StockDataModel.stock_code == stock_code_upper)
        )
        stock_data = result.scalar_one_or_none()

        if stock_data:
            self.stock_data_cache[stock_code_upper] = stock_data.id
            return stock_data.id
        else:
            raise ValueError(f"Stock code not found: {stock_code}")

    async def get_or_cache_uom(self, name: str) -> Optional[int]:
        """Get UOM ID from cache or database"""
        if not name or pd.isna(name):
            return None

        name_upper = str(name).strip().upper()

        # Check cache first
        if name_upper in self.uom_cache:
            return self.uom_cache[name_upper]

        # Query database
        result = await self.db_session.execute(
            select(UomModel).where(UomModel.name == name_upper)
        )
        uom = result.scalar_one_or_none()

        if uom:
            self.uom_cache[name_upper] = uom.id
            return uom.id
        else:
            raise ValueError(f"UOM not found: {name}")

    async def check_iso_stock_kod_duplicate(self, iso_stock_kod: str) -> bool:
        """Check if ISO_STOCK_KOD already exists in current import session"""
        if iso_stock_kod in self.iso_stock_kod_cache:
            return True
        self.iso_stock_kod_cache.add(iso_stock_kod)
        return False

    async def import_excel(self):
        """Main method to import MTO Excel data"""

        # if not os.path.exists(self.excel_path):
        #     raise HTTPException(404, f"Excel file not found: {self.excel_path}")
        #
        #     # Read Excel
        # df = pd.read_excel(self.excel_path, engine='openpyxl')
        #
        # # DEBUG: Print actual column names
        # print("\n=== ACTUAL EXCEL COLUMNS ===")
        # for i, col in enumerate(df.columns):
        #     print(f"{i}: '{col}'")
        # print("=============================\n")

        """Main method to import MTO Excel data"""

        if not os.path.exists(self.excel_path):
            raise HTTPException(404, f"Excel file not found: {self.excel_path}")

        # Read Excel
        df = pd.read_excel(self.excel_path, engine='openpyxl')

        # Clean column names
        df.columns = df.columns.str.strip()

        # DEBUG: Print MTO actual column names
        print("\n=== MTO ACTUAL EXCEL COLUMNS ===")
        for i, col in enumerate(df.columns):
            print(f"{i}: '{col}'")
        print("================================\n")

        self.stats["total_rows"] = len(df)

        # Clean column names (strip spaces)
        df.columns = df.columns.str.strip()

        self.stats["total_rows"] = len(df)

        if not os.path.exists(self.excel_path):
            raise HTTPException(404, f"Excel file not found: {self.excel_path}")

        # Read Excel
        df = pd.read_excel(self.excel_path, engine='openpyxl')
        self.stats["total_rows"] = len(df)

        print(f"\n{'=' * 60}")
        print(f"Starting MTO import of {self.stats['total_rows']} rows...")
        print(f"Log file: {log_filename}")
        print(f"{'=' * 60}\n")

        mto_objects = []
        batch_size = 500  # Commit every 500 rows

        for index, row in df.iterrows():
            try:
                mto_data = await self.process_row(row, index + 2)
                mto_objects.append(mto_data)

                # Commit batch
                if len(mto_objects) >= batch_size:
                    await self.bulk_insert(mto_objects)
                    mto_objects = []

            except Exception as e:
                self.stats["failed"] += 1
                error_msg = f"Row {index + 2}: {str(e)}"
                logging.error(error_msg)
                print(f"❌ {error_msg}")
                continue

        # Insert remaining rows
        if mto_objects:
            await self.bulk_insert(mto_objects)

        # Print summary
        print(f"\n{'=' * 60}")
        print(f"MTO IMPORT SUMMARY")
        print(f"{'=' * 60}")
        print(f"✅ Total rows: {self.stats['total_rows']}")
        print(f"✅ Success: {self.stats['success']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"⏭️  Skipped (duplicate ISO_STOCK_KOD): {self.stats['skipped']}")
        print(f"📄 Log file: {self.stats['log_file']}")
        print(f"{'=' * 60}\n")

        return self.stats

    async def process_row(self, row: pd.Series, row_num: int) -> MtoModel:
        """Process single row and return MtoModel object"""

        # Extract required fields
        no = str(row.get('NO', '')).strip()
        if not no or pd.isna(no):
            raise ValueError("NO is required")

        reference_mto = str(row.get('REFERANCE_MTO', '')).strip()
        if not reference_mto or pd.isna(reference_mto):
            raise ValueError("REFERANCE_MTO is required")

        # Handle date - allow NULL
        mto_date = row.get('MTO_DATE')
        if pd.isna(mto_date) or mto_date is None:
            mto_date = None
        else:
            try:
                # If it's already a datetime, keep it
                if not isinstance(mto_date, (datetime, pd.Timestamp)):
                    mto_date = pd.to_datetime(mto_date)
            except Exception as e:
                print(f"⚠️ Row {row_num}: Invalid date format '{mto_date}', setting to NULL")
                mto_date = None

        # Get foreign key IDs
        location_id = await self.get_or_cache_location(row.get('LOCATION'))

        # AREA (required)
        area_name = row.get('AREA')
        area_desc = row.get('AREA_2_DESC')
        area_id = await self.get_or_cache_area(area_name, area_desc)

        # AREA_2 (optional)
        area_2_name = row.get('AREA_2')
        area_2_id = None
        if area_2_name and not pd.isna(area_2_name):
            area_2_id = await self.get_or_cache_area(area_2_name, None)

        # AREA_2_DESC (optional)
        area_2_desc_name = row.get('AREA_2_DESC')
        area_2_desc_id = None
        if area_2_desc_name and not pd.isna(area_2_desc_name):
            area_2_desc_id = await self.get_or_cache_description(area_2_desc_name)

        # Stock Code
        stock_code = row.get('STOCK_CODE')
        stock_data_id = await self.get_or_cache_stock_data(stock_code)

        # Get stock_data object for ISO_STOCK_KOD computation
        stock_data_obj = await self.db_session.get(StockDataModel, stock_data_id)
        if not stock_data_obj:
            raise ValueError(f"Stock data not found for ID: {stock_data_id}")

        # UOM
        uom_name = row.get('UOM')
        uom_id = await self.get_or_cache_uom(uom_name)

        # Check ISO_STOCK_KOD uniqueness (computed field)
        isometric_drawing_no = str(row.get('ISOMETRIC_DRAWING_NO', '')).strip() if row.get(
            'ISOMETRIC_DRAWING_NO') and not pd.isna(row.get('ISOMETRIC_DRAWING_NO')) else None
        iso_stock_kod = None
        if isometric_drawing_no and stock_code:
            iso_stock_kod = f"{isometric_drawing_no}{str(stock_code).strip().upper()}"
            if await self.check_iso_stock_kod_duplicate(iso_stock_kod):
                self.stats["skipped"] += 1
                raise ValueError(f"Duplicate ISO_STOCK_KOD: {iso_stock_kod}")

        # Create MTO object
        mto = MtoModel(
            no=no,
            reference_mto=reference_mto,
            mto_date=mto_date,  # Can be None now
            location_id=location_id,
            pid_no=str(row.get('PID_NO', '')).strip() if row.get('PID_NO') and not pd.isna(row.get('PID_NO')) else None,
            line_no=str(row.get('LINE_NO', '')).strip() if row.get('LINE_NO') and not pd.isna(
                row.get('LINE_NO')) else None,
            isometric_drawing_no=isometric_drawing_no,
            iso_rev=str(row.get('ISO_REV', '')).strip() if row.get('ISO_REV') and not pd.isna(
                row.get('ISO_REV')) else None,
            iso_and_rev=str(row.get('ISO_AND_REV', '')).strip() if row.get('ISO_AND_REV') and not pd.isna(
                row.get('ISO_AND_REV')) else None,
            spec=str(row.get('SPEC', '')).strip() if row.get('SPEC') and not pd.isna(row.get('SPEC')) else None,
            quantity=float(row.get('QUANTITY', 0)) if not pd.isna(row.get('QUANTITY')) else 0,
            required_area=float(row.get('REQUIRED_AREA', 0)) if not pd.isna(row.get('REQUIRED_AREA')) else None,
            required_iso=float(row.get('REQUIRED_ISO', 0)) if not pd.isna(row.get('REQUIRED_ISO')) else None,
            comment=str(row.get('COMMENT', '')).strip() if row.get('COMMENT') and not pd.isna(
                row.get('COMMENT')) else None,
            area_id=area_id,
            area_2_id=area_2_id,
            area_2_desc_id=area_2_desc_id,
            stock_data_id=stock_data_id,
            uom_id=uom_id,
            created_by_id=self.user_id
        )

        self.stats["success"] += 1
        print(f"✅ Row {row_num}: Processed '{reference_mto}' - {no}")

        return mto

    async def bulk_insert(self, mto_objects: list):
        """Bulk insert MTO objects"""
        try:
            self.db_session.add_all(mto_objects)
            await self.db_session.commit()
            print(f"💾 Committed {len(mto_objects)} rows to database")
        except Exception as e:
            await self.db_session.rollback()
            error_msg = f"Bulk insert failed: {str(e)}"
            logging.error(error_msg)
            print(f"❌ {error_msg}")
            raise e