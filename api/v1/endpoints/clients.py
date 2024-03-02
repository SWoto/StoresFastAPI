import uuid
from fastapi import APIRouter, status

from schemas.clients import PostPutClientSchema, ReturnClientSchema

router = APIRouter()


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ReturnClientSchema)
async def post_client(client: PostPutClientSchema):
    post_data = client.model_dump()
    post_data['id'] = uuid.uuid4()
    return post_data
