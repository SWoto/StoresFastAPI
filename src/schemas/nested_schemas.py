from typing import List
from pydantic import UUID4

from src.schemas.products import ProductSchemaWithoutStore, PlainProductSchema
from src.schemas.stores import ReturnStoreSchema, PlainStoreSchema

class CreateProductSchema(PlainProductSchema):
    store_id: UUID4

class ReturnProductSchema(ProductSchemaWithoutStore):
    store_id: UUID4

class ReturnFullProductSchema(ProductSchemaWithoutStore):
    store: PlainStoreSchema

class ReturnFullStoresSchema(ReturnStoreSchema):
    products: List[PlainProductSchema]