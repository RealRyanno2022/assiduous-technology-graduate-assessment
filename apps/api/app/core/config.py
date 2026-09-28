from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# apps/api -> repo root locally; resolves to a nonexistent /.env inside the container, which is ignored
_REPO_ROOT_ENV = Path(__file__).resolve().parents[2].parent.parent / ".env"


class Settings(BaseSettings):
    # repo-root .env first, then a cwd-local .env overrides it
    model_config = SettingsConfigDict(env_file=(_REPO_ROOT_ENV, ".env"), extra="ignore")

    database_url: str = "sqlite:///./senus.db"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 12
    cors_origins: list[str] = ["http://localhost:3000"]
    allowed_ips: list[str] = []


settings = Settings()
