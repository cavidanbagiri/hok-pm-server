from typing import Optional, List, Dict, Any

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update, distinct
from sqlalchemy.orm import selectinload

from models.user_model import UserModel, StatusModel, ProjectModel
from models.common_model import AreaModel, LocationModel, UomModel, TypeModel, StockDataModel, SubTypeModel, Size1Model, \
    DescriptionModel, MaterialModel, Size2Model, TypesModel

from schemas.common_schema import *

########################################################################### User Classes tested
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

class UpdateAreaRepository:

    def __init__(
            self,
            db_session: AsyncSession,
            data: UpdateAreaSchema,
            user_id: int,
            area_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id
        self.area_id = area_id

    async def update_area(self):

        # Authorization
        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Check if area exists
        existing_area = await self.db_session.scalar(
            select(AreaModel).where(AreaModel.id == self.area_id)
        )

        if not existing_area:
            raise HTTPException(
                status_code=404,
                detail="Area not found"
            )

        # Prepare update data
        update_data = {}

        if self.data.name is not None:
            name = self.data.name.strip().upper()
            update_data['name'] = name

            # Check duplicate name if name is being changed
            if name != existing_area.name:
                duplicate_area = await self.db_session.scalar(
                    select(AreaModel).where(
                        AreaModel.name == name,
                        AreaModel.project_id == (
                            self.data.project_id if self.data.project_id is not None else existing_area.project_id),
                        AreaModel.id != self.area_id
                    )
                )
                if duplicate_area:
                    raise HTTPException(
                        status_code=400,
                        detail="Area already exists in this project"
                    )

        if self.data.description is not None:
            update_data['description'] = self.data.description.strip().upper()

        if self.data.doc_no is not None:
            update_data['doc_no'] = self.data.doc_no.strip().upper()

        if self.data.doc_rev is not None:
            update_data['doc_rev'] = self.data.doc_rev.strip().upper()

        if self.data.say_iso_no is not None:
            update_data['say_iso_no'] = self.data.say_iso_no.strip().upper()

        if self.data.project_id is not None:
            update_data['project_id'] = self.data.project_id

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        try:
            # Perform update
            await self.db_session.execute(
                update(AreaModel)
                .where(AreaModel.id == self.area_id)
                .values(**update_data)
            )

            await self.db_session.commit()

            # Fetch updated area
            updated_area = await self.db_session.scalar(
                select(AreaModel).where(AreaModel.id == self.area_id)
            )

            return updated_area

        except Exception:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error updating area"
            )



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

class UpdateLocationRepository:

    def __init__(
            self,
            db_session: AsyncSession,
            data: UpdateLocationSchema,
            user_id: int,
            location_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id
        self.location_id = location_id

    async def update_location(self):

        # Authorization
        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Check if location exists
        existing_location = await self.db_session.scalar(
            select(LocationModel).where(LocationModel.id == self.location_id)
        )

        if not existing_location:
            raise HTTPException(
                status_code=404,
                detail="Location not found"
            )

        # Prepare update data
        update_data = {}

        if self.data.name is not None:
            location_name = self.data.name.strip().upper()
            update_data['name'] = location_name

            # Check duplicate if name is being changed
            if location_name != existing_location.name:
                duplicate_location = await self.db_session.scalar(
                    select(LocationModel).where(
                        LocationModel.name == location_name,
                        LocationModel.project_id == (
                            self.data.project_id if self.data.project_id is not None else existing_location.project_id),
                        LocationModel.id != self.location_id
                    )
                )
                if duplicate_location:
                    raise HTTPException(
                        status_code=400,
                        detail="Location already exists in this project"
                    )

        if self.data.project_id is not None:
            update_data['project_id'] = self.data.project_id

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        try:
            # Perform update
            await self.db_session.execute(
                update(LocationModel)
                .where(LocationModel.id == self.location_id)
                .values(**update_data)
            )

            await self.db_session.commit()

            # Fetch updated location
            updated_location = await self.db_session.scalar(
                select(LocationModel).where(LocationModel.id == self.location_id)
            )

            return updated_location

        except Exception:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error updating location"
            )



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

