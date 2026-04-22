from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cultivos API"
    app_version: str = "0.1.0"
    env: str = "dev"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 10080

    api_v1_prefix: str = "/api/v1"
    cors_allow_origins: str = "*"

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "cultivos"
    mysql_password: str = "cultivos123"
    mysql_db: str = "cultivos"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )

    @property
    def cors_origins(self) -> list[str]:
        raw = self.cors_allow_origins.strip()
        if not raw:
            return []
        if raw == "*":
            return ["*"]
        return [item.strip() for item in raw.split(",") if item.strip()]


settings = Settings()
