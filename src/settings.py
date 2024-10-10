from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    Field,
)


class Settings(BaseSettings):
    project_title: str = Field(alias="PROJECT_TITLE")
    fastapi_host: str = Field(alias="FASTAPI_HOST")
    fastapi_port: int = Field(alias="FASTAPI_PORT")

    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_host: str = Field(alias="POSTGRES_HOST")
    postgres_port: str = Field(alias="POSTGRES_PORT")
    
    google_client_id: str = Field(alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(alias="GOOGLE_CLIENT_SECRET")

    @property
    def db_url(self) -> str:
        scheme = "postgresql+asyncpg" 
        return (
            f"{scheme}://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )
    
    model_config = SettingsConfigDict(
        env_file=".env-example"
    )

settings = Settings()