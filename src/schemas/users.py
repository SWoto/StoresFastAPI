from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, field_validator


class PlainUserSchema(BaseModel):
    email: EmailStr
    document: str | int
    first_name: str
    sur_name: str
    role: str

    model_config = dict(from_attributes=True)

    @field_validator("document", mode='before')
    def transform_id_to_str(cls, value) -> str:
        return str(value)
    
    @field_validator("role", mode='after')
    def transform_caps_to_lower(cls, value) -> str:
        return value.lower()
    
    @field_validator("first_name", "sur_name", mode='after')
    def transform_str_to_first_caps(cls, value):
        return value.title()

class PostPutUserSchema(PlainUserSchema):
    password: str


class ReturnUserSchema(PlainUserSchema):
    id: UUID4
    confirmed: bool


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str

    model_config = dict(from_attributes=True)
