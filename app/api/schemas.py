from typing import Optional
from pydantic import BaseModel, EmailStr

class Indicator_metadata_response(BaseModel):
    id_indicator: str
    name: str
    description: bool = True
    units_description: Optional[int] = None
    calculation: int
    source: str
    source_code: str
    attributes: str

    class Config:
        from_attributes = True

class User_Class(BaseModel):
    email: EmailStr
    password: str









