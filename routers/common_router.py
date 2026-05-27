# router/admin_router.py
from fastapi import APIRouter, Depends, Response, HTTPException, Request
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from auth.token_handler import TokenHandler
from database.setup import get_db

from schemas.common_schema import *

from repositories.common_repository import *

router = APIRouter()


# ########################################################################### Area Functions Filter tested
@router.get("/fetch_area", status_code=200)
async def fetch_area(
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token),
        project_id: int | None = None,
        name: str | None = None,
        description: str | None = None,
        doc_no: str | None = None,
        doc_rev: str | None = None,
        say_iso_no: str | None = None,
):
    try:
        user_id = int(user_info['sub'])

        repo = FetchAreaRepository(db)

        result = await repo.fetch_area(
            user_id=user_id,
            project_id=project_id,
            name=name,
            description=description,
            doc_no=doc_no,
            doc_rev=doc_rev,
            say_iso_no=say_iso_no
        )

        return {"data": result}

    except HTTPException as ex:
        raise ex

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.put("/update_area/{area_id}", status_code=200)
async def update_area(
        area_id: int,
        data: UpdateAreaSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = UpdateAreaRepository(db, data, int(user_id), area_id)
        result = await repo.update_area()
        return {
            "message": "Area updated successfully",
            "id": result.id,
            "name": result.name,
            "description": result.description,
            "doc_no": result.doc_no,
            "doc_rev": result.doc_rev,
            "say_iso_no": result.say_iso_no,
            "project_id": result.project_id
        }
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print(ex)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )




########################################################################### Location Functions Filter tested
@router.get("/fetch_location", status_code=200)
async def fetch_location(
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token),

        # Filters
        project_id: int | None = None,
        name: str | None = None,
):
    try:

        user_id = int(user_info['sub'])

        repo = FetchLocationRepository(db)

        result = await repo.fetch_location(
            user_id=user_id,
            project_id=project_id,
            name=name
        )

        return {"data": result}

    except HTTPException as ex:
        raise ex

    except Exception as ex:
        raise HTTPException(
            500,
            f"Internal server error {ex}"
        )


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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.put("/update_location/{location_id}", status_code=200)
async def update_location(
        location_id: int,
        data: UpdateLocationSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = UpdateLocationRepository(db, data, int(user_id), location_id)
        result = await repo.update_location()
        return {
            "message": "Location updated successfully",
            "id": result.id,
            "name": result.name,
            "project_id": result.project_id
        }
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )



########################################################################### Location Functions
@router.get("/fetch_uom", status_code=200)
async def fetch_uom(
        db: Annotated[AsyncSession, Depends(get_db)],

        # Filters
        uom_id: int | None = None,
        name: str | None = None,
):
    try:

        repo = FetchUomRepository(db)

        result = await repo.fetch_uom(
            uom_id=uom_id,
            name=name
        )

        return {"data": result}

    except HTTPException as ex:
        raise ex

    except Exception as ex:
        raise HTTPException(
            500,
            f"Internal server error {ex}"
        )


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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.put("/update_uom/{uom_id}", status_code=200)
async def update_uom(
        uom_id: int,
        data: UpdateUomSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = UpdateUomRepository(db, data, int(user_id), uom_id)
        result = await repo.update_uom()
        return {
            "message": "UOM updated successfully",
            "id": result.id,
            "name": result.name
        }
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )





