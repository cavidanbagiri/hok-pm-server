from typing import Optional, List, Dict, Any

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from models.user_model import UserModel, StatusModel, ProjectModel
from models.common_model import AreaModel, LocationModel, UomModel, TypeModel, StockDataModel, SubTypeModel, Size1Model, \
    DescriptionModel, MaterialModel, Size2Model, TypesModel

from schemas.common_schema import CreateStockSchema, CreateTypeSchema, CreateUomSchema, CreateLocationSchema, \
    CreateAreaSchema, CreateDescriptionSchema, CreateSize2Schema, CreateSize1Schema, CreateMaterialSchema, \
    CreateSubTypeSchema, CreateTypesSchema, BulkCreateSubTypeSchema, BulkCreateSize1Schema, BulkCreateSize2Schema, \
    BulkCreateMaterialSchema, BulkCreateDescriptionSchema


class CheckAdminManagerAuthorize:

    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id

    async def check_admin_or_manager(self):

        query = (
            select(UserModel)
            .options(selectinload(UserModel.status))
            .where(UserModel.id == self.user_id)
        )

        result = await self.db.execute(query)

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        if user.status.status.upper() not in ["ADMIN", "MANAGER"]:
            raise HTTPException(
                status_code=403,
                detail="Authorization Error"
            )

        return user


class GetUserInformation:
    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id

    async def get_user_information(self):
        try:
            query = (
                select(UserModel)
                .options(selectinload(UserModel.status))
                .where(UserModel.id == self.user_id)
            )

            result = await self.db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            return {
                'user_id': user.id,
                'project_id': user.project_id,
                'status_id': user.status_id,
                'status': user.status.status if user.status else None,
                'email': user.email,
                'firstname': user.firstname,
                'lastname': user.lastname
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching user information: {str(e)}"
            )


########################################################################### Area Classes tested
class FetchAreaRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def fetch_area(
            self,
            user_id: int,
            project_id: int = None,
            name: str = None,
            description: str = None,
            doc_no: str = None,
            doc_rev: str = None,
            say_iso_no: str = None
    ):

        user_info = await GetUserInformation(
            self.db_session,
            user_id
        ).get_user_information()

        query = (
            select(AreaModel)
            .options(selectinload(AreaModel.project))
        )

        # Admin or manager check
        is_admin_or_manager = user_info['status_id'] in [1, 2]

        # Regular user restriction
        if not is_admin_or_manager:
            query = query.where(
                AreaModel.project_id == user_info['project_id']
            )

        # Admin/Manager project filter
        elif project_id:
            query = query.where(
                AreaModel.project_id == project_id
            )

        # Additional filters
        if name:
            query = query.where(
                AreaModel.name.ilike(f"%{name}%")
            )

        if description:
            query = query.where(
                AreaModel.description.ilike(f"%{description}%")
            )

        if doc_no:
            query = query.where(
                AreaModel.doc_no.ilike(f"%{doc_no}%")
            )

        if doc_rev:
            query = query.where(
                AreaModel.doc_rev.ilike(f"%{doc_rev}%")
            )

        if say_iso_no:
            query = query.where(
                AreaModel.say_iso_no.ilike(f"%{say_iso_no}%")
            )

        result = await self.db_session.execute(query)

        areas = result.scalars().all()

        return areas


