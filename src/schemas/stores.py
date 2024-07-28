from pydantic import BaseModel, UUID4, field_validator


class PlainStoreSchema(BaseModel):
    name: str
    description: str | None
    address: str

    model_config = dict(from_attributes=True)
    
    @field_validator("description", mode='after')
    def transform_caps_to_lower(cls, value) -> str:
        return value.lower()
    
    @field_validator("name", "address", mode='after')
    def transform_str_to_first_caps(cls, value):
        return value.title()
    
class ReturnStoreSchema(PlainStoreSchema):
    id: UUID4
