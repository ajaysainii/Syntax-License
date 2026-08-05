from datetime import UTC, datetime

from pydantic import BaseModel

from pydantic import EmailStr


class ValidationLicensePayload(BaseModel):
    id: str
    issued_to: str
    email: EmailStr
    plan: str
    expires_at: datetime | None = None
    features: list[str]
    status: str


class LicenseValidationRequest(BaseModel):
    license_key: str
    installation_id: str
    product: str
    version: str | None = None
    hostname: str | None = None
    platform: str | None = None


class LicenseValidationResponse(BaseModel):
    valid: bool
    status: str
    message: str
    checked_at: datetime
    license: ValidationLicensePayload | None = None

    @classmethod
    def invalid(cls, checked_at: datetime, message: str) -> "LicenseValidationResponse":
        return cls(
            valid=False,
            status="invalid",
            message=message,
            checked_at=checked_at.astimezone(UTC),
            license=None,
        )
