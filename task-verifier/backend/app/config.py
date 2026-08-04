from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    ANTHROPIC_API_KEY: str
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173"
    ADMIN_API_KEY: str = "cambiar-en-produccion"
    CREDITOS_BASICO: int = 10
    CREDITOS_PLUS: int = 1000
    CREDITOS_PREMIUM: int = 5000
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""


    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # ignora POSTGRES_USER, POSTGRES_DB, etc.
    }


settings = Settings()