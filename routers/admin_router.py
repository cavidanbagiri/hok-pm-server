# router/admin_router.py
from fastapi import APIRouter, Depends, Response, HTTPException, Request
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from database.setup import get_db
from schemas.admin_schema import CreateProjectSchema
from repositories.admin_repository import CreateProjectRepository
from auth.token_handler import TokenHandler

router = APIRouter()


@router.post('/create_project', status_code=201)
async def create_project(
        data: CreateProjectSchema,
        db_session: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token),
):
    print('here working')
    try:
        # Extract user_id from token payload (assuming 'sub' contains user_id)
        user_id = user_info.get('sub')
        if not user_id:
            raise HTTPException(401, "Invalid token: user_id not found")

        repo = CreateProjectRepository(db_session, data, int(user_id))  # Convert to int if needed
        project = await repo.create_project()
        return {"message": "Project created successfully", "project_id": project.id, "name": project.name}

    except HTTPException as ex:
        print('ex is ', ex)
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')