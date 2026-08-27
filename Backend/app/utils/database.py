from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


import configs


SQLALCHEMY_DATABASE_URL_ASYNC = configs.SQLALCHEMY_DATABASE_URL_ASYNC

Base = declarative_base()

async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL_ASYNC,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600, # 1 hour
    echo=False,
    future=True
)


AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_async() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def get_db_context_async() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
