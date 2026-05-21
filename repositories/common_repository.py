# repositories/common_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from models.user_model import UserModel, StatusModel
from models.common_model import AreaModel, LocationModel, UomModel, TypeModel, StockDataModel

from schemas.common_schema import CreateStockSchema, CreateTypeSchema, CreateUomSchema, CreateLocationSchema, \
    CreateAreaSchema


class CheckAdminManagerAuthorize:

    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id

    async def check_admin_or_manager(self):
        query = select(UserModel).where(UserModel.id == self.user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        print(f'status  is ')

        if not user:
            raise HTTPException(404, "User not found")

        status_query = select(StatusModel).where(StatusModel.id == user.status_id)
        status_result = await self.db.execute(status_query)
        status = status_result.scalar_one_or_none()

        if not status:
            raise HTTPException(404, "Status not found")

        if status.status.lower() not in ["admin", "manager"]:
            raise HTTPException(403, "Authorization Error. Please write to admin")

        return user


class CreateAreaRepository:

    def __init__(self, db_session: AsyncSession, data: CreateAreaSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_area(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        area = AreaModel(
            name=self.data.name,
            description=self.data.description,
            project_id=self.data.project_id
        )

        self.db_session.add(area)
        await self.db_session.commit()
        await self.db_session.refresh(area)

        return area


class CreateLocationRepository:

    def __init__(self, db_session: AsyncSession, data: CreateLocationSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_location(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        location = LocationModel(
            name=self.data.name,
            project_id=self.data.project_id
        )

        self.db_session.add(location)
        await self.db_session.commit()
        await self.db_session.refresh(location)

        return location


class CreateUomRepository:

    def __init__(self, db_session: AsyncSession, data: CreateUomSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_uom(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        # Check if UOM already exists
        existing = await self.db_session.execute(
            select(UomModel).where(UomModel.name == self.data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(409, "UOM already exists")

        uom = UomModel(name=self.data.name)

        self.db_session.add(uom)
        await self.db_session.commit()
        await self.db_session.refresh(uom)

        return uom


class CreateTypeRepository:

    def __init__(self, db_session: AsyncSession, data: CreateTypeSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_type(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        type_obj = TypeModel(
            name=self.data.name,
            sub_name=self.data.sub_name,
            description=self.data.description,
            material=self.data.material,
            size_1=self.data.size_1,
            size_2=self.data.size_2,
            thickness_1=self.data.thickness_1,
            thickness_2=self.data.thickness_2
        )

        self.db_session.add(type_obj)
        await self.db_session.commit()
        await self.db_session.refresh(type_obj)

        return type_obj


class CreateStockRepository:

    def __init__(self, db_session: AsyncSession, data: CreateStockSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_stock(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        # Check if type exists
        type_obj = await self.db_session.execute(
            select(TypeModel).where(TypeModel.id == self.data.type_id)
        )
        if not type_obj.scalar_one_or_none():
            raise HTTPException(404, "Type not found")

        # Check if UOM exists
        uom_obj = await self.db_session.execute(
            select(UomModel).where(UomModel.id == self.data.uom_id)
        )
        if not uom_obj.scalar_one_or_none():
            raise HTTPException(404, "UOM not found")

        # Check if stock code already exists
        existing = await self.db_session.execute(
            select(StockDataModel).where(StockDataModel.stock_code == self.data.stock_code)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(409, "Stock code already exists")

        stock = StockDataModel(
            stock_code=self.data.stock_code,
            alternative_id=self.data.alternative_id,
            old_code=self.data.old_code,
            comment=self.data.comment,
            type_id=self.data.type_id,
            uom_id=self.data.uom_id
        )

        self.db_session.add(stock)
        await self.db_session.commit()
        await self.db_session.refresh(stock)

        return stock