class UpdateUomRepository:

    def __init__(
            self,
            db_session: AsyncSession,
            data: UpdateUomSchema,
            user_id: int,
            uom_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id
        self.uom_id = uom_id

    async def update_uom(self):

        # Authorization
        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Check if UOM exists
        existing_uom = await self.db_session.scalar(
            select(UomModel).where(UomModel.id == self.uom_id)
        )

        if not existing_uom:
            raise HTTPException(
                status_code=404,
                detail="UOM not found"
            )

        # Prepare update data
        update_data = {}

        if self.data.name is not None:
            uom_name = self.data.name.strip().upper()
            update_data['name'] = uom_name

            # Check duplicate if name is being changed
            if uom_name != existing_uom.name:
                duplicate_uom = await self.db_session.scalar(
                    select(UomModel).where(
                        UomModel.name == uom_name,
                        UomModel.id != self.uom_id
                    )
                )
                if duplicate_uom:
                    raise HTTPException(
                        status_code=409,
                        detail="UOM already exists"
                    )

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        try:
            # Perform update
            await self.db_session.execute(
                update(UomModel)
                .where(UomModel.id == self.uom_id)
                .values(**update_data)
            )

            await self.db_session.commit()

            # Fetch updated UOM
            updated_uom = await self.db_session.scalar(
                select(UomModel).where(UomModel.id == self.uom_id)
            )

            return updated_uom

        except Exception:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error updating UOM"
            )



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

class UpdateSize1Repository:

    def __init__(
            self,
            db_session: AsyncSession,
            data: UpdateSize1Schema,
            user_id: int,
            size1_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id
        self.size1_id = size1_id

    async def update_size1(self):

        # Authorization
        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Check if Size1 exists
        existing_size1 = await self.db_session.scalar(
            select(Size1Model).where(Size1Model.id == self.size1_id)
        )

        if not existing_size1:
            raise HTTPException(
                status_code=404,
                detail="Size1 not found"
            )

        # Prepare update data
        update_data = {}

        if self.data.name is not None:
            size1_name = self.data.name.strip().upper()
            update_data['name'] = size1_name

            # Check duplicate if name is being changed
            if size1_name != existing_size1.name:
                duplicate_size1 = await self.db_session.scalar(
                    select(Size1Model).where(
                        Size1Model.name == size1_name,
                        Size1Model.id != self.size1_id
                    )
                )
                if duplicate_size1:
                    raise HTTPException(
                        status_code=409,
                        detail="Size already exists"
                    )

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        try:
            # Perform update
            await self.db_session.execute(
                update(Size1Model)
                .where(Size1Model.id == self.size1_id)
                .values(**update_data)
            )

            await self.db_session.commit()

            # Fetch updated Size1
            updated_size1 = await self.db_session.scalar(
                select(Size1Model).where(Size1Model.id == self.size1_id)
            )

            return updated_size1

        except Exception:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error updating Size1"
            )

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

class UpdateSize2Repository:

    def __init__(
            self,
            db_session: AsyncSession,
            data: UpdateSize2Schema,
            user_id: int,
            size2_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id
        self.size2_id = size2_id

    async def update_size2(self):

        # Authorization
        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Check if Size2 exists
        existing_size2 = await self.db_session.scalar(
            select(Size2Model).where(Size2Model.id == self.size2_id)
        )

        if not existing_size2:
            raise HTTPException(
                status_code=404,
                detail="Size2 not found"
            )

        # Prepare update data
        update_data = {}

        if self.data.name is not None:
            size2_name = self.data.name.strip().upper()
            update_data['name'] = size2_name

            # Check duplicate if name is being changed
            if size2_name != existing_size2.name:
                duplicate_size2 = await self.db_session.scalar(
                    select(Size2Model).where(
                        Size2Model.name == size2_name,
                        Size2Model.id != self.size2_id
                    )
                )
                if duplicate_size2:
                    raise HTTPException(
                        status_code=409,
                        detail="Size2 already exists"
                    )

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        try:
            # Perform update
            await self.db_session.execute(
                update(Size2Model)
                .where(Size2Model.id == self.size2_id)
                .values(**update_data)
            )

            await self.db_session.commit()

            # Fetch updated Size2
            updated_size2 = await self.db_session.scalar(
                select(Size2Model).where(Size2Model.id == self.size2_id)
            )

            return updated_size2

        except Exception:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error updating Size2"
            )

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

