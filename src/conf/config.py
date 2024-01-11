import pathlib
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PG_DB: str = "name_database"
    PG_USER: str = "user_database"
    PG_PASSWORD: str = '123456'
    PG_DOMAIN: str = "localhost"
    PG_PORT: int = 5432

    DB_URL: str = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_DOMAIN}:{PG_PORT}/{PG_DB}"

    SECRET_KEY_JWT: str = "secret_key_jwt"
    ALGORITHM_JWT: str = "HS256"

    MAIL_USERNAME: str = "example@meta.ua"
    MAIL_PASSWORD: str = "secretPassword"
    MAIL_FROM: str = "example@meta.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"

    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: int = 123456

    CLOUDINARY_NAME: str = "cloud_name"
    CLOUDINARY_API_KEY: int = 123456
    CLOUDINARY_API_SECRET: str = "api_secret"

    model_config = SettingsConfigDict(env_file='.env', extra='ignore', env_file_encoding='utf-8')


dot_env_file = pathlib.Path(__file__).parent.parent.parent / '.env'
config = Settings(_env_file=dot_env_file)