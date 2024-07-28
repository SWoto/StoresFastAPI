from pydantic import BaseModel, UUID4, field_validator
from decimal import Decimal

class PlainProductSchema(BaseModel):
    name: str
    description: str | None
    price: Decimal

    model_config = dict(from_attributes=True)
    
    @field_validator("description", mode='after')
    def transform_caps_to_lower(cls, value) -> str:
        return value.lower()
    
    @field_validator("name", mode='after')
    def transform_str_to_first_caps(cls, value):
        return value.title()
    
class ProductSchemaWithoutStore(PlainProductSchema):
    id: UUID4
