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
    CreateStockRepository, FetchAreaRepository, FetchLocationRepository, FetchUomRepository, FetchTypeRepository,
    FetchStockRepository, CreateDescriptionRepository, CreateMaterialRepository, CreateSize2Repository,
    CreateSize1Repository, CreateSubTypeRepository, FetchSubTypeRepository, FetchSize1Repository, FetchSize2Repository,
    FetchMaterialRepository, FetchDescriptionRepository
)

router = APIRouter()




# router/admin_router.py (add these fetch endpoints)

@router.get("/fetch_area", status_code=200)
async def fetch_area(
        db: Annotated[AsyncSession, Depends(get_db)],
        area_id: int = None,
        project_id: int = None
):
    try:
        repo = FetchAreaRepository(db, area_id, project_id)
        result = await repo.fetch_area()
        return {"data": result}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(500, f'Internal server error {ex}')


@router.get("/fetch_location", status_code=200)
async def fetch_location(
        db: Annotated[AsyncSession, Depends(get_db)],
        location_id: int = None,
        project_id: int = None
):
    try:
        repo = FetchLocationRepository(db, location_id, project_id)
        result = await repo.fetch_location()
        return {"data": result}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(500, f'Internal server error {ex}')


@router.get("/fetch_uom", status_code=200)
async def fetch_uom(
        db: Annotated[AsyncSession, Depends(get_db)],
        uom_id: int = None
):
    try:
        repo = FetchUomRepository(db, uom_id)
        result = await repo.fetch_uom()
        return {"data": result}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(500, f'Internal server error {ex}')


@router.get("/fetch_type", status_code=200)
async def fetch_type(
        db: Annotated[AsyncSession, Depends(get_db)],
        type_id: int = None
):
    try:
        repo = FetchTypeRepository(db, type_id)
        result = await repo.fetch_type()
        return {"data": result}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(500, f'Internal server error {ex}')


@router.get("/fetch_stock_data", status_code=200)
async def fetch_stock_data(
        db: Annotated[AsyncSession, Depends(get_db)],
        stock_id: int = None,
        stock_code: str = None
):
    try:
        repo = FetchStockRepository(db, stock_id, stock_code)
        result = await repo.fetch_stock()
        return {"data": result}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(500, f'Internal server error {ex}')





@router.post("/create_area", status_code=201)
async def create_area(
        data: CreateAreaSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = CreateAreaRepository(db, data, int(user_id))
        result = await repo.create_area()
        return {"message": "Area created successfully", "id": result.id, "name": result.name}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
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
        return {"message": "Type created successfully", "id": result.id}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
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
        raise HTTPException(500, f'Internal server error {ex}')



@router.post("/create_subtype", status_code=201)
async def create_subtype(
        data: CreateSubTypeSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = CreateSubTypeRepository(db, data, int(user_id))
        result = await repo.create_subtype()
        return {"message": "SubType created successfully", "id": result.id, "name": result.name}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.post("/create_size1", status_code=201)
async def create_size1(
        data: CreateSize1Schema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = CreateSize1Repository(db, data, int(user_id))
        result = await repo.create_size1()
        return {"message": "Size1 created successfully", "id": result.id, "name": result.name}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.post("/create_size2", status_code=201)
async def create_size2(
        data: CreateSize2Schema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = CreateSize2Repository(db, data, int(user_id))
        result = await repo.create_size2()
        return {"message": "Size2 created successfully", "id": result.id, "name": result.name}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.post("/create_material", status_code=201)
async def create_material(
        data: CreateMaterialSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = CreateMaterialRepository(db, data, int(user_id))
        result = await repo.create_material()
        return {"message": "Material created successfully", "id": result.id, "name": result.name}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.post("/create_description", status_code=201)
async def create_description(
        data: CreateDescriptionSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = CreateDescriptionRepository(db, data, int(user_id))
        result = await repo.create_description()
        return {"message": "Description created successfully", "id": result.id, "name": result.name}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')



# router/admin_router.py (add these fetch endpoints)

@router.get("/fetch_subtype", status_code=200)
async def fetch_subtype(
        db: Annotated[AsyncSession, Depends(get_db)],
        subtype_id: int = None
):
    try:
        repo = FetchSubTypeRepository(db, subtype_id)
        result = await repo.fetch_subtype()
        return {"data": result}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.get("/fetch_size1", status_code=200)
async def fetch_size1(
        db: Annotated[AsyncSession, Depends(get_db)],
        size1_id: int = None
):
    try:
        repo = FetchSize1Repository(db, size1_id)
        result = await repo.fetch_size1()
        return {"data": result}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.get("/fetch_size2", status_code=200)
async def fetch_size2(
        db: Annotated[AsyncSession, Depends(get_db)],
        size2_id: int = None
):
    try:
        repo = FetchSize2Repository(db, size2_id)
        result = await repo.fetch_size2()
        return {"data": result}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.get("/fetch_material", status_code=200)
async def fetch_material(
        db: Annotated[AsyncSession, Depends(get_db)],
        material_id: int = None
):
    try:
        repo = FetchMaterialRepository(db, material_id)
        result = await repo.fetch_material()
        return {"data": result}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.get("/fetch_description", status_code=200)
async def fetch_description(
        db: Annotated[AsyncSession, Depends(get_db)],
        description_id: int = None
):
    try:
        repo = FetchDescriptionRepository(db, description_id)
        result = await repo.fetch_description()
        return {"data": result}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')


@router.get("/fetch_type", status_code=200)
async def fetch_type(
        db: Annotated[AsyncSession, Depends(get_db)],
        type_id: int = None
):
    try:
        repo = FetchTypeRepository(db, type_id)
        result = await repo.fetch_type()
        return {"data": result}
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print('ex is ', ex)
        raise HTTPException(500, f'Internal server error {ex}')