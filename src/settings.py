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
    google_token_url: str = Field(alias="GOOGLE_TOKEN_URL")
    google_tokeninfo_url: str = Field(alias="GOOGLE_TOKENINFO_URL")
    google_userinfo_url: str = Field(alias="GOOGLE_USERINFO_URL")
    google_authorization_url: str = Field(alias="GOOGLE_AUTHORIZATION_URL")
    google_certs_url: str = Field(alias="GOOGLE_CERTS_URL")
    google_revoke_url: str = Field(alias="GOOGLE_REVOKE_URL")
    certs_issuer: str = Field(alias="CERTS_ISSUER")
    redirect_google_to_uri: str = Field(alias="REDIRECT_GOOGLE_TO_URI")

    jwt_signing_key: str = Field(alias="JWT_SIGNING_KEY")
    jwt_encoding_algo: str = Field(alias="JWT_ENCODING_ALGORITHM")


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