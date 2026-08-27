import logging
from uuid import UUID

from fastapi import Depends, HTTPException

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app import models as m
from app.utils.database import get_db_async
from app.utils.schemas import PaginationIn, PaginationObject
from app.auth import dependencies as auth_deps

from . import router, schemas


@router.get('/', response_model=schemas.ClaimPaginationOut)
async def list_claims(
        pagination: PaginationIn = Depends(),
        db: AsyncSession = Depends(get_db_async),
        current_admin: m.Admin = Depends(auth_deps.get_current_admin),
        claim_number: str | None = None,
        policy_id: UUID | None = None
):
    logging.info(f'List claims request by admin id: {current_admin.id}', extra={'admin_id': current_admin.id})
    base_query = select(m.Claim)
    if claim_number:
        base_query = base_query.where(m.Claim.claim_number == claim_number)
    if policy_id:
        base_query = base_query.where(m.Claim.policy_id == policy_id)

    paged_query = base_query.order_by(m.Claim.created_at.desc()).limit(pagination.limit).offset(pagination.offset)
    claims_result = await db.execute(paged_query)
    claims = claims_result.scalars().all()

    count_query = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_query)
    count = count_result.scalar_one()

    return PaginationObject(
        items=claims,
        count=count,
        limit=pagination.limit,
        offset=pagination.offset
    )


@router.post('/', response_model=schemas.ClaimOutSchema)
async def create_claim(
        claim_in: schemas.ClaimCreateSchema,
        db: AsyncSession = Depends(get_db_async),
        current_admin: m.Admin = Depends(auth_deps.get_current_admin)
):
    logging.info(f'Create claim request by admin id: {current_admin.id}', extra={'admin_id': current_admin.id})
    new_claim = m.Claim(**claim_in.model_dump())
    db.add(new_claim)
    await db.commit()
    await db.refresh(new_claim)
    return new_claim


@router.get('/{claim_id}', response_model=schemas.ClaimOutSchema)
async def get_claim_details(
        claim_id: UUID,
        db: AsyncSession = Depends(get_db_async),
        current_admin: m.Admin = Depends(auth_deps.get_current_admin)
):
    logging.info(
        f'Get claim(id:{claim_id}) details request by admin id: {current_admin.id}',
        extra={'admin_id': current_admin.id}
    )
    q = select(m.Claim).where(m.Claim.id == claim_id)
    result = await db.execute(q)
    claim: m.Claim | None = result.scalars().first()
    if not claim:
        raise HTTPException(status_code=404, detail='Claim not found')
    return claim


@router.patch('/{claim_id}', response_model=schemas.ClaimOutSchema)
async def update_claim(
        claim_id: UUID,
        claim_in: schemas.ClaimUpdateSchema,
        db: AsyncSession = Depends(get_db_async),
        current_admin: m.Admin = Depends(auth_deps.get_current_admin)
):
    logging.info(
        f'Update claim(id:{claim_id}) request by admin id: {current_admin.id}',
        extra={'admin_id': current_admin.id}
    )

    q = select(m.Claim).where(m.Claim.id == claim_id).with_for_update()
    result = await db.execute(q)
    claim: m.Claim | None = result.scalars().first()
    if not claim:
        raise HTTPException(status_code=404, detail='Claim not found')

    next_allowed_status = None
    if claim.status == m.ClaimStatusEnum.SUBMITTED:
        next_allowed_status = m.ClaimStatusEnum.UNDER_REVIEW
    elif claim.status == m.ClaimStatusEnum.UNDER_REVIEW:
        next_allowed_status = [m.ClaimStatusEnum.APPROVED, m.ClaimStatusEnum.REJECTED]
    elif claim.status in [m.ClaimStatusEnum.APPROVED, m.ClaimStatusEnum.REJECTED]:
        next_allowed_status = m.ClaimStatusEnum.PAID

    if claim_in.status and claim_in.status != claim.status:
        if isinstance(next_allowed_status, list):
            if claim_in.status not in next_allowed_status:
                raise HTTPException(status_code=400, detail=f'Invalid status transition from {claim.status} to {claim_in.status}')
        else:
            if claim_in.status != next_allowed_status:
                raise HTTPException(status_code=400, detail=f'Invalid status transition from {claim.status} to {claim_in.status}')

    for field, value in claim_in.model_dump(exclude_unset=True).items():
        setattr(claim, field, value)

    db.add(claim)
    await db.commit()
    await db.refresh(claim)
    return claim
