import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from settings import settings
from common.logger import logger
from auth.router import router as auth_router
from google_auth.router import router as google_auth_router
from google_auth.dependencies import get_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    http_cleint = get_http_client()
    await http_cleint.init_session()
    yield
    await http_cleint.close_session()


app = FastAPI(
    title=settings.project_title,
    lifespan=lifespan
)

allowed_hosts = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(google_auth_router)


if __name__ == "__main__":
    logger.info("app started")
    
    uvicorn.run(
        app="main:app", 
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=True
    )