class UpdateMaterialRepository:

    def __init__(
            self,
            db_session: AsyncSession,
            data: UpdateMaterialSchema,
            user_id: int,
            material_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id
        self.material_id = material_id

    async def update_material(self):

        # Authorization
        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Check if Material exists
        existing_material = await self.db_session.scalar(
            select(MaterialModel).where(MaterialModel.id == self.material_id)
        )

        if not existing_material:
            raise HTTPException(
                status_code=404,
                detail="Material not found"
            )

        # Prepare update data
        update_data = {}

        if self.data.name is not None:
            material_name = self.data.name.strip().upper()
            update_data['name'] = material_name

            # Check duplicate if name is being changed
            if material_name != existing_material.name:
                duplicate_material = await self.db_session.scalar(
                    select(MaterialModel).where(
                        MaterialModel.name == material_name,
                        MaterialModel.id != self.material_id
                    )
                )
                if duplicate_material:
                    raise HTTPException(
                        status_code=409,
                        detail="Material already exists"
                    )

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        try:
            # Perform update
            await self.db_session.execute(
                update(MaterialModel)
                .where(MaterialModel.id == self.material_id)
                .values(**update_data)
            )

            await self.db_session.commit()

            # Fetch updated Material
            updated_material = await self.db_session.scalar(
                select(MaterialModel).where(MaterialModel.id == self.material_id)
            )

            return updated_material

        except Exception:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error updating Material"
            )

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

class UpdateDescriptionRepository:

    def __init__(
            self,
            db_session: AsyncSession,
            data: UpdateDescriptionSchema,
            user_id: int,
            description_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id
        self.description_id = description_id

    async def update_description(self):

        # Authorization
        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Check if Description exists
        existing_description = await self.db_session.scalar(
            select(DescriptionModel).where(DescriptionModel.id == self.description_id)
        )

        if not existing_description:
            raise HTTPException(
                status_code=404,
                detail="Description not found"
            )

        # Prepare update data
        update_data = {}

        if self.data.name is not None:
            description_name = self.data.name.strip().upper()
            update_data['name'] = description_name

            # Check duplicate if name is being changed
            if description_name != existing_description.name:
                duplicate_description = await self.db_session.scalar(
                    select(DescriptionModel).where(
                        DescriptionModel.name == description_name,
                        DescriptionModel.id != self.description_id
                    )
                )
                if duplicate_description:
                    raise HTTPException(
                        status_code=409,
                        detail="Description already exists"
                    )

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        try:
            # Perform update
            await self.db_session.execute(
                update(DescriptionModel)
                .where(DescriptionModel.id == self.description_id)
                .values(**update_data)
            )

            await self.db_session.commit()

            # Fetch updated Description
            updated_description = await self.db_session.scalar(
                select(DescriptionModel).where(DescriptionModel.id == self.description_id)
            )

            return updated_description

        except Exception:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error updating Description"
            )

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

class UpdateSubTypeRepository:

    def __init__(
            self,
            db_session: AsyncSession,
            data: UpdateSubTypeSchema,
            user_id: int,
            subtype_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id
        self.subtype_id = subtype_id

    async def update_subtype(self):

        # Authorization
        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Check if SubType exists
        existing_subtype = await self.db_session.scalar(
            select(SubTypeModel).where(SubTypeModel.id == self.subtype_id)
        )

        if not existing_subtype:
            raise HTTPException(
                status_code=404,
                detail="SubType not found"
            )

        # Prepare update data
        update_data = {}

        if self.data.name is not None:
            subtype_name = self.data.name.strip().upper()
            update_data['name'] = subtype_name

            # Check duplicate if name is being changed
            if subtype_name != existing_subtype.name:
                duplicate_subtype = await self.db_session.scalar(
                    select(SubTypeModel).where(
                        SubTypeModel.name == subtype_name,
                        SubTypeModel.id != self.subtype_id
                    )
                )
                if duplicate_subtype:
                    raise HTTPException(
                        status_code=409,
                        detail="SubType already exists"
                    )

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        try:
            # Perform update
            await self.db_session.execute(
                update(SubTypeModel)
                .where(SubTypeModel.id == self.subtype_id)
                .values(**update_data)
            )

            await self.db_session.commit()

            # Fetch updated SubType
            updated_subtype = await self.db_session.scalar(
                select(SubTypeModel).where(SubTypeModel.id == self.subtype_id)
            )

            return updated_subtype

        except Exception:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error updating SubType"
            )

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

