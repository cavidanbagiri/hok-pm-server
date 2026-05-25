# repository/admin_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from models.user_model import UserModel, ProjectModel, StatusModel
from schemas.admin_schema import CreateProjectSchema

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


class CreateProjectRepository:

    def __init__(
        self,
        db: AsyncSession,
        project_data: CreateProjectSchema,
        user_id: int
    ):
        self.db = db
        self.project_data = project_data
        self.user_id = user_id

    async def create_project(self):

        await CheckAdminManagerAuthorize(
            self.db,
            self.user_id
        ).check_admin_or_manager()

        project_name = self.project_data.name.strip().upper()
        project_code = self.project_data.code.strip().upper()
        project_country = self.project_data.country.strip().upper()

        existing_project = await self.db.scalar(
            select(ProjectModel).where(
                ProjectModel.name == project_name
            )
        )

        if existing_project:
            raise HTTPException(
                status_code=400,
                detail="Project already exists"
            )

        try:

            new_project = ProjectModel(
                name=project_name,
                code=project_code,
                country=project_country,
            )

            self.db.add(new_project)

            await self.db.commit()
            await self.db.refresh(new_project)

            return new_project

        except Exception:
            await self.db.rollback()
            raise