from typing import List, Optional
from pydantic import BaseModel, EmailStr, field_validator

class IndicatorMetadataResponse(BaseModel):
    id_indicator: int
    name: str
    description: Optional[str] = None
    units: Optional[str] = None
    units_desc: Optional[str] = None
    calculation: Optional[str] = None
    source: Optional[str] = None
    source_code: Optional[str] = None
    attributes: Optional[str] = None
    class Config:
        from_attributes = True

class IndicatorDataResponse(BaseModel):
    id_indicator: int
    name: str
    description: Optional[str] = None
    units: Optional[str] = None
    units_desc: Optional[str] = None
    source: Optional[str] = None
    attributes: Optional[str] = None
    timecode: Optional[str] = None
    value: Optional[float] = None
    geocode: Optional[str] = None
    distrito: Optional[str] = None
    concelho: Optional[str] = None
    freguesia: Optional[str] = None
    nuts1: Optional[str] = None
    nuts2: Optional[str] = None
    nuts3: Optional[str] = None
    calculation: Optional[str] = None
    source: Optional[str] = None
    source_code: Optional[str] = None
    attributes: Optional[str] = None
    class Config:
        from_attributes = True
        
    # Validador para convertir cualquier tipo a str en el campo 'timecode'
    @field_validator('timecode', mode='before')
    def convert_timecode_to_str(cls, v):
        if v is not None:
            return str(v)
        return v

class MetadataResponse(BaseModel):
    user_email: str
    consulted_at: str
    indicators: List[IndicatorMetadataResponse]

class DataResponse(BaseModel):
    user_email: str
    consulted_at: str
    indicators: List[IndicatorDataResponse]

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