########################################################################### Size1 Functions
@router.get("/fetch_size1", status_code=200)
async def fetch_size1(
        db: Annotated[AsyncSession, Depends(get_db)],

        # Filters
        size1_id: int | None = None,
        name: str | None = None,
):
    try:

        repo = FetchSize1Repository(db)

        result = await repo.fetch_size1(
            size1_id=size1_id,
            name=name
        )

        return {"data": result}

    except HTTPException as ex:
        raise ex

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.put("/update_size1/{size1_id}", status_code=200)
async def update_size1(
        size1_id: int,
        data: UpdateSize1Schema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = UpdateSize1Repository(db, data, int(user_id), size1_id)
        result = await repo.update_size1()
        return {
            "message": "Size1 updated successfully", 
            "id": result.id, 
            "name": result.name
        }
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.post("/bulk_create_size1", status_code=201)
async def bulk_create_size1(
        data: BulkCreateSize1Schema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = BulkCreateSize1Repository(db, data, int(user_id))
        result = await repo.bulk_create_size1()
        return result
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )




########################################################################### Size2 Functions
@router.get("/fetch_size2", status_code=200)
async def fetch_size2(
        db: Annotated[AsyncSession, Depends(get_db)],

        # Filters
        size2_id: int | None = None,
        name: str | None = None,
):
    try:

        repo = FetchSize2Repository(db)

        result = await repo.fetch_size2(
            size2_id=size2_id,
            name=name
        )

        return {"data": result}

    except HTTPException as ex:
        raise ex

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.put("/update_size2/{size2_id}", status_code=200)
async def update_size2(
        size2_id: int,
        data: UpdateSize2Schema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = UpdateSize2Repository(db, data, int(user_id), size2_id)
        result = await repo.update_size2()
        return {
            "message": "Size2 updated successfully",
            "id": result.id,
            "name": result.name
        }
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post("/bulk_create_size2", status_code=201)
async def bulk_create_size2(
        data: BulkCreateSize2Schema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = BulkCreateSize2Repository(db, data, int(user_id))
        result = await repo.bulk_create_size2()
        return result
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )





########################################################################### Material Functions
@router.get("/fetch_material", status_code=200)
async def fetch_material(
        db: Annotated[AsyncSession, Depends(get_db)],

        # Filters
        material_id: int | None = None,
        name: str | None = None,
):
    try:

        repo = FetchMaterialRepository(db)

        result = await repo.fetch_material(
            material_id=material_id,
            name=name
        )

        return {"data": result}

    except HTTPException as ex:
        raise ex

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.put("/update_material/{material_id}", status_code=200)
async def update_material(
        material_id: int,
        data: UpdateMaterialSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = UpdateMaterialRepository(db, data, int(user_id), material_id)
        result = await repo.update_material()
        return {
            "message": "Material updated successfully",
            "id": result.id,
            "name": result.name
        }
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post("/bulk_create_material", status_code=201)
async def bulk_create_material(
        data: BulkCreateMaterialSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = BulkCreateMaterialRepository(db, data, int(user_id))
        result = await repo.bulk_create_material()
        return result
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )



########################################################################### Description Functions
@router.get("/fetch_description", status_code=200)
async def fetch_description(
        db: Annotated[AsyncSession, Depends(get_db)],

        # Filters
        description_id: int | None = None,
        name: str | None = None,
):
    try:

        repo = FetchDescriptionRepository(db)

        result = await repo.fetch_description(
            description_id=description_id,
            name=name
        )

        return {"data": result}

    except HTTPException as ex:
        raise ex

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.put("/update_description/{description_id}", status_code=200)
async def update_description(
        description_id: int,
        data: UpdateDescriptionSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = UpdateDescriptionRepository(db, data, int(user_id), description_id)
        result = await repo.update_description()
        return {
            "message": "Description updated successfully",
            "id": result.id,
            "name": result.name
        }
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post("/bulk_create_description", status_code=201)
async def bulk_create_descriptions(
        data: BulkCreateDescriptionSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = BulkCreateDescriptionRepository(db, data, int(user_id))
        result = await repo.bulk_create_descriptions()
        return result
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )



########################################################################### Subtype Functions
@router.get("/fetch_subtype", status_code=200)
async def fetch_subtype(
        db: Annotated[AsyncSession, Depends(get_db)],

        # Filters
        subtype_id: int | None = None,
        name: str | None = None,
):
    try:

        repo = FetchSubTypeRepository(db)

        result = await repo.fetch_subtype(
            subtype_id=subtype_id,
            name=name
        )

        return {"data": result}

    except HTTPException as ex:
        raise ex

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.put("/update_subtype/{subtype_id}", status_code=200)
async def update_subtype(
        subtype_id: int,
        data: UpdateSubTypeSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = UpdateSubTypeRepository(db, data, int(user_id), subtype_id)
        result = await repo.update_subtype()
        return {
            "message": "SubType updated successfully",
            "id": result.id,
            "name": result.name
        }
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post("/bulk_create_subtype", status_code=201)
async def bulk_create_subtype(
        data: BulkCreateSubTypeSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = BulkCreateSubTypeRepository(db, data, int(user_id))
        result = await repo.bulk_create_subtype()
        return result
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


########################################################################### Types Functions # Can be: [valve, reducer, pee, tie, elbow, ...]
@router.get("/fetch_item_types", status_code=200)
async def fetch_types(
        db: Annotated[AsyncSession, Depends(get_db)],

        # Filters
        types_id: int | None = None,
        name: str | None = None,
):
    try:

        repo = FetchItemTypesRepository(db)

        result = await repo.fetch_types(
            types_id=types_id,
            name=name
        )

        return {"data": result}

    except HTTPException as ex:
        raise ex

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.post("/create_item_types", status_code=201)
async def create_types(
        data: CreateTypesSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = CreateItemTypesRepository(db, data, int(user_id))
        result = await repo.create_types()
        return {"message": "Types created successfully", "id": result.id, "name": result.name}
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.put("/update_item_types/{types_id}", status_code=200)
async def update_types(
        types_id: int,
        data: UpdateTypesSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token)
):
    try:
        user_id = user_info.get('sub')
        repo = UpdateItemTypesRepository(db, data, int(user_id), types_id)
        result = await repo.update_types()
        return {
            "message": "Types updated successfully",
            "id": result.id,
            "name": result.name
        }
    except HTTPException as ex:
        raise ex
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )



########################################################################### Type Functions
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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )



########################################################################### Stock Functions
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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )





########################################################################### Project Functions

@router.get("/fetch_projects", status_code=200)
async def fetch_projects(
        db: Annotated[AsyncSession, Depends(get_db)],
        user_info: dict = Depends(TokenHandler.verify_access_token),
):
    try:
        user_id = int(user_info.get('sub'))

        repo = FetchProjectRepository(db)
        result = await repo.fetch_project(user_id)

        return {"data": result}

    except HTTPException as ex:
        raise ex

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )