# schemas/common_schema.py
from pydantic import BaseModel

class CreateAreaSchema(BaseModel):
    name: str
    description: str
    project_id: int

class CreateLocationSchema(BaseModel):
    name: str
    project_id: int

class CreateUomSchema(BaseModel):
    name: str

class CreateTypeSchema(BaseModel):
    name: str
    sub_name: str
    description: str
    material: str
    size_1: str
    size_2: str
    thickness_1: str
    thickness_2: str

class CreateStockSchema(BaseModel):
    stock_code: str
    alternative_id: str
    old_code: str
    comment: str
    type_id: int
    uom_id: int