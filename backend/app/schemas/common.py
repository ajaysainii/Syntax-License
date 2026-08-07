from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.services.products import normalize_product_name


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AdminRead(ORMModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime


class AdminUpdate(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True
    password: str | None = None


class AdminListResponse(BaseModel):
    items: list[AdminRead]
    total: int


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    company: str | None = None
    notes: str | None = None


class CustomerRead(ORMModel):
    id: str
    name: str
    email: EmailStr
    company: str | None = None
    notes: str | None = None
    created_at: datetime


class CustomerListResponse(BaseModel):
    items: list[CustomerRead]
    total: int


class UserCreate(BaseModel):
    customer_id: str
    full_name: str
    email: EmailStr
    role: str = "user"


class UserUpdate(BaseModel):
    customer_id: str
    full_name: str
    email: EmailStr
    role: str = "user"


class UserRead(ORMModel):
    id: str
    customer_id: str
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime


class UserListResponse(BaseModel):
    items: list[UserRead]
    total: int


class LicenseCreate(BaseModel):
    user_id: str
    product: str
    plan: str
    expires_at: datetime | None = None
    features: list[str] = Field(default_factory=list)

    @field_validator("product")
    @classmethod
    def normalize_product(cls, value: str) -> str:
        return normalize_product_name(value)


class LicenseRead(BaseModel):
    id: str
    issued_to: str
    email: EmailStr
    plan: str
    expires_at: datetime | None = None
    features: list[str]
    status: str
    product: str
    key_prefix: str
    created_at: datetime


class LicenseCreateResponse(BaseModel):
    license_key: str
    license: LicenseRead


class LicenseKeyRead(BaseModel):
    license_key: str


class LicenseListResponse(BaseModel):
    items: list[LicenseRead]
    total: int


class LicenseActionRequest(BaseModel):
    action: str
    reason: str | None = None


class AuditLogRead(ORMModel):
    id: str
    actor_type: str
    actor_id: str | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    changes: dict
    created_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogRead]
