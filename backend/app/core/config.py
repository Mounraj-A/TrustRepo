from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    APP_DESCRIPTION: str

    ENVIRONMENT: str

    HOST: str
    PORT: int

    DATABASE_URL: str
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD_BACKEND: str

    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore"
    )


settings = Settings()
