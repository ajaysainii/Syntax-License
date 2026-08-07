from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_admin
from app.core.security import decrypt_license_key, encrypt_license_key
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.installation import Installation
from app.models.license import License
from app.models.user import User
from app.schemas.common import (
    LicenseActionRequest,
    LicenseCreate,
    LicenseCreateResponse,
    LicenseKeyRead,
    LicenseListResponse,
    LicenseRead,
)
from app.schemas.validation import (
    LicenseValidationRequest,
    LicenseValidationResponse,
    ValidationLicensePayload,
)
from app.services.audit import write_audit_log
from app.services.licensing import (
    create_license_key,
    hash_license_key,
    normalize_features,
    serialize_license,
)
from app.services.products import product_match_names

router = APIRouter(prefix="/licenses", tags=["licenses"])


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


@router.get("", response_model=LicenseListResponse)
def list_licenses(
    q: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> LicenseListResponse:
    stmt = (
        select(License)
        .options(joinedload(License.user), joinedload(License.customer))
        .order_by(License.created_at.desc())
    )
    count_stmt = select(func.count()).select_from(License)

    if q:
        term = f"%{q.strip()}%"
        predicate = or_(
            License.key_prefix.ilike(term),
            License.product.ilike(term),
            License.plan.ilike(term),
            User.full_name.ilike(term),
            User.email.ilike(term),
        )
        stmt = stmt.join(User).where(predicate)
        count_stmt = count_stmt.join(User).where(predicate)
    if status_filter:
        stmt = stmt.where(License.status == status_filter)
        count_stmt = count_stmt.where(License.status == status_filter)

    items = db.scalars(stmt).unique().all()
    total = db.scalar(count_stmt) or 0
    return LicenseListResponse(items=[serialize_license(item) for item in items], total=total)


@router.post("", response_model=LicenseCreateResponse, status_code=status.HTTP_201_CREATED)
def create_license(
    payload: LicenseCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> LicenseCreateResponse:
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plain_key = create_license_key()
    license_hash = hash_license_key(plain_key)
    license_row = License(
        user_id=user.id,
        customer_id=user.customer_id,
        product=payload.product,
        plan=payload.plan,
        expires_at=payload.expires_at,
        status="active",
        features=normalize_features(payload.features),
        license_key_hash=license_hash,
        license_key_encrypted=encrypt_license_key(plain_key),
        key_prefix=plain_key[:12],
    )
    db.add(license_row)
    db.flush()
    write_audit_log(
        db,
        actor_type="admin",
        actor_id=admin.id,
        action="license.create",
        entity_type="license",
        entity_id=license_row.id,
        changes={
            "user_id": user.id,
            "plan": payload.plan,
            "product": payload.product,
            "expires_at": payload.expires_at.isoformat() if payload.expires_at else None,
        },
    )
    db.commit()
    db.refresh(license_row)
    return LicenseCreateResponse(
        license_key=plain_key,
        license=serialize_license(license_row),
    )


@router.get("/{license_id}/key", response_model=LicenseKeyRead)
def get_license_key(
    license_id: str,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> LicenseKeyRead:
    license_row = db.get(License, license_id)
    if not license_row:
        raise HTTPException(status_code=404, detail="License not found")
    if not license_row.license_key_encrypted:
        raise HTTPException(status_code=404, detail="License key is unavailable for this record")

    license_key = decrypt_license_key(license_row.license_key_encrypted)
    if not license_key:
        raise HTTPException(status_code=500, detail="Stored license key could not be decrypted")
    return LicenseKeyRead(license_key=license_key)


@router.post("/{license_id}/actions", response_model=LicenseRead)
def mutate_license(
    license_id: str,
    payload: LicenseActionRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> LicenseRead:
    license_row = db.get(License, license_id)
    if not license_row:
        raise HTTPException(status_code=404, detail="License not found")

    action_to_status = {
        "revoke": "revoked",
        "suspend": "suspended",
        "reactivate": "active",
    }
    license_row.status = action_to_status[payload.action]
    license_row.updated_at = datetime.now(UTC)
    db.add(license_row)
    write_audit_log(
        db,
        actor_type="admin",
        actor_id=admin.id,
        action=f"license.{payload.action}",
        entity_type="license",
        entity_id=license_row.id,
        changes={"reason": payload.reason, "status": license_row.status},
    )
    db.commit()
    db.refresh(license_row)
    return serialize_license(license_row)


@router.post("/validate", response_model=LicenseValidationResponse)
def validate_license(
    payload: LicenseValidationRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> LicenseValidationResponse:
    checked_at = datetime.now(UTC)
    license_hash = hash_license_key(payload.license_key)
    license_row = db.scalar(
        select(License)
        .options(joinedload(License.user))
        .where(
            License.license_key_hash == license_hash,
            License.product.in_(product_match_names(payload.product)),
        )
    )

    if not license_row:
        return LicenseValidationResponse.invalid(
            checked_at=checked_at,
            message="License key not found",
        )

    installation = db.scalar(
        select(Installation).where(
            Installation.license_id == license_row.id,
            Installation.installation_id == payload.installation_id,
        )
    )
    if not installation:
        installation = Installation(
            license_id=license_row.id,
            installation_id=payload.installation_id,
            hostname=payload.hostname,
            platform=payload.platform,
            version=payload.version,
            last_seen_at=checked_at,
            first_seen_ip=request.client.host if request.client else None,
            last_seen_ip=request.client.host if request.client else None,
        )
        db.add(installation)
    else:
        installation.hostname = payload.hostname
        installation.platform = payload.platform
        installation.version = payload.version
        installation.last_seen_at = checked_at
        installation.last_seen_ip = request.client.host if request.client else None

    status_value = license_row.status
    valid = True
    message = "License is valid"

    if status_value != "active":
        valid = False
        message = f"License is {status_value}"
    elif (expires_at := _as_utc(license_row.expires_at)) and expires_at < checked_at:
        status_value = "expired"
        valid = False
        message = "License has expired"

    write_audit_log(
        db,
        actor_type="system",
        actor_id=None,
        action="license.validate",
        entity_type="license",
        entity_id=license_row.id,
        changes={
            "installation_id": payload.installation_id,
            "valid": valid,
            "reported_version": payload.version,
        },
    )
    db.commit()
    db.refresh(license_row)
    return LicenseValidationResponse(
        valid=valid,
        status=status_value,
        message=message,
        checked_at=checked_at,
        license=ValidationLicensePayload(
            id=license_row.id,
            issued_to=license_row.user.full_name,
            email=license_row.user.email,
            plan=license_row.plan,
            expires_at=license_row.expires_at,
            features=license_row.features or [],
            status=license_row.status,
        ),
    )
