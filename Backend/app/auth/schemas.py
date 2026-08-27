from uuid import UUID

from pydantic import BaseModel, field_validator


class EmailLowercaseMixin(BaseModel):
    @field_validator("email", check_fields=False)
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class AuthSchema(EmailLowercaseMixin):
    email: str
    password: str


class EmailStrSchema(EmailLowercaseMixin):
    email: str


class TokenOutSchema(BaseModel):
    token: str


class MessageOutSchema(BaseModel):
    message: str


class AdminMinimalSchemaOut(BaseModel):
    id: UUID
    name: str
    email: str
    msisdn: str
    role: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str
    admin: AdminMinimalSchemaOut
