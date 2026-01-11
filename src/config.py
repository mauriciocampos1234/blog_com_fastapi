# Configuração central do projeto (Settings).
#
# Este módulo usa `pydantic-settings` para ler variáveis de ambiente e/ou `.env`.
#
# Regras importantes:
# - Em produção (Render), as configs vêm do painel de env vars.
# - Em desenvolvimento/testes, há valores padrão para a API subir sem `.env`.

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Carrega e valida as configurações do app.
    #
    # `model_config` define, por exemplo:
    # - qual arquivo `.env` ler
    # - como lidar com variáveis extras
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    # Defaults allow the project (and tests) to run even when no `.env` is present.
    # In production (e.g. Render), override via environment variables.
    database_url: str = Field(
        # URL de conexão com o banco.
        # - SQLite (default) é ótimo para rodar local rápido.
        # - Em produção, tipicamente será Postgres.
        default="sqlite:///./app.db",
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        # Normaliza a URL do banco para compatibilidade.
        #
        # Render (e alguns provedores) expõem Postgres como `postgres://...`, mas
        # drivers/SQLAlchemy normalmente esperam `postgresql://...`.

        # Se a URL começar com postgres://, trocamos para postgresql://.
        if value.startswith("postgres://"):
            # Remove o prefixo antigo e adiciona o prefixo esperado.
            return "postgresql://" + value.removeprefix("postgres://")
        # Se não precisar normalizar, devolve como veio.
        return value
    environment: str = Field(
        # Ambiente lógico do app. Usado para habilitar comportamentos de dev.
        default="development",
        validation_alias=AliasChoices("ENVIRONMENT", "environment"),
    )

    jwt_secret: str = Field(
        # Segredo de assinatura do JWT.
        # Em produção, use um valor forte e não comite no Git.
        default="my-secret",
        validation_alias=AliasChoices("JWT_SECRET", "jwt_secret"),
    )
    jwt_algorithm: str = Field(
        # Algoritmo de assinatura do JWT (HS256 = HMAC + SHA-256).
        default="HS256",
        validation_alias=AliasChoices("JWT_ALGORITHM", "jwt_algorithm"),
    )
    jwt_issuer: str = Field(
        # `iss` (issuer): identifica quem emitiu o token.
        default="curso-fastapi.com.br",
        validation_alias=AliasChoices("JWT_ISSUER", "jwt_issuer"),
    )
    jwt_audience: str = Field(
        # `aud` (audience): para quem o token foi emitido.
        default="curso-fastapi",
        validation_alias=AliasChoices("JWT_AUDIENCE", "jwt_audience"),
    )
    jwt_expires_minutes: int = Field(
        # Tempo de vida do token em minutos.
        default=30,
        validation_alias=AliasChoices("JWT_EXPIRES_MINUTES", "jwt_expires_minutes"),
    )


settings = Settings()

