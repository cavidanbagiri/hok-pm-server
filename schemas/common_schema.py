# schemas/common_schema.py
from pydantic import BaseModel
from typing import Optional, List


class CreateSubTypeSchema(BaseModel):
    name: str

class BulkCreateSubTypeSchema(BaseModel):
    items: List[CreateSubTypeSchema]

class CreateSize1Schema(BaseModel):
    name: str

# schemas/common_schema.py (add this)
class BulkCreateSize1Schema(BaseModel):
    items: List[CreateSize1Schema]

class CreateSize2Schema(BaseModel):
    name: str

# schemas/common_schema.py (add this)
class BulkCreateSize2Schema(BaseModel):
    items: List[CreateSize2Schema]

class CreateMaterialSchema(BaseModel):
    name: str

# schemas/common_schema.py (add this)
class BulkCreateMaterialSchema(BaseModel):
    items: List[CreateMaterialSchema]

class CreateDescriptionSchema(BaseModel):
    name: str




# schemas/common_schema.py (add these new schemas)

class CreateTypesSchema(BaseModel):
    name: str


class CreateTypeSchema(BaseModel):
    type_id: int  # Changed from subtype_id to type_id
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
    doc_no: str
    doc_rev: str
    say_iso_no: str
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