# schemas/common_schema.py
from pydantic import BaseModel, validator
from typing import Optional, List


######################################### Area Schema
class CreateAreaSchema(BaseModel):
    name: str
    description: str
    doc_no: str
    doc_rev: str
    say_iso_no: str
    project_id: int


class UpdateAreaSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    doc_no: Optional[str] = None
    doc_rev: Optional[str] = None
    say_iso_no: Optional[str] = None
    project_id: Optional[int] = None



######################################### Location Schema
class CreateLocationSchema(BaseModel):
    name: str
    project_id: int

class UpdateLocationSchema(BaseModel):
    name: Optional[str] = None
    project_id: Optional[int] = None



######################################### UOM Schema
class CreateUomSchema(BaseModel):
    name: str

class UpdateUomSchema(BaseModel):
    name: Optional[str] = None



######################################### Size1 Schema
class CreateSize1Schema(BaseModel):
    name: str

class UpdateSize1Schema(BaseModel):
    name: Optional[str] = None

# schemas/common_schema.py (add this)
class BulkCreateSize1Schema(BaseModel):
    items: List[CreateSize1Schema]



######################################### Size2 Schema
class CreateSize2Schema(BaseModel):
    name: str

class UpdateSize2Schema(BaseModel):
    name: Optional[str] = None

# schemas/common_schema.py (add this)
class BulkCreateSize2Schema(BaseModel):
    items: List[CreateSize2Schema]



######################################### Material Schema
class CreateMaterialSchema(BaseModel):
    name: str

class UpdateMaterialSchema(BaseModel):
    name: Optional[str] = None

class BulkCreateMaterialSchema(BaseModel):
    items: List[CreateMaterialSchema]



######################################### Description Schema
class CreateDescriptionSchema(BaseModel):
    name: str

class UpdateDescriptionSchema(BaseModel):
    name: Optional[str] = None

class BulkCreateDescriptionSchema(BaseModel):
    descriptions: List[CreateDescriptionSchema]

    @validator('descriptions')
    def validate_non_empty(cls, v):
        if not v:
            raise ValueError('Descriptions list cannot be empty')
        return v



######################################### Subtype Schema
class CreateSubTypeSchema(BaseModel):
    name: str

class BulkCreateSubTypeSchema(BaseModel):
    items: List[CreateSubTypeSchema]



######################################### Itemtypes Schema
class CreateTypesSchema(BaseModel):
    name: str

class UpdateSubTypeSchema(BaseModel):
    name: Optional[str] = None

class UpdateTypesSchema(BaseModel):
    name: Optional[str] = None




######################################### Type Schema
class CreateTypeSchema(BaseModel):
    type_id: int  # Changed from subtype_id to type_id
    subtype_id: int
    size1_id: int
    size2_id: Optional[int] = None
    material_id: int
    description_id: int
    thickness_1: Optional[str] = None
    thickness_2: Optional[str] = None


class UpdateTypeSchema(BaseModel):
    type_id: Optional[int] = None
    subtype_id: Optional[int] = None
    size1_id: Optional[int] = None
    size2_id: Optional[int] = None
    material_id: Optional[int] = None
    description_id: Optional[int] = None
    thickness_1: Optional[str] = None
    thickness_2: Optional[str] = None




######################################### Stock Schema
class CreateStockSchema(BaseModel):
    stock_code: str
    alternative_id: Optional[str] = None
    old_code: Optional[str] = None
    comment: Optional[str] = None
    type_id: int
    uom_id: int


class UpdateStockSchema(BaseModel):
    stock_code: Optional[str] = None
    alternative_id: Optional[str] = None
    old_code: Optional[str] = None
    comment: Optional[str] = None
    type_id: Optional[int] = None
    uom_id: Optional[int] = None