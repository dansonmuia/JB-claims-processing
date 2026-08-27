import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import models as m
from app.utils.database import get_db_async

from . import router, schemas
from .tokens import generate_admin_access_token


async def login_for_token(email: str, password: str, db: AsyncSession):
    email = email.lower()
    q = select(m.Admin).where(m.Admin.email == email)
    result = await db.execute(q)
    admin: m.Admin = result.scalars().first()

    if admin is None:
        logging.error(f'email account not found {email}')
        raise HTTPException(status_code=401, detail='Invalid credentials')

    if not admin.check_password(password):
        logging.error(f'Invalid password for {email}')
        raise HTTPException(status_code=401, detail='Invalid credentials')

    if not admin.is_active:
        logging.error(f'User disabled. Cannot login: {email}')
        raise HTTPException(status_code=400, detail='Account is disabled. Contact support.')

    token = await generate_admin_access_token(admin)

    return {
        "access_token": token,
        "token_type": "bearer",
        "admin": {
            "id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "msisdn": admin.msisdn,
            "role": admin.role
        }
    }, admin


@router.post('/login-for-token', response_model=schemas.AdminLoginResponse)
async def login_for_token(credentials: schemas.AuthSchema, db: AsyncSession = Depends(get_db_async)):
    response, admin = await login_for_token(credentials.email, credentials.password, db)
    logging.info(f'Login successful for: {credentials.email}', extra={'admin_id': admin.id})

    return response


# For logging in while on the swagger docs
@router.post('/docs-login-here', response_model=schemas.AdminLoginResponse, include_in_schema=False)
async def login_from_docs(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db_async)):
    logging.info(f'Login from docs attempt for: {form_data.username}')
    response, admin = await login_for_token(form_data.username, form_data.password, db)
    logging.info(f'Login from docs successful for: {form_data.username}', extra={'admin_id': admin.id})

    return response
