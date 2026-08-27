from datetime import datetime

from fastapi import Query
from pydantic import BaseModel, field_validator, ConfigDict


MAX_LIMIT = 150


class TimeStampSchemaMixin:
    created_at: datetime
    updated_at: datetime


class PaginationBase(BaseModel):
    offset: int = 0
    limit: int = 50


class PaginationIn(PaginationBase):
    offset: int = Query(0, ge=0)
    limit: int = Query(50, ge=1)

    @field_validator('limit')
    def validate_limit(cls, limit: int):
        return min(limit, MAX_LIMIT)


class PaginationOutMixin(PaginationBase):
    """
    To be inherited by the schema representing the response of a paginated endpoint.
    The inheriting schema should have a field named `items` of type `List[Model]`.
    """
    count: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginationObject:
    """
    A class whose instances are returned by the paginated endpoints.
    """
    def __init__(self, offset: int = 0, limit: int = 50, items: list = None, count: int = None):
        self.offset = offset
        self.limit = limit
        self.items = items
        self.count = count
