# schemas/mto_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class MTOFilterSchema(BaseModel):
    # ID filters
    id: Optional[int] = None

    # String filters (exact match)
    no: Optional[str] = None
    reference_mto: Optional[str] = None
    pid_no: Optional[str] = None
    line_no: Optional[str] = None
    isometric_drawing_no: Optional[str] = None
    iso_rev: Optional[str] = None
    iso_and_rev: Optional[str] = None
    spec: Optional[str] = None
    comment: Optional[str] = None

    # String filters (partial match / contains)
    no_contains: Optional[str] = None
    reference_mto_contains: Optional[str] = None
    pid_no_contains: Optional[str] = None
    line_no_contains: Optional[str] = None
    isometric_drawing_no_contains: Optional[str] = None
    iso_rev_contains: Optional[str] = None
    iso_and_rev_contains: Optional[str] = None
    spec_contains: Optional[str] = None
    comment_contains: Optional[str] = None

    # Date filters
    mto_date: Optional[date] = None
    mto_date_from: Optional[date] = None
    mto_date_to: Optional[date] = None

    # Numeric filters
    quantity: Optional[float] = None
    quantity_min: Optional[float] = None
    quantity_max: Optional[float] = None
    required_area: Optional[float] = None
    required_area_min: Optional[float] = None
    required_area_max: Optional[float] = None
    required_iso: Optional[float] = None
    required_iso_min: Optional[float] = None
    required_iso_max: Optional[float] = None

    # Foreign Key filters
    location_id: Optional[int] = None
    area_id: Optional[int] = None
    area_2_id: Optional[int] = None
    area_2_desc_id: Optional[int] = None
    stock_data_id: Optional[int] = None
    uom_id: Optional[int] = None
    created_by_id: Optional[int] = None

    # Relationship name filters (partial match)
    location_name: Optional[str] = None
    area_name: Optional[str] = None
    area_2_name: Optional[str] = None
    area_2_desc_name: Optional[str] = None
    stock_code: Optional[str] = None
    uom_name: Optional[str] = None
    project_id: Optional[int] = None,
    # created_by_name: Optional[str] = None

    # Pagination
    page: Optional[int] = 1
    limit: Optional[int] = 50

    # Sorting
    sort_by: Optional[str] = "id"  # id, no, reference_mto, mto_date, quantity, created_at
    sort_order: Optional[str] = "asc"  # asc, desc