class UpdateItemTypesRepository:

    def __init__(
            self,
            db_session: AsyncSession,
            data: UpdateTypesSchema,
            user_id: int,
            types_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id
        self.types_id = types_id

    async def update_types(self):

        # Authorization
        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Check if Types exists
        existing_types = await self.db_session.scalar(
            select(TypesModel).where(TypesModel.id == self.types_id)
        )

        if not existing_types:
            raise HTTPException(
                status_code=404,
                detail="Types not found"
            )

        # Prepare update data
        update_data = {}

        if self.data.name is not None:
            types_name = self.data.name.strip().upper()
            update_data['name'] = types_name

            # Check duplicate if name is being changed
            if types_name != existing_types.name:
                duplicate_types = await self.db_session.scalar(
                    select(TypesModel).where(
                        TypesModel.name == types_name,
                        TypesModel.id != self.types_id
                    )
                )
                if duplicate_types:
                    raise HTTPException(
                        status_code=409,
                        detail="Types already exists"
                    )

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        try:
            # Perform update
            await self.db_session.execute(
                update(TypesModel)
                .where(TypesModel.id == self.types_id)
                .values(**update_data)
            )

            await self.db_session.commit()

            # Fetch updated Types
            updated_types = await self.db_session.scalar(
                select(TypesModel).where(TypesModel.id == self.types_id)
            )

            return updated_types

        except Exception:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error updating Types"
            )



########################################################################### Type Classes
class FetchTypeRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def fetch_type(
            self,
            type_id: Optional[int] = None,
            types_id: Optional[int] = None,
            subtype_id: Optional[int] = None,
            size1_id: Optional[int] = None,
            size2_id: Optional[int] = None,
            material_id: Optional[int] = None,
            description_id: Optional[int] = None,
            type_name: Optional[str] = None,
            subtype_name: Optional[str] = None,
            size1_name: Optional[str] = None,
            size2_name: Optional[str] = None,
            material_name: Optional[str] = None,
            description_name: Optional[str] = None,
            thickness_1: Optional[str] = None,
            thickness_2: Optional[str] = None,
            page: int = 1,
            limit: int = 50
    ):

        # Build base query with joins for name filters
        query = select(TypeModel).options(
            selectinload(TypeModel.type),
            selectinload(TypeModel.subtype),
            selectinload(TypeModel.size1),
            selectinload(TypeModel.size2),
            selectinload(TypeModel.material),
            selectinload(TypeModel.description)
        )

        # Apply filters
        # ID filters
        if type_id is not None:
            query = query.where(TypeModel.id == type_id)

        if types_id is not None:
            query = query.where(TypeModel.type_id == types_id)

        if subtype_id is not None:
            query = query.where(TypeModel.subtype_id == subtype_id)

        if size1_id is not None:
            query = query.where(TypeModel.size1_id == size1_id)

        if size2_id is not None:
            query = query.where(TypeModel.size2_id == size2_id)

        if material_id is not None:
            query = query.where(TypeModel.material_id == material_id)

        if description_id is not None:
            query = query.where(TypeModel.description_id == description_id)

        # Name filters (case-insensitive partial match)
        if type_name is not None:
            query = query.join(TypeModel.type).where(
                TypesModel.name.ilike(f"%{type_name}%")
            )

        if subtype_name is not None:
            query = query.join(TypeModel.subtype).where(
                SubTypeModel.name.ilike(f"%{subtype_name}%")
            )

        if size1_name is not None:
            query = query.join(TypeModel.size1).where(
                Size1Model.name.ilike(f"%{size1_name}%")
            )

        if size2_name is not None:
            query = query.join(TypeModel.size2).where(
                Size2Model.name.ilike(f"%{size2_name}%")
            )

        if material_name is not None:
            query = query.join(TypeModel.material).where(
                MaterialModel.name.ilike(f"%{material_name}%")
            )

        if description_name is not None:
            query = query.join(TypeModel.description).where(
                DescriptionModel.name.ilike(f"%{description_name}%")
            )

        # Thickness filters
        if thickness_1 is not None:
            query = query.where(TypeModel.thickness_1 == thickness_1)

        if thickness_2 is not None:
            query = query.where(TypeModel.thickness_2 == thickness_2)

        # Get total count before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.db_session.scalar(count_query)

        if total_count == 0:
            return [], 0

        # Apply pagination
        offset = (page - 1) * limit
        query = query.order_by(TypeModel.id).offset(offset).limit(limit)

        # Execute query
        result = await self.db_session.execute(query)
        types = result.scalars().all()

        return types, total_count

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

