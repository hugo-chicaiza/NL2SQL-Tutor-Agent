from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    api_port: int
    
    class Config:
        env_file = ".env"


settings = Settings()