from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import get_settings

settings = get_settings()

# Use an async engine; DATABASE_URL must be an async URL (e.g. sqlite+aiosqlite:///... or postgresql+asyncpg://...)
engine = create_async_engine(settings.DATABASE_URL, future=True)

# Async session factory
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

async def get_db():
    """Async DB session generator for dependency injection."""
    async with AsyncSessionLocal() as session:
        yield session