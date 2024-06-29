from fastapi import FastAPI

from src.core.configs import settings
from src.api.v1.api import api_router

app = FastAPI(debug=True, title="Stores FastAPI")
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload=True)
