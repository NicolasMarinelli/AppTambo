from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://cami:cami@db:5432/cami"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 8

    default_admin_username: str = "admin"
    default_admin_password: str = "admin123"

    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
