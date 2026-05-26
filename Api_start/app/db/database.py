from sqlalchemy.orm import sessionmaker
from app.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)


DATABASE_URL = (
    f"postgresql+asyncpg://{settings.postgres_user}:"
    f"{settings.postgres_password}@"
    f"{settings.postgres_host}:"
    f"{settings.postgres_port}/"
    f"{settings.postgres_db}"
    #postgresql://user:password@host:port/dbname    
)

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.sql_echo,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

AI_WRITER_URL = (
    f"postgresql+asyncpg://{settings.postgres_user_context}:"
    f"{settings.postgres_password_context}@"
    f"{settings.postgres_host}:"
    f"{settings.postgres_port}/"
    f"{settings.postgres_db}"
    #postgresql://user:password@host:port/dbname    
)


ai_writer_engine = create_async_engine(
    AI_WRITER_URL,
    echo=settings.sql_echo,
    pool_pre_ping=True,
)

AsyncSessionWriterContext = sessionmaker(
    bind=ai_writer_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def push_db_context():
    async with AsyncSessionWriterContext() as session:
        yield session
