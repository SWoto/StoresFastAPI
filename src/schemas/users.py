from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4


class PlainUserSchema(BaseModel):
    email: EmailStr
    document: str | int
    first_name: str
    sur_name: str
    admin: bool

    model_config = dict(from_attributes=True)


class PostPutUserSchema(PlainUserSchema):
    password: str


class ReturnUserSchema(PlainUserSchema):
    id: UUID4


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str

    model_config = dict(from_attributes=True)
