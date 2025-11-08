import asyncio
import pytest
from typing import Any, AsyncGenerator, Dict
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.core.database import Base
from app.main import app
from app.core.security import create_access_token, get_password_hash
from app.models.users import User

settings = get_settings()

# Type alias to avoid SQLAlchemy typing issues
AsyncSessionGen = AsyncGenerator[AsyncSession, None]

# Create test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db(event_loop) -> AsyncSessionGen:
    """Create a test database session."""
    engine = create_async_engine(
        TEST_SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()
    
    await engine.dispose()

@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    from app.core.database import get_db

    async def override_get_db():
        try:
            yield db
        finally:
            await db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
async def auth_headers(db: AsyncSession) -> Dict[str, str]:
    """Create authentication headers with a test token."""
    
    # Create test user
    test_user = User(
        username="testuser",
        email="test@example.com",
        is_active=True
    )
    test_user.set_password("testpass123")
    db.add(test_user)
    await db.commit()
    await db.refresh(test_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": test_user.username})
    
    # Create a session record so dependency check passes
    from app.models.sessions import Session as UserSession
    session = UserSession(
        user_id=test_user.id,
        device_name="test-client",
        session_token=access_token,
        ip_address="127.0.0.1",
        user_agent="test-agent"
    )
    db.add(session)
    await db.commit()

    return {"Authorization": f"Bearer {access_token}"}