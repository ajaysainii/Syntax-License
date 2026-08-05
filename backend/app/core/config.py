from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Syntax Licensing Platform"
    environment: str = "development"
    database_url: str | None = None
    db_engine: str = "mysql+pymysql"
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str = "syntax_licensing"
    db_user: str = "syntax_user"
    db_password: str = "change-me"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 12
    license_hmac_secret: str = "change-license-secret"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    admin_email: str = "admin@syntaxnation.com"
    admin_password: str = "ChangeThisNow123!"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.db_engine.startswith("sqlite"):
            return f"sqlite:///./{self.db_name}.db"
        return (
            f"{self.db_engine}://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
