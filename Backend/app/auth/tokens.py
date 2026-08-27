import logging
from datetime import datetime, timezone, timedelta

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import configs
from app import models as m


JWT_ALGORITHM = "HS256"
SECRET_KEY = configs.JWT_SECRET
ACCESS_TOKEN_EXPIRY = configs.JWT_EXPIRY_HOURS * 60 * 60  # convert hours to seconds


async def generate_admin_access_token(admin: m.Admin):
    return jwt.encode(
        {
            "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=ACCESS_TOKEN_EXPIRY),
            'admin_id': str(admin.id)
        },
        SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


async def load_admin_from_access_token(token: str, db: AsyncSession) -> m.Admin | None:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        admin_id = data.get('admin_id')

        admin_q = select(m.Admin).where(m.Admin.id == admin_id)
        result =  await db.execute(admin_q)
        return result.scalar_one_or_none()

    except Exception as e:
        logging.error(f'Error decoding token: {e}')
        return None
