# routers/static_data_router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from auth.token_handler import TokenHandler
from database.setup import get_db
from models.common_model import StockDataModel, TypeModel
from repositories.static_repository import ExcelStockImporter

from repositories.common_repository import CheckAdminManagerAuthorize

router = APIRouter()


@router.post("/import_stock_excel", status_code=200)
async def import_stock_excel(
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')

        # Check if user is admin/manager
        auth_check = CheckAdminManagerAuthorize(db, int(user_id))
        await auth_check.check_admin_or_manager()

        # Excel file path (adjust path as needed)
        excel_path = "static_datas/Stock_data.xlsx"

        # Import Excel
        importer = ExcelStockImporter(db, excel_path, int(user_id))
        result = await importer.import_excel()

        return result

    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


#####################################################################################################################################################################################################################################################




import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
# Замените StockModel на вашу реальную SQLAlchemy-модель склада/товаров
from models.common_model import StockDataModel
import asyncio
from functools import partial
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

class ExcelStockExporter:
    def __init__(self, db_session: AsyncSession, file_path: str):
        self.db_session = db_session
        self.file_path = file_path

    async def export_to_excel(self):
        # 1. Запрос к базе данных со всеми необходимыми JOIN'ами через joinedload.
        # Это предотвратит проблему N+1 запросов и подгрузит связанные имена за один раз.
        query = (
            select(StockDataModel)
            .options(
                joinedload(StockDataModel.uom),
                joinedload(StockDataModel.type).options(
                    joinedload(TypeModel.type),
                    joinedload(TypeModel.subtype),
                    joinedload(TypeModel.size1),
                    joinedload(TypeModel.size2),
                    joinedload(TypeModel.material),
                    joinedload(TypeModel.description)
                )
            )
        )

        result = await self.db_session.execute(query)
        stocks = result.scalars().all()

        # 2. Собираем плоскую структуру данных для Excel таблицы
        data = []
        for stock in stocks:
            # Безопасное извлечение связанных объектов (на случай, если size2 или другие поля nullable)
            t_model = stock.type
            uom_name = stock.uom.name if stock.uom else None

            # Извлекаем названия из вложенных связей TypeModel
            type_name = t_model.type.name if t_model and t_model.type else None
            subtype_name = t_model.subtype.name if t_model and t_model.subtype else None
            size1_name = t_model.size1.name if t_model and t_model.size1 else None
            size2_name = t_model.size2.name if t_model and t_model.size2 else None
            material_name = t_model.material.name if t_model and t_model.material else None
            description_name = t_model.description.name if t_model and t_model.description else None

            # Добавляем строку данных
            data.append({
                "Stock ID": stock.id,
                "Stock Code": stock.stock_code,
                "Alternative ID": stock.alternative_id,
                "Old Code": stock.old_code,
                "Comment": stock.comment,
                "UOM (Ед. изм.)": uom_name,
                "Type": type_name,
                "Subtype": subtype_name,
                "Size 1": size1_name,
                "Size 2": size2_name,
                "Thickness 1": t_model.thickness_1 if t_model else None,
                "Thickness 2": t_model.thickness_2 if t_model else None,
                "Material": material_name,
                "Description": description_name
            })

        # 3. Переводим в DataFrame
        df = pd.DataFrame(data)

        # Если база пустая, создаем пустой DataFrame с нужными колонками
        if df.empty:
            df = pd.DataFrame(columns=[
                "Stock ID", "Stock Code", "Alternative ID", "Old Code", "Comment",
                "UOM (Ед. изм.)", "Type", "Subtype", "Size 1", "Size 2",
                "Thickness 1", "Thickness 2", "Material", "Description"
            ])

        # 4. Асинхронно записываем Excel-файл на диск в фоновом потоке
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            partial(df.to_excel, self.file_path, index=False, engine='openpyxl')
        )

@router.get("/export_stock_excel", status_code=200)
async def export_stock_excel(
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')

        # 1. Проверяем права пользователя
        auth_check = CheckAdminManagerAuthorize(db, int(user_id))
        await auth_check.check_admin_or_manager()

        # 2. Путь для сохранения временного файла экспорта
        export_dir = "static_datas"
        os.makedirs(export_dir, exist_ok=True)
        excel_path = os.path.join(export_dir, "Exported_Stock_data.xlsx")

        # 3. Вызываем класс экспортера
        exporter = ExcelStockExporter(db, excel_path)
        await exporter.export_to_excel()

        # 4. Возвращаем файл пользователю для скачивания
        return FileResponse(
            path=excel_path,
            filename="Stock_data.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')
