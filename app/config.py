from pydantic import BaseSettings

class Settings(BaseSettings):
    base_url: str
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    access_secret_key: str
    refresh_secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()