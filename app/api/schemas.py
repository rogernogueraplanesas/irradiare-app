from typing import Optional
from pydantic import BaseModel, EmailStr

class IndicatorMetadataResponse(BaseModel):
    id_indicator: int
    name: str
    description: str
    units: str
    units_descr: str
    calculation: str
    source: str
    source_code: str
    attributes: Optional[str] = None
    class Config:
        from_attributes = True


class User_Class(BaseModel):
    email: EmailStr
    password: str


class User_Response(BaseModel):
    email: EmailStr
    class Config:
        from_attributes = True

class Login_Class(BaseModel):
    email: EmailStr
    password: str
