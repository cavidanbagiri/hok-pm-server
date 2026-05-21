
from pydantic import BaseModel

class CreateProjectSchema(BaseModel):
    name: str
    country: str
    code: str