class UpdateTypeRepository:

    def __init__(
            self,
            db_session: AsyncSession,
            data: UpdateTypeSchema,
            user_id: int,
            type_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id
        self.type_id = type_id

    async def update_type(self):

        # Authorization (same as other endpoints)
        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Check if Type exists
        existing_type = await self.db_session.scalar(
            select(TypeModel).where(TypeModel.id == self.type_id)
        )

        if not existing_type:
            raise HTTPException(
                status_code=404,
                detail="Type not found"
            )

        # Prepare update data (only include fields that are provided)
        update_data = {}

        if self.data.type_id is not None:
            # Validate that type_id exists in TypesModel
            type_exists = await self.db_session.scalar(
                select(TypesModel).where(TypesModel.id == self.data.type_id)
            )
            if not type_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Type with id {self.data.type_id} not found"
                )
            update_data['type_id'] = self.data.type_id

        if self.data.subtype_id is not None:
            # Validate that subtype_id exists in SubTypeModel
            subtype_exists = await self.db_session.scalar(
                select(SubTypeModel).where(SubTypeModel.id == self.data.subtype_id)
            )
            if not subtype_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"SubType with id {self.data.subtype_id} not found"
                )
            update_data['subtype_id'] = self.data.subtype_id

        if self.data.size1_id is not None:
            # Validate that size1_id exists in Size1Model
            size1_exists = await self.db_session.scalar(
                select(Size1Model).where(Size1Model.id == self.data.size1_id)
            )
            if not size1_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Size1 with id {self.data.size1_id} not found"
                )
            update_data['size1_id'] = self.data.size1_id

        if self.data.size2_id is not None:
            # Validate that size2_id exists in Size2Model (can be nullable)
            if self.data.size2_id > 0:  # Assuming 0 or negative means null
                size2_exists = await self.db_session.scalar(
                    select(Size2Model).where(Size2Model.id == self.data.size2_id)
                )
                if not size2_exists:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Size2 with id {self.data.size2_id} not found"
                    )
            update_data['size2_id'] = self.data.size2_id if self.data.size2_id > 0 else None

        if self.data.material_id is not None:
            # Validate that material_id exists in MaterialModel
            material_exists = await self.db_session.scalar(
                select(MaterialModel).where(MaterialModel.id == self.data.material_id)
            )
            if not material_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Material with id {self.data.material_id} not found"
                )
            update_data['material_id'] = self.data.material_id

        if self.data.description_id is not None:
            # Validate that description_id exists in DescriptionModel
            description_exists = await self.db_session.scalar(
                select(DescriptionModel).where(DescriptionModel.id == self.data.description_id)
            )
            if not description_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Description with id {self.data.description_id} not found"
                )
            update_data['description_id'] = self.data.description_id

        if self.data.thickness_1 is not None:
            update_data['thickness_1'] = self.data.thickness_1.strip() if self.data.thickness_1 else None

        if self.data.thickness_2 is not None:
            update_data['thickness_2'] = self.data.thickness_2.strip() if self.data.thickness_2 else None

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        try:
            # Perform update
            await self.db_session.execute(
                update(TypeModel)
                .where(TypeModel.id == self.type_id)
                .values(**update_data)
            )

            await self.db_session.commit()

            # Fetch updated Type with all relationships
            updated_type = await self.db_session.scalar(
                select(TypeModel)
                .options(
                    selectinload(TypeModel.type),
                    selectinload(TypeModel.subtype),
                    selectinload(TypeModel.size1),
                    selectinload(TypeModel.size2),
                    selectinload(TypeModel.material),
                    selectinload(TypeModel.description)
                )
                .where(TypeModel.id == self.type_id)
            )

            return updated_type

        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating Type: {str(e)}"
            )



