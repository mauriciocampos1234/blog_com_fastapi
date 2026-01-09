from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    # Defaults allow the project (and tests) to run even when no `.env` is present.
    # In production (e.g. Render), override via environment variables.
    database_url: str = Field(
        default="sqlite:///./app.db",
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        # Render (e alguns provedores) expõem Postgres como `postgres://...`, mas
        # os drivers/SQLAlchemy esperam `postgresql://...`.
        if value.startswith("postgres://"):
            return "postgresql://" + value.removeprefix("postgres://")
        return value
    environment: str = Field(
        default="development",
        validation_alias=AliasChoices("ENVIRONMENT", "environment"),
    )

    jwt_secret: str = Field(
        default="my-secret",
        validation_alias=AliasChoices("JWT_SECRET", "jwt_secret"),
    )
    jwt_algorithm: str = Field(
        default="HS256",
        validation_alias=AliasChoices("JWT_ALGORITHM", "jwt_algorithm"),
    )
    jwt_issuer: str = Field(
        default="curso-fastapi.com.br",
        validation_alias=AliasChoices("JWT_ISSUER", "jwt_issuer"),
    )
    jwt_audience: str = Field(
        default="curso-fastapi",
        validation_alias=AliasChoices("JWT_AUDIENCE", "jwt_audience"),
    )
    jwt_expires_minutes: int = Field(
        default=30,
        validation_alias=AliasChoices("JWT_EXPIRES_MINUTES", "jwt_expires_minutes"),
    )


settings = Settings()
