# router.py
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from auth.token_handler import TokenHandler
from database.setup import get_db
from repositories.mto_repository import FetchMTORepository

router = APIRouter()


@router.get("/fetch_mto", status_code=200)
async def fetch_mto(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_info: dict = Depends(TokenHandler.verify_access_token),
    # ID filters
    id: Optional[int] = Query(None, description="Filter by MTO ID"),
    # String exact filters
    no: Optional[str] = Query(None, description="Filter by No (exact match)"),
    reference_mto: Optional[str] = Query(None, description="Filter by Reference MTO (exact match)"),
    pid_no: Optional[str] = Query(None, description="Filter by PID No (exact match)"),
    line_no: Optional[str] = Query(None, description="Filter by Line No (exact match)"),
    isometric_drawing_no: Optional[str] = Query(None, description="Filter by Isometric Drawing No (exact match)"),
    iso_rev: Optional[str] = Query(None, description="Filter by ISO Rev (exact match)"),
    iso_and_rev: Optional[str] = Query(None, description="Filter by ISO and Rev (exact match)"),
    spec: Optional[str] = Query(None, description="Filter by Spec (exact match)"),
    comment: Optional[str] = Query(None, description="Filter by Comment (exact match)"),
    # String partial filters
    no_contains: Optional[str] = Query(None, description="Filter by No (contains)"),
    reference_mto_contains: Optional[str] = Query(None, description="Filter by Reference MTO (contains)"),
    pid_no_contains: Optional[str] = Query(None, description="Filter by PID No (contains)"),
    line_no_contains: Optional[str] = Query(None, description="Filter by Line No (contains)"),
    isometric_drawing_no_contains: Optional[str] = Query(None, description="Filter by Isometric Drawing No (contains)"),
    iso_rev_contains: Optional[str] = Query(None, description="Filter by ISO Rev (contains)"),
    iso_and_rev_contains: Optional[str] = Query(None, description="Filter by ISO and Rev (contains)"),
    spec_contains: Optional[str] = Query(None, description="Filter by Spec (contains)"),
    comment_contains: Optional[str] = Query(None, description="Filter by Comment (contains)"),
    # Date filters
    mto_date: Optional[date] = Query(None, description="Filter by exact MTO date"),
    mto_date_from: Optional[date] = Query(None, description="Filter by MTO date from"),
    mto_date_to: Optional[date] = Query(None, description="Filter by MTO date to"),
    # Numeric filters
    quantity: Optional[float] = Query(None, description="Filter by exact quantity"),
    quantity_min: Optional[float] = Query(None, description="Filter by minimum quantity"),
    quantity_max: Optional[float] = Query(None, description="Filter by maximum quantity"),
    required_area: Optional[float] = Query(None, description="Filter by exact required area"),
    required_area_min: Optional[float] = Query(None, description="Filter by minimum required area"),
    required_area_max: Optional[float] = Query(None, description="Filter by maximum required area"),
    required_iso: Optional[float] = Query(None, description="Filter by exact required ISO"),
    required_iso_min: Optional[float] = Query(None, description="Filter by minimum required ISO"),
    required_iso_max: Optional[float] = Query(None, description="Filter by maximum required ISO"),
    # Foreign Key filters
    location_id: Optional[int] = Query(None, description="Filter by Location ID"),
    area_id: Optional[int] = Query(None, description="Filter by Area ID"),
    area_2_id: Optional[int] = Query(None, description="Filter by Area 2 ID"),
    area_2_desc_id: Optional[int] = Query(None, description="Filter by Area 2 Description ID"),
    stock_data_id: Optional[int] = Query(None, description="Filter by Stock Data ID"),
    uom_id: Optional[int] = Query(None, description="Filter by UOM ID"),
    created_by_id: Optional[int] = Query(None, description="Filter by Created By User ID"),
    # Relationship name filters
    location_name: Optional[str] = Query(None, description="Filter by Location name (contains)"),
    area_name: Optional[str] = Query(None, description="Filter by Area name (contains)"),
    area_2_name: Optional[str] = Query(None, description="Filter by Area 2 name (contains)"),
    area_2_desc_name: Optional[str] = Query(None, description="Filter by Area 2 Description name (contains)"),
    stock_code: Optional[str] = Query(None, description="Filter by Stock Code (contains)"),
    uom_name: Optional[str] = Query(None, description="Filter by UOM name (contains)"),
    project_id: Optional[int] = Query(None, description="Filter by Project ID (admin/manager only)"),
    # Pagination
    page: Optional[int] = Query(1, ge=1, description="Page number"),
    limit: Optional[int] = Query(50, ge=1, le=200, description="Items per page"),
    # Sorting
    sort_by: Optional[str] = Query("id", description="Sort by field (id, no, reference_mto, mto_date, quantity, created_at)"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Sort order (asc or desc)")
):
    try:
        user_id = int(user_info["sub"])
        repo = FetchMTORepository(db, user_id)
        result = await repo.fetch_mto(
            id=id,
            no=no,
            reference_mto=reference_mto,
            pid_no=pid_no,
            line_no=line_no,
            isometric_drawing_no=isometric_drawing_no,
            iso_rev=iso_rev,
            iso_and_rev=iso_and_rev,
            spec=spec,
            comment=comment,
            no_contains=no_contains,
            reference_mto_contains=reference_mto_contains,
            pid_no_contains=pid_no_contains,
            line_no_contains=line_no_contains,
            isometric_drawing_no_contains=isometric_drawing_no_contains,
            iso_rev_contains=iso_rev_contains,
            iso_and_rev_contains=iso_and_rev_contains,
            spec_contains=spec_contains,
            comment_contains=comment_contains,
            mto_date=mto_date,
            mto_date_from=mto_date_from,
            mto_date_to=mto_date_to,
            quantity=quantity,
            quantity_min=quantity_min,
            quantity_max=quantity_max,
            required_area=required_area,
            required_area_min=required_area_min,
            required_area_max=required_area_max,
            required_iso=required_iso,
            required_iso_min=required_iso_min,
            required_iso_max=required_iso_max,
            location_id=location_id,
            area_id=area_id,
            area_2_id=area_2_id,
            area_2_desc_id=area_2_desc_id,
            stock_data_id=stock_data_id,
            uom_id=uom_id,
            created_by_id=created_by_id,
            location_name=location_name,
            area_name=area_name,
            area_2_name=area_2_name,
            area_2_desc_name=area_2_desc_name,
            stock_code=stock_code,
            uom_name=uom_name,
            project_id=project_id,
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return result
    except HTTPException as ex:
        raise ex
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )