import enum
import uuid

from passlib.context import CryptContext
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    func,
    Enum,
    ForeignKey,
    Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.utils.database import Base


class TimeStampMixin:
    created_at = Column(DateTime(timezone=True), index=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), index=True, server_default=func.now(), onupdate=func.now())


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class Admin(Base, TimeStampMixin):
    __tablename__ = 'admins'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(64), nullable=False, unique=True, index=True)
    email = Column(String(128), nullable=False, unique=True, index=True)
    msisdn = Column(String(15), nullable=False, unique=True, index=True)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean(), default=True, nullable=False)
    role = Column(String(32), nullable=False, default='admin')

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, raw_password: str):
        self.password_hash = pwd_context.hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return pwd_context.verify(raw_password, self.password_hash)

    def __str__(self):
        return f'<Admin (id={self.id} name={self.name})'


class Customer(Base, TimeStampMixin):
    __tablename__ = 'customers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    msisdn = Column(String(15), nullable=False, unique=True, index=True)
    email = Column(String(128), nullable=True, unique=True, index=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    other_names = Column(String(128), nullable=True)
    is_active = Column(Boolean(), default=True, nullable=False)

    def __str__(self):
        return f'<Customer (id={self.id} msisdn={self.msisdn})'


class Policy(Base, TimeStampMixin):
    __tablename__ = 'policies'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_number = Column(String(64), nullable=False, unique=True, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    is_active = Column(Boolean(), default=True, nullable=False)

    customer = relationship('Customer', backref='policies')

    def __str__(self):
        return f'<Policy (id={self.id} policy_number={self.policy_number})'


class ClaimTypeEnum(enum.Enum):
    MOTOR = 'MOTOR'
    HEALTH = 'HEALTH'
    TRAVEL = 'TRAVEL'
    PROPERTY = 'PROPERTY'
    OTHER = 'OTHER'


class ClaimStatusEnum(enum.Enum):
    SUBMITTED = 'SUBMITTED'
    UNDER_REVIEW = 'UNDER_REVIEW'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    PAID = 'PAID'


class Claim(Base, TimeStampMixin):
    __tablename__ = 'claims'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_number = Column(String(64), nullable=False, unique=True, index=True)
    policy_id = Column(UUID(as_uuid=True), ForeignKey('policies.id'), nullable=False, index=True)
    claim_type = Column(Enum(ClaimTypeEnum), nullable=False, index=True)
    claim_amount = Column(Numeric(precision=12, scale=2), nullable=False)
    incident_date = Column(DateTime(timezone=True), nullable=False, index=True)
    description = Column(Text(), nullable=True)
    status = Column(Enum(ClaimStatusEnum), nullable=False, index=True, default=ClaimStatusEnum.SUBMITTED)

    policy = relationship('Policy', backref='claims')

    def __str__(self):
        return f'<Claim (id={self.id} claim_number={self.claim_number})'


class AuditLog(Base, TimeStampMixin):
    __tablename__ = 'audit_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey('admins.id'), nullable=False, index=True)
    action = Column(String(128), nullable=False)
    details = Column(Text(), nullable=True)

    admin = relationship('Admin', backref='audit_logs')

    def __str__(self):
        return f'<AuditLog (id={self.id} action={self.action})'
