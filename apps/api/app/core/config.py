from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./senus.db"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 12
    cors_origins: list[str] = ["http://localhost:3000"]
    allowed_ips: list[str] = []


settings = Settings()
