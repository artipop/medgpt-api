from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    Field,
)


class Settings(BaseSettings):
    project_title: str = Field(alias="PROJECT_TITLE")
    fastapi_host: str = Field(alias="FASTAPI_HOST")
    fastapi_port: int = Field(alias="FASTAPI_PORT")
    
    model_config = SettingsConfigDict(
        env_file=".env-example"
    )

settings = Settings()