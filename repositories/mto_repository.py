# repositories/mto_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, date
from fastapi import HTTPException

from models.common_model import (
    MtoModel, LocationModel, AreaModel, DescriptionModel,
    StockDataModel, UomModel
)
from models.user_model import UserModel



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


class FetchMTORepository:

    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id

    async def fetch_mto(
            self,
            # ID filters
            id: Optional[int] = None,
            # String exact filters
            no: Optional[str] = None,
            reference_mto: Optional[str] = None,
            pid_no: Optional[str] = None,
            line_no: Optional[str] = None,
            isometric_drawing_no: Optional[str] = None,
            iso_rev: Optional[str] = None,
            iso_and_rev: Optional[str] = None,
            spec: Optional[str] = None,
            comment: Optional[str] = None,
            # String partial filters
            no_contains: Optional[str] = None,
            reference_mto_contains: Optional[str] = None,
            pid_no_contains: Optional[str] = None,
            line_no_contains: Optional[str] = None,
            isometric_drawing_no_contains: Optional[str] = None,
            iso_rev_contains: Optional[str] = None,
            iso_and_rev_contains: Optional[str] = None,
            spec_contains: Optional[str] = None,
            comment_contains: Optional[str] = None,
            # Date filters
            mto_date: Optional[date] = None,
            mto_date_from: Optional[date] = None,
            mto_date_to: Optional[date] = None,
            # Numeric filters
            quantity: Optional[float] = None,
            quantity_min: Optional[float] = None,
            quantity_max: Optional[float] = None,
            required_area: Optional[float] = None,
            required_area_min: Optional[float] = None,
            required_area_max: Optional[float] = None,
            required_iso: Optional[float] = None,
            required_iso_min: Optional[float] = None,
            required_iso_max: Optional[float] = None,
            # Foreign Key filters
            location_id: Optional[int] = None,
            area_id: Optional[int] = None,
            area_2_id: Optional[int] = None,
            area_2_desc_id: Optional[int] = None,
            stock_data_id: Optional[int] = None,
            uom_id: Optional[int] = None,
            created_by_id: Optional[int] = None,
            # Relationship name filters
            location_name: Optional[str] = None,
            area_name: Optional[str] = None,
            area_2_name: Optional[str] = None,
            area_2_desc_name: Optional[str] = None,
            stock_code: Optional[str] = None,
            uom_name: Optional[str] = None,
            project_id: Optional[int] = None,
            # Pagination
            page: int = 1,
            limit: int = 50,
            # Sorting
            sort_by: str = "id",
            sort_order: str = "asc"
    ) -> Dict[str, Any]:

        # Get user information
        user_info = await GetUserInformation(
            self.db,
            self.user_id
        ).get_user_information()

        is_admin_or_manager = user_info['status_id'] in [1, 2]

        # Build base query
        query = select(MtoModel).options(
            selectinload(MtoModel.location),
            selectinload(MtoModel.area),
            selectinload(MtoModel.area_2),
            selectinload(MtoModel.area_2_desc),
            selectinload(MtoModel.stock_data),
            selectinload(MtoModel.uom),
            selectinload(MtoModel.created_by)
        )

        # APPLY PERMISSION FILTERS HERE (before other filters)
        if not is_admin_or_manager:
            # Regular user: only their project
            query = query.join(MtoModel.area).where(
                AreaModel.project_id == user_info['project_id']
            )
        elif project_id is not None:
            # Admin/Manager: can filter by specific project
            query = query.join(MtoModel.area).where(
                AreaModel.project_id == project_id
            )

        # Apply filters
        # ID filters
        if id is not None:
            query = query.where(MtoModel.id == id)

        # String exact filters
        if no is not None:
            query = query.where(MtoModel.no == no)
        if reference_mto is not None:
            query = query.where(MtoModel.reference_mto == reference_mto)
        if pid_no is not None:
            query = query.where(MtoModel.pid_no == pid_no)
        if line_no is not None:
            query = query.where(MtoModel.line_no == line_no)
        if isometric_drawing_no is not None:
            query = query.where(MtoModel.isometric_drawing_no == isometric_drawing_no)
        if iso_rev is not None:
            query = query.where(MtoModel.iso_rev == iso_rev)
        if iso_and_rev is not None:
            query = query.where(MtoModel.iso_and_rev == iso_and_rev)
        if spec is not None:
            query = query.where(MtoModel.spec == spec)
        if comment is not None:
            query = query.where(MtoModel.comment == comment)

        # String partial filters (case-insensitive)
        if no_contains is not None:
            query = query.where(MtoModel.no.ilike(f"%{no_contains}%"))
        if reference_mto_contains is not None:
            query = query.where(MtoModel.reference_mto.ilike(f"%{reference_mto_contains}%"))
        if pid_no_contains is not None:
            query = query.where(MtoModel.pid_no.ilike(f"%{pid_no_contains}%"))
        if line_no_contains is not None:
            query = query.where(MtoModel.line_no.ilike(f"%{line_no_contains}%"))
        if isometric_drawing_no_contains is not None:
            query = query.where(MtoModel.isometric_drawing_no.ilike(f"%{isometric_drawing_no_contains}%"))
        if iso_rev_contains is not None:
            query = query.where(MtoModel.iso_rev.ilike(f"%{iso_rev_contains}%"))
        if iso_and_rev_contains is not None:
            query = query.where(MtoModel.iso_and_rev.ilike(f"%{iso_and_rev_contains}%"))
        if spec_contains is not None:
            query = query.where(MtoModel.spec.ilike(f"%{spec_contains}%"))
        if comment_contains is not None:
            query = query.where(MtoModel.comment.ilike(f"%{comment_contains}%"))

        # Date filters
        if mto_date is not None:
            query = query.where(func.date(MtoModel.mto_date) == mto_date)
        if mto_date_from is not None:
            query = query.where(MtoModel.mto_date >= mto_date_from)
        if mto_date_to is not None:
            query = query.where(MtoModel.mto_date <= mto_date_to)

        # Numeric filters
        if quantity is not None:
            query = query.where(MtoModel.quantity == quantity)
        if quantity_min is not None:
            query = query.where(MtoModel.quantity >= quantity_min)
        if quantity_max is not None:
            query = query.where(MtoModel.quantity <= quantity_max)

        if required_area is not None:
            query = query.where(MtoModel.required_area == required_area)
        if required_area_min is not None:
            query = query.where(MtoModel.required_area >= required_area_min)
        if required_area_max is not None:
            query = query.where(MtoModel.required_area <= required_area_max)

        if required_iso is not None:
            query = query.where(MtoModel.required_iso == required_iso)
        if required_iso_min is not None:
            query = query.where(MtoModel.required_iso >= required_iso_min)
        if required_iso_max is not None:
            query = query.where(MtoModel.required_iso <= required_iso_max)

        # Foreign Key filters
        if location_id is not None:
            query = query.where(MtoModel.location_id == location_id)
        if area_id is not None:
            query = query.where(MtoModel.area_id == area_id)
        if area_2_id is not None:
            query = query.where(MtoModel.area_2_id == area_2_id)
        if area_2_desc_id is not None:
            query = query.where(MtoModel.area_2_desc_id == area_2_desc_id)
        if stock_data_id is not None:
            query = query.where(MtoModel.stock_data_id == stock_data_id)
        if uom_id is not None:
            query = query.where(MtoModel.uom_id == uom_id)
        if created_by_id is not None:
            query = query.where(MtoModel.created_by_id == created_by_id)

        # Relationship name filters
        if location_name is not None:
            query = query.join(MtoModel.location).where(
                LocationModel.name.ilike(f"%{location_name}%")
            )
        if area_name is not None:
            query = query.join(MtoModel.area).where(
                AreaModel.name.ilike(f"%{area_name}%")
            )
        if area_2_name is not None:
            query = query.join(MtoModel.area_2).where(
                AreaModel.name.ilike(f"%{area_2_name}%")
            )
        if area_2_desc_name is not None:
            query = query.join(MtoModel.area_2_desc).where(
                DescriptionModel.name.ilike(f"%{area_2_desc_name}%")
            )
        if stock_code is not None:
            query = query.join(MtoModel.stock_data).where(
                StockDataModel.stock_code.ilike(f"%{stock_code}%")
            )
        if uom_name is not None:
            query = query.join(MtoModel.uom).where(
                UomModel.name.ilike(f"%{uom_name}%")
            )

        # Get total count before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.db.scalar(count_query)

        if total_count == 0:
            return {
                "data": [],
                "pagination": {
                    "current_page": page,
                    "limit": limit,
                    "total_count": 0,
                    "total_pages": 0
                }
            }

        # Apply sorting
        sort_column = getattr(MtoModel, sort_by, MtoModel.id)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # Execute query
        result = await self.db.execute(query)
        mtos = result.scalars().all()

        # Format response
        formatted_mtos = []
        for mto in mtos:
            formatted_mtos.append(self._format_mto_response(mto))

        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

        return {
            "data": formatted_mtos,
            "pagination": {
                "current_page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages
            }
        }

    def _format_mto_response(self, mto: MtoModel) -> Dict[str, Any]:
        """Format MTO response with all relationships"""
        return {
            "id": mto.id,
            "no": mto.no,
            "reference_mto": mto.reference_mto,
            "mto_date": mto.mto_date.isoformat() if mto.mto_date else None,
            "pid_no": mto.pid_no,
            "line_no": mto.line_no,
            "isometric_drawing_no": mto.isometric_drawing_no,
            "iso_rev": mto.iso_rev,
            "iso_and_rev": mto.iso_and_rev,
            "spec": mto.spec,
            "quantity": mto.quantity,
            "required_area": mto.required_area,
            "required_iso": mto.required_iso,
            "comment": mto.comment,
            "iso_stock_kod": mto.iso_stock_kod,
            "created_at": mto.created_at.isoformat() if mto.created_at else None,
            "updated_at": mto.updated_at.isoformat() if mto.updated_at else None,
            # Location
            "location": {
                "id": mto.location.id,
                "name": mto.location.name,
                "project_id": mto.location.project_id
            } if mto.location else None,
            # Area
            "area": {
                "id": mto.area.id,
                "name": mto.area.name,
                "description": mto.area.description,
                "project_id": mto.area.project_id
            } if mto.area else None,
            # Area 2
            "area_2": {
                "id": mto.area_2.id,
                "name": mto.area_2.name,
                "description": mto.area_2.description,
                "project_id": mto.area_2.project_id
            } if mto.area_2 else None,
            # Area 2 Description
            "area_2_desc": {
                "id": mto.area_2_desc.id,
                "name": mto.area_2_desc.name
            } if mto.area_2_desc else None,
            # Stock Data
            "stock_data": {
                "id": mto.stock_data.id,
                "stock_code": mto.stock_data.stock_code,
                "alternative_id": mto.stock_data.alternative_id,
                "old_code": mto.stock_data.old_code,
                "comment": mto.stock_data.comment
            } if mto.stock_data else None,
            # UOM
            "uom": {
                "id": mto.uom.id,
                "name": mto.uom.name
            } if mto.uom else None,

        }