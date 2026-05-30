from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    db_schema: str

    postgres_user_context: str
    postgres_password_context: str
    db_schema_context: str

    sql_echo: bool

    GEMINI_API_KEY: str
    OPENROUTER_API_KEY: str
    
    class Config:
        env_file = ".env"
        extra="ignore"


settings = Settings()