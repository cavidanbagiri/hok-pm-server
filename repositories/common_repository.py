from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.user_model import UserModel, StatusModel
from models.common_model import AreaModel, LocationModel, UomModel, TypeModel, StockDataModel, SubTypeModel, Size1Model, \
    DescriptionModel, MaterialModel, Size2Model

from schemas.common_schema import CreateStockSchema, CreateTypeSchema, CreateUomSchema, CreateLocationSchema, \
    CreateAreaSchema, CreateDescriptionSchema, CreateSize2Schema, CreateSize1Schema, CreateMaterialSchema, \
    CreateSubTypeSchema


class CheckAdminManagerAuthorize:

    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id

    async def check_admin_or_manager(self):
        query = select(UserModel).where(UserModel.id == self.user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

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



class FetchAreaRepository:

    def __init__(self, db_session: AsyncSession, area_id: int = None, project_id: int = None):
        self.db_session = db_session
        self.area_id = area_id
        self.project_id = project_id

    async def fetch_area(self):
        query = select(AreaModel)

        if self.area_id:
            query = query.where(AreaModel.id == self.area_id)

        if self.project_id:
            query = query.where(AreaModel.project_id == self.project_id)

        result = await self.db_session.execute(query)
        areas = result.scalars().all()

        if not areas:
            raise HTTPException(404, "Area not found")

        return areas


class FetchLocationRepository:

    def __init__(self, db_session: AsyncSession, location_id: int = None, project_id: int = None):
        self.db_session = db_session
        self.location_id = location_id
        self.project_id = project_id

    async def fetch_location(self):
        query = select(LocationModel)

        if self.location_id:
            query = query.where(LocationModel.id == self.location_id)

        if self.project_id:
            query = query.where(LocationModel.project_id == self.project_id)

        result = await self.db_session.execute(query)
        locations = result.scalars().all()

        if not locations:
            raise HTTPException(404, "Location not found")

        return locations


class FetchUomRepository:

    def __init__(self, db_session: AsyncSession, uom_id: int = None):
        self.db_session = db_session
        self.uom_id = uom_id

    async def fetch_uom(self):
        query = select(UomModel)

        if self.uom_id:
            query = query.where(UomModel.id == self.uom_id)

        result = await self.db_session.execute(query)
        uoms = result.scalars().all()

        if not uoms:
            raise HTTPException(404, "UOM not found")

        return uoms


# class FetchTypeRepository:
#
#     def __init__(self, db_session: AsyncSession, type_id: int = None):
#         self.db_session = db_session
#         self.type_id = type_id
#
#     async def fetch_type(self):
#         query = select(TypeModel)
#
#         if self.type_id:
#             query = query.where(TypeModel.id == self.type_id)
#
#         result = await self.db_session.execute(query)
#         types = result.scalars().all()
#
#         if not types:
#             raise HTTPException(404, "Type not found")
#
#         return types


class FetchStockRepository:

    def __init__(self, db_session: AsyncSession, stock_id: int = None, stock_code: str = None):
        self.db_session = db_session
        self.stock_id = stock_id
        self.stock_code = stock_code

    async def fetch_stock(self):
        query = select(StockDataModel)

        if self.stock_id:
            query = query.where(StockDataModel.id == self.stock_id)

        if self.stock_code:
            query = query.where(StockDataModel.stock_code == self.stock_code)

        result = await self.db_session.execute(query)
        stocks = result.scalars().all()

        if not stocks:
            raise HTTPException(404, "Stock data not found")

        return stocks



class FetchSubTypeRepository:

    def __init__(self, db_session: AsyncSession, subtype_id: int = None):
        self.db_session = db_session
        self.subtype_id = subtype_id

    async def fetch_subtype(self):
        query = select(SubTypeModel)

        if self.subtype_id:
            query = query.where(SubTypeModel.id == self.subtype_id)

        result = await self.db_session.execute(query)
        subtypes = result.scalars().all()

        if not subtypes:
            raise HTTPException(404, "SubType not found")

        return subtypes


class FetchSize1Repository:

    def __init__(self, db_session: AsyncSession, size1_id: int = None):
        self.db_session = db_session
        self.size1_id = size1_id

    async def fetch_size1(self):
        query = select(Size1Model)

        if self.size1_id:
            query = query.where(Size1Model.id == self.size1_id)

        result = await self.db_session.execute(query)
        sizes1 = result.scalars().all()

        if not sizes1:
            raise HTTPException(404, "Size1 not found")

        return sizes1


class FetchSize2Repository:

    def __init__(self, db_session: AsyncSession, size2_id: int = None):
        self.db_session = db_session
        self.size2_id = size2_id

    async def fetch_size2(self):
        query = select(Size2Model)

        if self.size2_id:
            query = query.where(Size2Model.id == self.size2_id)

        result = await self.db_session.execute(query)
        sizes2 = result.scalars().all()

        if not sizes2:
            raise HTTPException(404, "Size2 not found")

        return sizes2


class FetchMaterialRepository:

    def __init__(self, db_session: AsyncSession, material_id: int = None):
        self.db_session = db_session
        self.material_id = material_id

    async def fetch_material(self):
        query = select(MaterialModel)

        if self.material_id:
            query = query.where(MaterialModel.id == self.material_id)

        result = await self.db_session.execute(query)
        materials = result.scalars().all()

        if not materials:
            raise HTTPException(404, "Material not found")

        return materials


class FetchDescriptionRepository:

    def __init__(self, db_session: AsyncSession, description_id: int = None):
        self.db_session = db_session
        self.description_id = description_id

    async def fetch_description(self):
        query = select(DescriptionModel)

        if self.description_id:
            query = query.where(DescriptionModel.id == self.description_id)

        result = await self.db_session.execute(query)
        descriptions = result.scalars().all()

        if not descriptions:
            raise HTTPException(404, "Description not found")

        return descriptions


class FetchTypeRepository:

    def __init__(self, db_session: AsyncSession, type_id: int = None):
        self.db_session = db_session
        self.type_id = type_id

    async def fetch_type(self):
        query = select(TypeModel).options(
            selectinload(TypeModel.subtype),
            selectinload(TypeModel.size1),
            selectinload(TypeModel.size2),
            selectinload(TypeModel.material),
            selectinload(TypeModel.description)
        )

        if self.type_id:
            query = query.where(TypeModel.id == self.type_id)

        result = await self.db_session.execute(query)
        types = result.scalars().all()

        if not types:
            raise HTTPException(404, "Type not found")

        return types











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


class CreateSubTypeRepository:

    def __init__(self, db_session: AsyncSession, data: CreateSubTypeSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_subtype(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        existing = await self.db_session.execute(
            select(SubTypeModel).where(SubTypeModel.name == self.data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(409, "SubType already exists")

        subtype = SubTypeModel(name=self.data.name)
        self.db_session.add(subtype)
        await self.db_session.commit()
        await self.db_session.refresh(subtype)
        return subtype


class CreateSize1Repository:

    def __init__(self, db_session: AsyncSession, data: CreateSize1Schema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_size1(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        existing = await self.db_session.execute(
            select(Size1Model).where(Size1Model.name == self.data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(409, "Size1 already exists")

        size1 = Size1Model(name=self.data.name)
        self.db_session.add(size1)
        await self.db_session.commit()
        await self.db_session.refresh(size1)
        return size1


class CreateSize2Repository:

    def __init__(self, db_session: AsyncSession, data: CreateSize2Schema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_size2(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        existing = await self.db_session.execute(
            select(Size2Model).where(Size2Model.name == self.data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(409, "Size2 already exists")

        size2 = Size2Model(name=self.data.name)
        self.db_session.add(size2)
        await self.db_session.commit()
        await self.db_session.refresh(size2)
        return size2


class CreateMaterialRepository:

    def __init__(self, db_session: AsyncSession, data: CreateMaterialSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_material(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        existing = await self.db_session.execute(
            select(MaterialModel).where(MaterialModel.name == self.data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(409, "Material already exists")

        material = MaterialModel(name=self.data.name)
        self.db_session.add(material)
        await self.db_session.commit()
        await self.db_session.refresh(material)
        return material


class CreateDescriptionRepository:

    def __init__(self, db_session: AsyncSession, data: CreateDescriptionSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_description(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        existing = await self.db_session.execute(
            select(DescriptionModel).where(DescriptionModel.name == self.data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(409, "Description already exists")

        description = DescriptionModel(name=self.data.name)
        self.db_session.add(description)
        await self.db_session.commit()
        await self.db_session.refresh(description)
        return description


class CreateTypeRepository:

    def __init__(self, db_session: AsyncSession, data: CreateTypeSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_type(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        # Verify all foreign keys exist
        for model, id_field in [
            (SubTypeModel, self.data.subtype_id),
            (Size1Model, self.data.size1_id),
            (MaterialModel, self.data.material_id),
            (DescriptionModel, self.data.description_id)
        ]:
            result = await self.db_session.execute(select(model).where(model.id == id_field))
            if not result.scalar_one_or_none():
                raise HTTPException(404, f"{model.__name__} not found")

        if self.data.size2_id:
            result = await self.db_session.execute(select(Size2Model).where(Size2Model.id == self.data.size2_id))
            if not result.scalar_one_or_none():
                raise HTTPException(404, "Size2 not found")

        type_obj = TypeModel(
            subtype_id=self.data.subtype_id,
            size1_id=self.data.size1_id,
            size2_id=self.data.size2_id,
            material_id=self.data.material_id,
            description_id=self.data.description_id,
            thickness_1=self.data.thickness_1,
            thickness_2=self.data.thickness_2
        )

        self.db_session.add(type_obj)
        await self.db_session.commit()
        await self.db_session.refresh(type_obj)
        return type_obj