class CreateAreaRepository:

    def __init__(
        self,
        db_session: AsyncSession,
        data: CreateAreaSchema,
        user_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_area(self):

        # Authorization
        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Normalize data
        name = self.data.name.strip().upper()
        description = self.data.description.strip().upper()
        doc_no = self.data.doc_no.strip().upper()
        doc_rev = self.data.doc_rev.strip().upper()
        say_iso_no = self.data.say_iso_no.strip().upper()

        # Check duplicate name inside same project
        existing_area = await self.db_session.scalar(
            select(AreaModel).where(
                AreaModel.name == name,
                AreaModel.project_id == self.data.project_id
            )
        )

        if existing_area:
            raise HTTPException(
                status_code=400,
                detail="Area already exists in this project"
            )

        try:

            area = AreaModel(
                name=name,
                description=description,
                doc_no=doc_no,
                doc_rev=doc_rev,
                say_iso_no=say_iso_no,
                project_id=self.data.project_id
            )

            self.db_session.add(area)

            await self.db_session.commit()
            await self.db_session.refresh(area)

            return area

        except Exception:
            await self.db_session.rollback()
            raise



########################################################################### Location Classes tested
class FetchLocationRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def fetch_location(
            self,
            user_id: int,
            project_id: int = None,
            name: str = None
    ):

        # MUST await here
        user_info = await GetUserInformation(
            self.db_session,
            user_id
        ).get_user_information()

        query = (
            select(LocationModel)
            .options(selectinload(LocationModel.project))
        )

        # Check role
        is_admin_or_manager = user_info['status_id'] in [1, 2]

        # Regular user
        if not is_admin_or_manager:

            query = query.where(
                LocationModel.project_id == user_info['project_id']
            )

        # Admin/Manager filters
        else:

            if project_id:
                query = query.where(
                    LocationModel.project_id == project_id
                )

        # Name filter
        if name:
            query = query.where(
                LocationModel.name.ilike(f"%{name}%")
            )

        result = await self.db_session.execute(query)

        locations = result.scalars().all()

        if not locations:
            raise HTTPException(404, "Location not found")

        return locations

class CreateLocationRepository:

    def __init__(
        self,
        db_session: AsyncSession,
        data: CreateLocationSchema,
        user_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_location(self):

        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Normalize
        location_name = self.data.name.strip().upper()

        # Check duplicate inside same project
        existing_location = await self.db_session.scalar(
            select(LocationModel).where(
                LocationModel.name == location_name,
                LocationModel.project_id == self.data.project_id
            )
        )

        if existing_location:
            raise HTTPException(
                status_code=400,
                detail="Location already exists in this project"
            )

        try:

            location = LocationModel(
                name=location_name,
                project_id=self.data.project_id
            )

            self.db_session.add(location)

            await self.db_session.commit()
            await self.db_session.refresh(location)

            return location

        except Exception:
            await self.db_session.rollback()
            raise


########################################################################### Uom Classes tested
class FetchUomRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def fetch_uom(
            self,
            uom_id: int = None,
            name: str = None
    ):

        query = select(UomModel)

        # Filter by ID
        if uom_id:
            query = query.where(
                UomModel.id == uom_id
            )

        # Filter by name
        if name:
            query = query.where(
                UomModel.name.ilike(f"%{name}%")
            )

        result = await self.db_session.execute(query)

        uoms = result.scalars().all()

        if not uoms:
            raise HTTPException(404, "UOM not found")

        return uoms

class CreateUomRepository:

    def __init__(
        self,
        db_session: AsyncSession,
        data: CreateUomSchema,
        user_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_uom(self):

        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Normalize
        uom_name = self.data.name.strip().upper()

        # Check duplicate
        existing = await self.db_session.scalar(
            select(UomModel).where(
                UomModel.name == uom_name
            )
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="UOM already exists"
            )

        try:

            uom = UomModel(
                name=uom_name
            )

            self.db_session.add(uom)

            await self.db_session.commit()
            await self.db_session.refresh(uom)

            return uom

        except Exception:
            await self.db_session.rollback()
            raise



########################################################################### Size1 Classes tested
class FetchSize1Repository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def fetch_size1(
            self,
            size1_id: int = None,
            name: str = None
    ) -> List[Size1Model]:

        query = (
            select(Size1Model)
            .order_by(Size1Model.id)
        )

        # Filter by ID
        if size1_id:
            query = query.where(
                Size1Model.id == size1_id
            )

        # Filter by name
        if name:
            query = query.where(
                Size1Model.name.ilike(f"%{name}%")
            )

        result = await self.db_session.execute(query)

        sizes1 = result.scalars().all()

        if not sizes1:
            raise HTTPException(404, "Size1 not found")

        return sizes1

class CreateSize1Repository:

    def __init__(self, db_session: AsyncSession, data: CreateSize1Schema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_size1(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        # Normalize to uppercase
        size1_name = self.data.name.strip().upper()

        # Check for duplicates using normalized name
        existing_size1 = await self.db_session.scalar(
            select(Size1Model).where(
                Size1Model.name == size1_name
            )
        )

        if existing_size1:
            raise HTTPException(
                status_code=409,
                detail="Size already exists in this project"
            )

        try:
            # Save the normalized uppercase version
            size1 = Size1Model(name=size1_name)  # ← Use uppercase here
            self.db_session.add(size1)
            await self.db_session.commit()
            await self.db_session.refresh(size1)
            return size1
        except Exception:
            await self.db_session.rollback()
            raise

class BulkCreateSize1Repository:

    def __init__(self, db_session: AsyncSession, data: BulkCreateSize1Schema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def bulk_create_size1(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        created_items = []
        failed_items = []

        for item in self.data.items:
            try:
                # Convert to uppercase
                name_upper = item.name.upper()

                # Check if exists
                existing = await self.db_session.execute(
                    select(Size1Model).where(Size1Model.name == name_upper)
                )
                if existing.scalar_one_or_none():
                    failed_items.append({"name": item.name, "error": "Already exists"})
                    continue

                size1 = Size1Model(name=name_upper)
                self.db_session.add(size1)
                created_items.append({"id": None, "name": item.name})

            except Exception as e:
                failed_items.append({"name": item.name, "error": str(e)})

        # Commit all at once
        if created_items:
            await self.db_session.commit()
            # Refresh to get IDs
            for item in created_items:
                result = await self.db_session.execute(
                    select(Size1Model).where(Size1Model.name == item["name"].upper())
                )
                size1 = result.scalar_one_or_none()
                item["id"] = size1.id

        return {
            "success": created_items,
            "failed": failed_items,
            "total_created": len(created_items),
            "total_failed": len(failed_items)
        }



########################################################################### Size2 Classes tested
class FetchSize2Repository:

    def __init__(self, db_session: AsyncSession, size2_id: int = None):
        self.db_session = db_session
        self.size2_id = size2_id

    async def fetch_size2(
            self,
            size2_id: int = None,
            name: str = None
    ) -> List[Size1Model]:

        query = (
            select(Size2Model)
            .order_by(Size2Model.id)
        )

        # Filter by ID
        if size2_id:
            query = query.where(
                Size2Model.id == size2_id
            )

        # Filter by name
        if name:
            query = query.where(
                Size2Model.name.ilike(f"%{name}%")
            )

        result = await self.db_session.execute(query)

        sizes2 = result.scalars().all()

        if not sizes2:
            raise HTTPException(404, "Size1 not found")

        return sizes2

class CreateSize2Repository:

    def __init__(self, db_session: AsyncSession, data: CreateSize2Schema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_size2(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        # Normalize to uppercase
        size2_name = self.data.name.strip().upper()

        # Check for duplicates using uppercase
        existing = await self.db_session.execute(
            select(Size2Model).where(Size2Model.name == size2_name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(409, "Size2 already exists")

        try:
            # Save the uppercase version
            size2 = Size2Model(name=size2_name)  # ← Uppercase here
            self.db_session.add(size2)
            await self.db_session.commit()
            await self.db_session.refresh(size2)
            return size2
        except Exception:
            await self.db_session.rollback()
            raise

class BulkCreateSize2Repository:

    def __init__(self, db_session: AsyncSession, data: BulkCreateSize2Schema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def bulk_create_size2(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        created_items = []
        failed_items = []

        for item in self.data.items:
            try:
                # Convert to uppercase
                name_upper = item.name.upper()

                # Check if exists
                existing = await self.db_session.execute(
                    select(Size2Model).where(Size2Model.name == name_upper)
                )
                if existing.scalar_one_or_none():
                    failed_items.append({"name": item.name, "error": "Already exists"})
                    continue

                size2 = Size2Model(name=name_upper)
                self.db_session.add(size2)
                created_items.append({"id": None, "name": item.name})

            except Exception as e:
                failed_items.append({"name": item.name, "error": str(e)})

        # Commit all at once
        if created_items:
            await self.db_session.commit()
            # Refresh to get IDs
            for item in created_items:
                result = await self.db_session.execute(
                    select(Size2Model).where(Size2Model.name == item["name"].upper())
                )
                size2 = result.scalar_one_or_none()
                item["id"] = size2.id

        return {
            "success": created_items,
            "failed": failed_items,
            "total_created": len(created_items),
            "total_failed": len(failed_items)
        }



########################################################################### Material Classes tested
class FetchMaterialRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def fetch_material(
            self,
            material_id: int = None,
            name: str = None
    ):

        query = (
            select(MaterialModel)
            .order_by(MaterialModel.id)
        )

        # Filter by ID
        if material_id:
            query = query.where(
                MaterialModel.id == material_id
            )

        # Filter by name
        if name:
            query = query.where(
                MaterialModel.name.ilike(f"%{name}%")
            )

        result = await self.db_session.execute(query)

        materials = result.scalars().all()

        if not materials:
            raise HTTPException(404, "Material not found")

        return materials

class CreateMaterialRepository:

    def __init__(self, db_session: AsyncSession, data: CreateMaterialSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_material(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        # Normalize to uppercase
        material_name = self.data.name.strip().upper()

        # Check for duplicates using uppercase
        existing = await self.db_session.execute(
            select(MaterialModel).where(MaterialModel.name == material_name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(409, "Material already exists")

        try:
            # Save the uppercase version
            material = MaterialModel(name=material_name)  # ← Uppercase here
            self.db_session.add(material)
            await self.db_session.commit()
            await self.db_session.refresh(material)
            return material
        except Exception:
            await self.db_session.rollback()
            raise

class BulkCreateMaterialRepository:

    def __init__(self, db_session: AsyncSession, data: BulkCreateMaterialSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def bulk_create_material(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        created_items = []
        failed_items = []

        for item in self.data.items:
            try:
                # Convert to uppercase
                name_upper = item.name.upper()

                # Check if exists
                existing = await self.db_session.execute(
                    select(MaterialModel).where(MaterialModel.name == name_upper)
                )
                if existing.scalar_one_or_none():
                    failed_items.append({"name": item.name, "error": "Already exists"})
                    continue

                material = MaterialModel(name=name_upper)
                self.db_session.add(material)
                created_items.append({"id": None, "name": item.name})

            except Exception as e:
                failed_items.append({"name": item.name, "error": str(e)})

        # Commit all at once
        if created_items:
            await self.db_session.commit()
            # Refresh to get IDs
            for item in created_items:
                result = await self.db_session.execute(
                    select(MaterialModel).where(MaterialModel.name == item["name"].upper())
                )
                material = result.scalar_one_or_none()
                item["id"] = material.id

        return {
            "success": created_items,
            "failed": failed_items,
            "total_created": len(created_items),
            "total_failed": len(failed_items)
        }




########################################################################### Description Classes tested
class FetchDescriptionRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def fetch_description(
            self,
            description_id: int = None,
            name: str = None
    ):

        query = (
            select(DescriptionModel)
            .order_by(DescriptionModel.id)
        )

        # Filter by ID
        if description_id:
            query = query.where(
                DescriptionModel.id == description_id
            )

        # Filter by name
        if name:
            query = query.where(
                DescriptionModel.name.ilike(f"%{name}%")
            )

        result = await self.db_session.execute(query)

        descriptions = result.scalars().all()

        if not descriptions:
            raise HTTPException(404, "Description not found")

        return descriptions

class CreateDescriptionRepository:

    def __init__(self, db_session: AsyncSession, data: CreateDescriptionSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_description(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        # Normalize to uppercase
        description_name = self.data.name.strip().upper()

        # Check for duplicates using uppercase
        existing = await self.db_session.execute(
            select(DescriptionModel).where(DescriptionModel.name == description_name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(409, "Description already exists")

        try:
            # Save the uppercase version
            description = DescriptionModel(name=description_name)  # ← Uppercase here
            self.db_session.add(description)
            await self.db_session.commit()
            await self.db_session.refresh(description)
            return description
        except Exception:
            await self.db_session.rollback()
            raise

class BulkCreateDescriptionRepository:

    def __init__(self, db_session: AsyncSession, data: BulkCreateDescriptionSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def bulk_create_descriptions(self) -> Dict[str, Any]:
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        # Extract all names (already uppercase from schema validation)
        new_names = [item.name for item in self.data.descriptions]

        # Check for duplicates in database
        existing = await self.db_session.execute(
            select(DescriptionModel.name).where(
                DescriptionModel.name.in_(new_names)
            )
        )
        existing_names = set(existing.scalars().all())

        # Filter out names that already exist
        unique_names = [name for name in new_names if name not in existing_names]

        if not unique_names:
            raise HTTPException(
                status_code=409,
                detail="All descriptions already exist"
            )

        # Check for duplicates within the request itself
        if len(new_names) != len(set(new_names)):
            duplicates = [name for name in new_names if new_names.count(name) > 1]
            raise HTTPException(
                status_code=400,
                detail=f"Duplicate names in request: {list(set(duplicates))}"
            )

        try:
            # Create all new description objects
            new_descriptions = [
                DescriptionModel(name=name)
                for name in unique_names
            ]

            # Bulk insert
            self.db_session.add_all(new_descriptions)
            await self.db_session.commit()

            # Refresh all (optional - for getting IDs)
            for description in new_descriptions:
                await self.db_session.refresh(description)

            return {
                "message": f"Successfully created {len(new_descriptions)} descriptions",
                "created": [
                    {"id": desc.id, "name": desc.name}
                    for desc in new_descriptions
                ],
                "skipped": [
                    {"name": name, "reason": "Already exists"}
                    for name in existing_names
                ] if existing_names else []
            }

        except IntegrityError:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Database integrity error - some descriptions may already exist"
            )
        except Exception:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Internal server error while creating descriptions"
            )



########################################################################### Description Classes tested
class FetchSubTypeRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def fetch_subtype(
            self,
            subtype_id: int = None,
            name: str = None
    ):

        query = (
            select(SubTypeModel)
            .order_by(SubTypeModel.id)
        )

        # Filter by ID
        if subtype_id:
            query = query.where(
                SubTypeModel.id == subtype_id
            )

        # Filter by name
        if name:
            query = query.where(
                SubTypeModel.name.ilike(f"%{name}%")
            )

        result = await self.db_session.execute(query)

        subtypes = result.scalars().all()

        if not subtypes:
            raise HTTPException(404, "SubType not found")

        return subtypes

class CreateSubTypeRepository:

    def __init__(self, db_session: AsyncSession, data: CreateSubTypeSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_subtype(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        # Normalize to uppercase
        subtype_name = self.data.name.strip().upper()

        # Check for duplicates using uppercase
        existing = await self.db_session.execute(
            select(SubTypeModel).where(SubTypeModel.name == subtype_name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(409, "SubType already exists")

        try:
            # Save the uppercase version
            subtype = SubTypeModel(name=subtype_name)  # ← Uppercase here
            self.db_session.add(subtype)
            await self.db_session.commit()
            await self.db_session.refresh(subtype)
            return subtype
        except Exception:
            await self.db_session.rollback()
            raise

class BulkCreateSubTypeRepository:

    def __init__(self, db_session: AsyncSession, data: BulkCreateSubTypeSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def bulk_create_subtype(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        created_items = []
        failed_items = []

        for item in self.data.items:
            try:
                # Convert to uppercase
                name_upper = item.name.upper()

                # Check if exists
                existing = await self.db_session.execute(
                    select(SubTypeModel).where(SubTypeModel.name == name_upper)
                )
                if existing.scalar_one_or_none():
                    failed_items.append({"name": item.name, "error": "Already exists"})
                    continue

                subtype = SubTypeModel(name=name_upper)
                self.db_session.add(subtype)
                created_items.append({"id": None, "name": item.name})

            except Exception as e:
                failed_items.append({"name": item.name, "error": str(e)})

        # Commit all at once
        if created_items:
            await self.db_session.commit()
            # Refresh to get IDs
            for item in created_items:
                result = await self.db_session.execute(
                    select(SubTypeModel).where(SubTypeModel.name == item["name"].upper())
                )
                subtype = result.scalar_one_or_none()
                item["id"] = subtype.id

        return {
            "success": created_items,
            "failed": failed_items,
            "total_created": len(created_items),
            "total_failed": len(failed_items)
        }



########################################################################### Types Classes # Can be: [valve, reducer, pee, tie, elbow, ...]
class FetchItemTypesRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def fetch_types(
            self,
            types_id: int = None,
            name: str = None
    ):

        query = (
            select(TypesModel)
            .order_by(TypesModel.id)
        )

        # Filter by ID
        if types_id:
            query = query.where(
                TypesModel.id == types_id
            )

        # Filter by name
        if name:
            query = query.where(
                TypesModel.name.ilike(f"%{name}%")
            )

        result = await self.db_session.execute(query)

        types = result.scalars().all()

        if not types:
            raise HTTPException(404, "Types not found")

        return types

class CreateItemTypesRepository:
    def __init__(self, db_session: AsyncSession, data: CreateTypesSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_types(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        # Normalize to uppercase (consistent with other repositories)
        types_name = self.data.name.strip().upper()

        # Check for duplicates using uppercase (simpler than func.upper)
        existing = await self.db_session.execute(
            select(TypesModel).where(TypesModel.name == types_name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(409, "Types already exists")

        try:
            # Save the uppercase version
            types = TypesModel(name=types_name)  # ← Uppercase here
            self.db_session.add(types)
            await self.db_session.commit()
            await self.db_session.refresh(types)
            return types
        except Exception:
            await self.db_session.rollback()
            raise




########################################################################### Type Classes
class FetchTypeRepository:

    def __init__(self, db_session: AsyncSession, type_id: int = None, types_id: int = None):
        self.db_session = db_session
        self.type_id = type_id
        self.types_id = types_id

    async def fetch_type(self):
        query = select(TypeModel).options(
            selectinload(TypeModel.type),
            selectinload(TypeModel.subtype),
            selectinload(TypeModel.size1),
            selectinload(TypeModel.size2),
            selectinload(TypeModel.material),
            selectinload(TypeModel.description)
        ).order_by(TypeModel.id)  # Add order_by for consistency

        if self.type_id:
            query = query.where(TypeModel.id == self.type_id)

        if self.types_id:
            query = query.where(TypeModel.type_id == self.types_id)

        result = await self.db_session.execute(query)
        types = result.scalars().all()

        if not types:
            raise HTTPException(404, "Type not found")

        return types

class CreateTypeRepository:

    def __init__(self, db_session: AsyncSession, data: CreateTypeSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_type(self):
        await CheckAdminManagerAuthorize(self.db_session, self.user_id).check_admin_or_manager()

        # Verify all foreign keys exist with better error messages
        foreign_keys = [
            (TypesModel, self.data.type_id, "Type"),
            (SubTypeModel, self.data.subtype_id, "SubType"),
            (Size1Model, self.data.size1_id, "Size1"),
            (MaterialModel, self.data.material_id, "Material"),
            (DescriptionModel, self.data.description_id, "Description")
        ]

        for model, id_value, name in foreign_keys:
            if id_value:  # Only check if ID is provided
                result = await self.db_session.execute(
                    select(model).where(model.id == id_value)
                )
                if not result.scalar_one_or_none():
                    raise HTTPException(404, f"{name} with id {id_value} not found")

        # Check optional Size2
        if self.data.size2_id:
            result = await self.db_session.execute(
                select(Size2Model).where(Size2Model.id == self.data.size2_id)
            )
            if not result.scalar_one_or_none():
                raise HTTPException(404, f"Size2 with id {self.data.size2_id} not found")

        # Check for duplicate combination (optional but recommended)
        existing = await self.db_session.execute(
            select(TypeModel).where(
                and_(
                    TypeModel.type_id == self.data.type_id,
                    TypeModel.subtype_id == self.data.subtype_id,
                    TypeModel.size1_id == self.data.size1_id,
                    TypeModel.size2_id == self.data.size2_id,
                    TypeModel.material_id == self.data.material_id,
                    TypeModel.description_id == self.data.description_id,
                    TypeModel.thickness_1 == self.data.thickness_1,
                    TypeModel.thickness_2 == self.data.thickness_2
                )
            )
        )

        if existing.scalar_one_or_none():
            raise HTTPException(409, "This Type combination already exists")

        try:
            type_obj = TypeModel(
                type_id=self.data.type_id,
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

            # Refresh relationships
            await self.db_session.refresh(type_obj, attribute_names=[
                'type', 'subtype', 'size1', 'size2', 'material', 'description'
            ])

            return type_obj

        except IntegrityError:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Database integrity error - possible duplicate or invalid foreign key"
            )
        except Exception:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Internal server error while creating type"
            )



########################################################################### Stock Classes
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

class CreateStockRepository:

    def __init__(self, db_session: AsyncSession, data: CreateStockSchema, user_id: int):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id

    async def create_stock(self):
        # Add await here
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




########################################################################### Project Classes
class FetchProjectRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def fetch_project(self, user_id: int):

        # Get user info
        user_info = await GetUserInformation(
            self.db_session,
            user_id
        ).get_user_information()

        # Base query
        query = select(ProjectModel)

        # Admin or Manager
        is_admin_or_manager = user_info['status_id'] in [1, 2]

        # Regular users only see their own project
        if not is_admin_or_manager:
            query = query.where(
                ProjectModel.id == user_info['project_id']
            )

        # Execute query
        result = await self.db_session.execute(query)
        projects = result.scalars().all()

        if not projects:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )

        # Return serialized data
        return [
            {
                "id": project.id,
                "name": project.name,
                "country": project.country,
                "code": project.code
            }
            for project in projects
        ]