########################################################################### Stock Classes
class FetchStockRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def fetch_stock(
            self,
            stock_id: Optional[int] = None,
            stock_code: Optional[str] = None,
            alternative_id: Optional[str] = None,
            old_code: Optional[str] = None,
            comment: Optional[str] = None,
            type_id: Optional[int] = None,
            uom_id: Optional[int] = None,
            # Name filters for relationships
            type_name: Optional[str] = None,
            uom_name: Optional[str] = None,
            # Pagination
            page: int = 1,
            limit: int = 50
    ):

        # Build base query with eager loading for ALL nested relationships
        query = select(StockDataModel).options(
            selectinload(StockDataModel.item_type).selectinload(TypeModel.type),  # Load type.name
            selectinload(StockDataModel.item_type).selectinload(TypeModel.subtype),  # Load subtype.name
            selectinload(StockDataModel.item_type).selectinload(TypeModel.size1),  # Load size1.name
            selectinload(StockDataModel.item_type).selectinload(TypeModel.size2),  # Load size2.name
            selectinload(StockDataModel.item_type).selectinload(TypeModel.material),  # Load material.name
            selectinload(StockDataModel.item_type).selectinload(TypeModel.description),  # Load description.name
            selectinload(StockDataModel.uom)  # Load uom.name
        )

        # Apply ID filters
        if stock_id is not None:
            query = query.where(StockDataModel.id == stock_id)

        if type_id is not None:
            query = query.where(StockDataModel.type_id == type_id)

        if uom_id is not None:
            query = query.where(StockDataModel.uom_id == uom_id)

        # Apply string filters (case-insensitive partial match)
        if stock_code is not None:
            query = query.where(StockDataModel.stock_code.ilike(f"%{stock_code}%"))

        if alternative_id is not None:
            query = query.where(StockDataModel.alternative_id.ilike(f"%{alternative_id}%"))

        if old_code is not None:
            query = query.where(StockDataModel.old_code.ilike(f"%{old_code}%"))

        if comment is not None:
            query = query.where(StockDataModel.comment.ilike(f"%{comment}%"))

        # Apply relationship name filters
        if type_name is not None:
            query = query.join(StockDataModel.item_type).join(TypeModel.type).where(
                TypesModel.name.ilike(f"%{type_name}%")
            )

        if uom_name is not None:
            query = query.join(StockDataModel.uom).where(
                UomModel.name.ilike(f"%{uom_name}%")
            )

        # Get total count before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.db_session.scalar(count_query)

        if total_count == 0:
            return [], 0

        # Apply pagination
        offset = (page - 1) * limit
        query = query.order_by(StockDataModel.id).offset(offset).limit(limit)

        # Execute query
        result = await self.db_session.execute(query)
        stocks = result.scalars().all()

        return stocks, total_count


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


class UpdateStockRepository:

    def __init__(
            self,
            db_session: AsyncSession,
            data: UpdateStockSchema,
            user_id: int,
            stock_id: int
    ):
        self.db_session = db_session
        self.data = data
        self.user_id = user_id
        self.stock_id = stock_id

    async def update_stock(self):

        # Authorization
        await CheckAdminManagerAuthorize(
            self.db_session,
            self.user_id
        ).check_admin_or_manager()

        # Check if Stock exists
        existing_stock = await self.db_session.scalar(
            select(StockDataModel).where(StockDataModel.id == self.stock_id)
        )

        if not existing_stock:
            raise HTTPException(
                status_code=404,
                detail="Stock data not found"
            )

        # Prepare update data
        update_data = {}

        if self.data.stock_code is not None:
            stock_code_upper = self.data.stock_code.strip().upper()
            update_data['stock_code'] = stock_code_upper

            # Check duplicate if stock_code is being changed
            if stock_code_upper != existing_stock.stock_code:
                duplicate_stock = await self.db_session.scalar(
                    select(StockDataModel).where(
                        StockDataModel.stock_code == stock_code_upper,
                        StockDataModel.id != self.stock_id
                    )
                )
                if duplicate_stock:
                    raise HTTPException(
                        status_code=409,
                        detail="Stock code already exists"
                    )

        if self.data.alternative_id is not None:
            update_data[
                'alternative_id'] = self.data.alternative_id.strip().upper() if self.data.alternative_id else None

        if self.data.old_code is not None:
            update_data['old_code'] = self.data.old_code.strip().upper() if self.data.old_code else None

        if self.data.comment is not None:
            update_data['comment'] = self.data.comment.strip()

        if self.data.type_id is not None:
            # Validate that type_id exists in TypeModel
            type_exists = await self.db_session.scalar(
                select(TypeModel).where(TypeModel.id == self.data.type_id)
            )
            if not type_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Type with id {self.data.type_id} not found"
                )
            update_data['type_id'] = self.data.type_id

        if self.data.uom_id is not None:
            # Validate that uom_id exists in UomModel
            uom_exists = await self.db_session.scalar(
                select(UomModel).where(UomModel.id == self.data.uom_id)
            )
            if not uom_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"UOM with id {self.data.uom_id} not found"
                )
            update_data['uom_id'] = self.data.uom_id

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        try:
            # Perform update
            await self.db_session.execute(
                update(StockDataModel)
                .where(StockDataModel.id == self.stock_id)
                .values(**update_data)
            )

            await self.db_session.commit()

            # Fetch updated Stock with relationships
            updated_stock = await self.db_session.scalar(
                select(StockDataModel)
                .options(
                    selectinload(StockDataModel.item_type),
                    selectinload(StockDataModel.uom)
                )
                .where(StockDataModel.id == self.stock_id)
            )

            return updated_stock

        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating Stock data: {str(e)}"
            )



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



