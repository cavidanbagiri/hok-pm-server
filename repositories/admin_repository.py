# repository/admin_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from models.user_model import UserModel, ProjectModel, StatusModel
from schemas.admin_schema import CreateProjectSchema

class CheckAdminManagerAuthorize:

    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id

    async def check_admin_or_manager(self):
        """
        Get user by user id and check if "Admin" or "Manager"
        continue
        :return:
        """
        # Get user with status relationship
        query = select(UserModel).where(UserModel.id == self.user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(404, "User not found")

        # Get status name (assuming status table has 'admin' and 'manager' entries)
        status_query = select(StatusModel).where(StatusModel.id == user.status_id)
        status_result = await self.db.execute(status_query)
        status = status_result.scalar_one_or_none()

        if not status:
            raise HTTPException(404, "Status not found")

        if status.status.lower() not in ["admin", "manager"]:
            raise HTTPException(403, "Authorization Error. Please write to admin")

        return user


class CreateProjectRepository:

    def __init__(self, db: AsyncSession, project_data: CreateProjectSchema, user_id: int):
        self.db = db
        self.project_data = project_data
        self.user_id = user_id

    async def create_project(self):
        """
        Check if user is admin or manager
        then
        can create a project
        otherwise
        return and Authorization Error
        :return:
        """
        # Check authorization
        auth_check = CheckAdminManagerAuthorize(self.db, self.user_id)
        await auth_check.check_admin_or_manager()
        print(f"project data is {self.project_data}")
        # Create new project
        new_project = ProjectModel(
            name=self.project_data.name.lower(),
            code=self.project_data.code.lower(),
            country=self.project_data.country.lower(),
        )

        self.db.add(new_project)
        await self.db.commit()
        await self.db.refresh(new_project)

        return new_project