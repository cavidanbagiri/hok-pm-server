# schemas/common_schema.py
from pydantic import BaseModel
from typing import Optional


class CreateSubTypeSchema(BaseModel):
    name: str


class CreateSize1Schema(BaseModel):
    name: str


class CreateSize2Schema(BaseModel):
    name: str


class CreateMaterialSchema(BaseModel):
    name: str


class CreateDescriptionSchema(BaseModel):
    name: str


class CreateTypeSchema(BaseModel):
    subtype_id: int
    size1_id: int
    size2_id: Optional[int] = None
    material_id: int
    description_id: int
    thickness_1: Optional[str] = None
    thickness_2: Optional[str] = None


class CreateAreaSchema(BaseModel):
    name: str
    description: str
    project_id: int


class CreateLocationSchema(BaseModel):
    name: str
    project_id: int


class CreateUomSchema(BaseModel):
    name: str


class CreateStockSchema(BaseModel):
    stock_code: str
    alternative_id: Optional[str] = None
    old_code: Optional[str] = None
    comment: Optional[str] = None
    type_id: int
    uom_id: int