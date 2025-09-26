import os
from sqladmin import Admin
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# common app dependencies
from admin import FilesView
from settings import settings
from common.logger import logger
# startup dependencies
from common.http_client import HttpClient
from google_auth.utils.id_provider_certs import IdentityProviderCerts
# routers
from native_auth.router import router as native_auth_router
from google_auth.router import router as google_auth_router
from common.auth.router import router as common_auth_router
from subs.router import router as subscription_router

from chat.router import router as chat_router
from database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    http_client = HttpClient()
    await http_client.init_session()
    await IdentityProviderCerts().renew_certs()
    # code above that line executes before app started
    yield
    # code below that line executes when app terminates
    await http_client.close_session()


app = FastAPI(
    title=settings.project_title,
    lifespan=lifespan,
    root_path='/api'
)

allowed_hosts = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
admin = Admin(app, engine=engine)
admin.add_view(FilesView)

app.include_router(native_auth_router)    
app.include_router(google_auth_router)
app.include_router(chat_router)
app.include_router(common_auth_router)
app.include_router(subscription_router)

# db_path = f"{settings.api_base_url}/api/static_files/{file.filename}"
static_dir = os.path.join(os.path.dirname(__file__), "chat", "static_files")
app.mount("/uploaded", StaticFiles(directory=static_dir), name="uploaded")
if __name__ == "__main__":
    
    logger.info("app started")
    uvicorn.run(
        app="main:app", 
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=True,
        proxy_headers=True
    )