########################################################################### Unique Values
class FetchUniqueValues:

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def fetch_unique_values(
            self,
            tables: Optional[List[str]] = None  # Optional: specify which tables to fetch
    ) -> Dict[str, Any]:

        result = {}

        # Define all available queries
        queries = {
            "areas": self._get_areas,
            "locations": self._get_locations,
            "uoms": self._get_uoms,
            "subtypes": self._get_subtypes,
            "size1": self._get_size1,
            "size2": self._get_size2,
            "materials": self._get_materials,
            "descriptions": self._get_descriptions,
            "item_types": self._get_item_types,
            "stock_codes": self._get_stock_codes,
            "thickness": self._get_thickness,
            "project_ids": self._get_project_ids
        }

        # If specific tables requested, only fetch those
        if tables:
            for table in tables:
                if table in queries:
                    result[table] = await queries[table]()
        else:
            # Fetch all tables
            for key, query_func in queries.items():
                result[key] = await query_func()

        return result

    async def _get_areas(self) -> List[Dict]:
        query = select(
            AreaModel.id,
            AreaModel.name,
            AreaModel.description,
            AreaModel.project_id
        ).order_by(AreaModel.name)
        result = await self.db.execute(query)
        areas = result.all()
        return [
            {
                "id": area.id,
                "name": area.name,
                "description": area.description,
                "project_id": area.project_id
            }
            for area in areas
        ]

    async def _get_locations(self) -> List[Dict]:
        query = select(
            LocationModel.id,
            LocationModel.name,
            LocationModel.project_id
        ).order_by(LocationModel.name)
        result = await self.db.execute(query)
        locations = result.all()
        return [
            {
                "id": loc.id,
                "name": loc.name,
                "project_id": loc.project_id
            }
            for loc in locations
        ]

    async def _get_uoms(self) -> List[Dict]:
        query = select(UomModel.id, UomModel.name).order_by(UomModel.name)
        result = await self.db.execute(query)
        uoms = result.all()
        return [{"id": uom.id, "name": uom.name} for uom in uoms]

    async def _get_subtypes(self) -> List[Dict]:
        query = select(SubTypeModel.id, SubTypeModel.name).order_by(SubTypeModel.name)
        result = await self.db.execute(query)
        subtypes = result.all()
        return [{"id": sub.id, "name": sub.name} for sub in subtypes]

    async def _get_size1(self) -> List[Dict]:
        query = select(Size1Model.id, Size1Model.name).order_by(Size1Model.name)
        result = await self.db.execute(query)
        size1_list = result.all()
        return [{"id": size.id, "name": size.name} for size in size1_list]

    async def _get_size2(self) -> List[Dict]:
        query = select(Size2Model.id, Size2Model.name).order_by(Size2Model.name)
        result = await self.db.execute(query)
        size2_list = result.all()
        return [{"id": size.id, "name": size.name} for size in size2_list]

    async def _get_materials(self) -> List[Dict]:
        query = select(MaterialModel.id, MaterialModel.name).order_by(MaterialModel.name)
        result = await self.db.execute(query)
        materials = result.all()
        return [{"id": mat.id, "name": mat.name} for mat in materials]

    async def _get_descriptions(self) -> List[Dict]:
        query = select(DescriptionModel.id, DescriptionModel.name).order_by(DescriptionModel.name)
        result = await self.db.execute(query)
        descriptions = result.all()
        return [{"id": desc.id, "name": desc.name} for desc in descriptions]

    async def _get_item_types(self) -> List[Dict]:
        query = select(TypesModel.id, TypesModel.name).order_by(TypesModel.name)
        result = await self.db.execute(query)
        item_types = result.all()
        return [{"id": it.id, "name": it.name} for it in item_types]

    async def _get_stock_codes(self) -> List[Dict]:
        query = select(
            StockDataModel.id,
            StockDataModel.stock_code,
            StockDataModel.alternative_id,
            StockDataModel.old_code,
            StockDataModel.comment
        ).order_by(StockDataModel.stock_code)
        result = await self.db.execute(query)
        stock_codes = result.all()
        return [
            {
                "id": stock.id,
                "stock_code": stock.stock_code,
                "alternative_id": stock.alternative_id,
                "old_code": stock.old_code,
                "comment": stock.comment
            }
            for stock in stock_codes
        ]

    async def _get_thickness(self) -> List[str]:
        # Get unique thickness values from TypeModel
        thickness_1_query = select(distinct(TypeModel.thickness_1)).where(
            TypeModel.thickness_1.isnot(None),
            TypeModel.thickness_1 != ""
        )
        thickness_1_result = await self.db.execute(thickness_1_query)
        thickness_1_values = [t[0] for t in thickness_1_result.all() if t[0]]

        thickness_2_query = select(distinct(TypeModel.thickness_2)).where(
            TypeModel.thickness_2.isnot(None),
            TypeModel.thickness_2 != ""
        )
        thickness_2_result = await self.db.execute(thickness_2_query)
        thickness_2_values = [t[0] for t in thickness_2_result.all() if t[0]]

        # Combine and sort unique values
        all_thickness = sorted(list(set(thickness_1_values + thickness_2_values)))
        return all_thickness

    async def _get_project_ids(self) -> List[int]:
        query = select(distinct(AreaModel.project_id)).union(
            select(distinct(LocationModel.project_id))
        ).order_by(AreaModel.project_id)
        result = await self.db.execute(query)
        project_ids = [p[0] for p in result.all() if p[0]]
        return project_ids



