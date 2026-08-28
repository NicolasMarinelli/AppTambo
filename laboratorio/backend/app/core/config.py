from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Misma base de datos que tambo ("cami"), rol propio de laboratorio.
    # Ver .env.example para el detalle de permisos.
    database_url: str = "postgresql+psycopg2://laboratorio:laboratorio@db:5432/cami"

    # Debe coincidir exactamente con tambo/backend/.env (JWT_SECRET_KEY /
    # ALGORITHM) para que los tokens sean intercambiables entre las dos apps.
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 8

    cors_origins: list[str] = ["http://localhost:5175"]

    anthropic_api_key: str = ""
    ai_model: str = "claude-haiku-4-5-20251001"

    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""


settings = Settings()
