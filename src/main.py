import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from settings import settings
from common.logger import logger
from auth.router import router as auth_router
from google_auth.router import router as google_auth_router


app = FastAPI(
  title=settings.project_title
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

