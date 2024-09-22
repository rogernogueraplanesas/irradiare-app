from typing import List, Optional
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

class IndicatorResponse(BaseModel):
    user_email: str
    consulted_at: str
    indicators: List[IndicatorMetadataResponse]

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

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int
