from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app import models
from app.utils.schemas import PaginationOutMixin


class ClaimBaseSchema(BaseModel):
    claim_number: str
    policy_id: str
    claim_type: models.ClaimTypeEnum
    claim_amount: float
    incident_date: datetime
    description: str | None = None


class ClaimCreateSchema(ClaimBaseSchema):
    ...


class ClaimUpdateSchema(BaseModel):
    claim_amount: float
    incident_date: datetime
    description: str | None = None
    status: models.ClaimStatusEnum


class ClaimOutSchema(ClaimBaseSchema):
    id: str
    status: models.ClaimStatusEnum

    model_config = ConfigDict(from_attributes=True)


class ClaimPaginationOut(PaginationOutMixin):
    items: list[ClaimOutSchema] = []
