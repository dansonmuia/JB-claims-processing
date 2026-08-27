"""
Idempotent data seeding, run once per container start (see entrypoint.sh),
after migrations have brought the schema up to date.

- The default superadmin is always ensured, so there's a way to log in.
- Demo customer/policy/claim rows are only added when SEED_DEMO_DATA=true,
  so a real deployment doesn't get sample data injected by accident.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import configs
from app import models as m
from app.utils.database import get_db_context_async

logging.basicConfig(level=logging.INFO)


async def seed_superadmin(db: AsyncSession) -> None:
    if not configs.DEFAULT_SUPERADMIN_EMAIL:
        logging.info('DEFAULT_SUPERADMIN_EMAIL not set, skipping superadmin seed')
        return

    email = configs.DEFAULT_SUPERADMIN_EMAIL.lower()
    result = await db.execute(select(m.Admin).where(m.Admin.email == email))
    if result.scalars().first() is not None:
        logging.info(f'Superadmin already exists, skipping: {email}')
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
    logging.info(f'Created default superadmin: {email}')


async def seed_demo_data(db: AsyncSession) -> None:
    result = await db.execute(select(m.Customer).limit(1))
    if result.scalars().first() is not None:
        logging.info('Demo data already present, skipping')
        return

    customer = m.Customer(
        msisdn='254700111222',
        email='jane.doe@example.com',
        first_name='Jane',
        last_name='Doe',
    )
    db.add(customer)
    await db.flush()

    policy = m.Policy(policy_number='POL-1001', customer_id=customer.id)
    db.add(policy)
    await db.flush()

    now = datetime.now(timezone.utc)
    db.add_all([
        m.Claim(
            claim_number='CLM-1001',
            policy_id=policy.id,
            claim_type=m.ClaimTypeEnum.MOTOR,
            claim_amount=45000,
            incident_date=now - timedelta(days=10),
            description='Rear-end collision on Thika Road',
            status=m.ClaimStatusEnum.SUBMITTED,
        ),
        m.Claim(
            claim_number='CLM-1002',
            policy_id=policy.id,
            claim_type=m.ClaimTypeEnum.HEALTH,
            claim_amount=12500,
            incident_date=now - timedelta(days=30),
            description='Outpatient treatment',
            status=m.ClaimStatusEnum.UNDER_REVIEW,
        ),
    ])
    await db.commit()
    logging.info('Seeded demo customer, policy, and claims')


async def main() -> None:
    async with get_db_context_async() as db:
        await seed_superadmin(db)
        if configs.SEED_DEMO_DATA:
            await seed_demo_data(db)


if __name__ == '__main__':
    asyncio.run(main())
