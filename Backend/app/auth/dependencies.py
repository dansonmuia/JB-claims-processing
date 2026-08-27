from fastapi import Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app import models as m
from app.utils.database import get_db_async

from . import oauth2_scheme
from .tokens import load_admin_from_access_token


async def get_current_admin(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db_async)
) -> m.Admin:
    admin = await load_admin_from_access_token(token, db)
    if admin is None or not admin.is_active:
        raise HTTPException(status_code=401, detail="Account disabled or not logged in")
    return admin