########################################################################### Types without stock_code
class FetchTypesWithoutStockCode:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_types_without_stock(self) -> Dict[str, Any]:
        """
        Fetch all TypeModel records that are NOT referenced in any StockDataModel
        """

        # Subquery to get all type_id values that exist in stock_data
        stock_type_ids_subquery = (
            select(StockDataModel.type_id)
            .distinct()
            .where(StockDataModel.type_id.isnot(None))
            .subquery()
        )

        # Main query: Get all TypeModel records where id is NOT in the subquery
        query = (
            select(TypeModel)
            .where(
                TypeModel.id.notin_(select(stock_type_ids_subquery))
            )
            .options(
                selectinload(TypeModel.type),
                selectinload(TypeModel.subtype),
                selectinload(TypeModel.size1),
                selectinload(TypeModel.size2),
                selectinload(TypeModel.material),
                selectinload(TypeModel.description)
            )
            .order_by(TypeModel.id)
        )

        # Execute query
        result = await self.db.execute(query)
        types_without_stock = result.scalars().all()

        # Format the response
        formatted_results = []
        for type_obj in types_without_stock:
            formatted_results.append({
                "id": type_obj.id,
                "type_id": type_obj.type_id,
                "type_name": type_obj.type.name if type_obj.type else None,
                "subtype_id": type_obj.subtype_id,
                "subtype_name": type_obj.subtype.name if type_obj.subtype else None,
                "size1_id": type_obj.size1_id,
                "size1_name": type_obj.size1.name if type_obj.size1 else None,
                "size2_id": type_obj.size2_id,
                "size2_name": type_obj.size2.name if type_obj.size2 else None,
                "material_id": type_obj.material_id,
                "material_name": type_obj.material.name if type_obj.material else None,
                "description_id": type_obj.description_id,
                "description_name": type_obj.description.name if type_obj.description else None,
                "thickness_1": type_obj.thickness_1,
                "thickness_2": type_obj.thickness_2,
                # Full relationship objects (optional)
                "type": {
                    "id": type_obj.type.id,
                    "name": type_obj.type.name
                } if type_obj.type else None,
                "subtype": {
                    "id": type_obj.subtype.id,
                    "name": type_obj.subtype.name
                } if type_obj.subtype else None,
                "size1": {
                    "id": type_obj.size1.id,
                    "name": type_obj.size1.name
                } if type_obj.size1 else None,
                "size2": {
                    "id": type_obj.size2.id,
                    "name": type_obj.size2.name
                } if type_obj.size2 else None,
                "material": {
                    "id": type_obj.material.id,
                    "name": type_obj.material.name
                } if type_obj.material else None,
                "description": {
                    "id": type_obj.description.id,
                    "name": type_obj.description.name
                } if type_obj.description else None,
            })

        return {
            "message": "Types without stock code fetched successfully",
            "count": len(formatted_results),
            "data": formatted_results
        }
