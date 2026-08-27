"""
Integration tests run against a real Postgres database (the models use
Postgres-specific column types, e.g. sqlalchemy.dialects.postgresql.UUID,
which aren't portable to SQLite). Point POSTGRES_* at a throwaway database -
see the "Running tests" section of the README for how to start one.

Schema is created directly from the SQLAlchemy models (Base.metadata.create_all)
rather than via Alembic, so the suite doesn't depend on migration history and
stays fast to set up/tear down. Each test runs inside its own transaction that
is rolled back afterwards, so tests don't leak data into one another.
"""
import os
import uuid

os.environ.setdefault('POSTGRES_DB', 'jbclaims_test')
os.environ.setdefault('POSTGRES_USER', 'jbclaims')
os.environ.setdefault('POSTGRES_PASSWORD', 'changeme')
os.environ.setdefault('POSTGRES_HOST', 'localhost')
os.environ.setdefault('POSTGRES_PORT', '5432')
os.environ.setdefault('JWT_SECRET', 'test-secret')
os.environ.setdefault(
    'PORTAL_API_LOG_FILE',
    os.path.join(os.path.dirname(__file__), '.test_portal_api.log'),
)

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import models as m
from app.utils.database import Base, async_engine, get_db_async
from main import app

TEST_ADMIN_PASSWORD = "TestPassword123!"


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _schema():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await async_engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    connection = await async_engine.connect()
    outer_transaction = await connection.begin()
    session = AsyncSession(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)

    yield session

    await session.close()
    await outer_transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture
async def client(db_session):
    async def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db_async] = _get_db_override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin(db_session):
    admin = m.Admin(
        name="Test Admin",
        email=f"admin-{uuid.uuid4().hex[:8]}@example.com",
        msisdn=f"2547{uuid.uuid4().int % 10**8:08d}",
        role="admin",
    )
    admin.password = TEST_ADMIN_PASSWORD
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def auth_headers(client, admin):
    response = await client.post(
        "/api/auth/login-for-token",
        json={"email": admin.email, "password": TEST_ADMIN_PASSWORD},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def policy(db_session):
    customer = m.Customer(
        msisdn=f"2547{uuid.uuid4().int % 10**8:08d}",
        email=f"customer-{uuid.uuid4().hex[:8]}@example.com",
        first_name="Jane",
        last_name="Doe",
    )
    db_session.add(customer)
    await db_session.flush()

    policy = m.Policy(policy_number=f"POL-{uuid.uuid4().hex[:8]}", customer_id=customer.id)
    db_session.add(policy)
    await db_session.commit()
    await db_session.refresh(policy)
    return policy
