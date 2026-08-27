from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

import configs
from app.utils.logger import logger
from app.utils.database import Base, async_engine, get_db_context_async
from app import auth, claims
from app import models as m


async def seed_default_superadmin():
    if not configs.DEFAULT_SUPERADMIN_EMAIL:
        return

    email = configs.DEFAULT_SUPERADMIN_EMAIL.lower()
    async with get_db_context_async() as db:
        result = await db.execute(select(m.Admin).where(m.Admin.email == email))
        if result.scalars().first() is not None:
            return

        admin = m.Admin(
            name=configs.DEFAULT_SUPERADMIN_NAME,
            email=email,
            msisdn=configs.DEFAULT_SUPERADMIN_MSISDN,
            role='superadmin',
        )
        admin.password = configs.DEFAULT_SUPERADMIN_PASSWORD
        db.add(admin)
        await db.commit()
        logger.info(f'Created default superadmin: {email}')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # No migration tooling (e.g. Alembic) is set up yet, so tables are created
    # from the models on startup. See README "Assumptions and Omissions".
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_default_superadmin()

    yield


logger.info("Starting the Claims Portal API application")


app = FastAPI(title='Jubilee Portal API', lifespan=lifespan)


app.include_router(auth.router, tags=["Auth"], prefix="/api/auth")
app.include_router(claims.router, tags=["Claims"], prefix="/api/claims")
