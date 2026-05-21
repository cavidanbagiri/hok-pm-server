# router/admin_router.py
from fastapi import APIRouter, Depends, Response, HTTPException, Request
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from auth.token_handler import TokenHandler
from database.setup import get_db

from schemas.common_schema import *

from repositories.common_repository import (
    CreateAreaRepository,
    CreateLocationRepository,
    CreateUomRepository,
    CreateTypeRepository,
    CreateStockRepository
)

router = APIRouter()


@router.post("/create_area", status_code=201)
async def create_area(
        data: CreateAreaSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        print('here work')
        user_id = user_info.get('sub')
        repo = CreateAreaRepository(db, data, int(user_id))
        result = await repo.create_area()
        return {"message": "Area created successfully", "id": result.id, "name": result.name}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.post("/create_location", status_code=201)
async def create_location(
        data: CreateLocationSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = CreateLocationRepository(db, data, int(user_id))
        result = await repo.create_location()
        return {"message": "Location created successfully", "id": result.id, "name": result.name}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.post("/create_uom", status_code=201)
async def create_uom(
        data: CreateUomSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = CreateUomRepository(db, data, int(user_id))
        result = await repo.create_uom()
        return {"message": "UOM created successfully", "id": result.id, "name": result.name}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.post("/create_type", status_code=201)
async def create_type(
        data: CreateTypeSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = CreateTypeRepository(db, data, int(user_id))
        result = await repo.create_type()
        return {"message": "Type created successfully", "id": result.id, "name": result.name}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.post("/create_stock", status_code=201)
async def create_stock(
        data: CreateStockSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = CreateStockRepository(db, data, int(user_id))
        result = await repo.create_stock()
        return {"message": "Stock created successfully", "id": result.id, "stock_code": result.stock_code}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')