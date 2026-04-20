from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cultivos API"
    env: str = "dev"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60

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


settings = Settings()
