from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4


class PlainClientSchema(BaseModel):
    email: EmailStr
    document: str | int
    first_name: str
    sur_name: str

    class Config:
        from_attributes = True


class PostPutClientSchema(PlainClientSchema):
    password: str


class ReturnClientSchema(PlainClientSchema):
    id: UUID4


class LoginClientSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True
