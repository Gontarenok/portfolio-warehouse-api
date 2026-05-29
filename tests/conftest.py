from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.password import hash_password
from app.db import Base, get_db
from app.main import app
from app.models.enums import UserRole
from app.models.user import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.commit()


@pytest.fixture
async def client(db_engine) -> AsyncGenerator[AsyncClient, None]:
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        email="admin@test.com",
        password_hash=hash_password("adminpass123"),
        role=UserRole.admin,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def manager_user(db_session: AsyncSession) -> User:
    user = User(
        email="manager@test.com",
        password_hash=hash_password("managerpass123"),
        role=UserRole.manager,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def admin_token(client: AsyncClient, admin_user: User) -> str:
    resp = await client.post(
        "/auth/login",
        json={"email": "admin@test.com", "password": "adminpass123"},
    )
    return resp.json()["access_token"]


@pytest.fixture
async def manager_token(client: AsyncClient, manager_user: User) -> str:
    resp = await client.post(
        "/auth/login",
        json={"email": "manager@test.com", "password": "managerpass123"},
    )
    return resp.json()["access_token"]


@pytest.fixture
def auth_header():
    def _header(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    return _header
