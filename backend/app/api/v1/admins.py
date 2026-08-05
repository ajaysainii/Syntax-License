from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.security import hash_password
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.common import AdminListResponse, AdminRead, AdminUpdate
from app.services.audit import write_audit_log

router = APIRouter(prefix="/admins", tags=["admins"])


@router.get("", response_model=AdminListResponse)
def list_admins(
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> AdminListResponse:
    stmt = select(AdminUser).order_by(AdminUser.created_at.desc())
    items = db.scalars(stmt).all()
    total = db.scalar(select(func.count()).select_from(AdminUser)) or 0
    return AdminListResponse(items=[AdminRead.model_validate(item) for item in items], total=total)


@router.put("/{admin_id}", response_model=AdminRead)
def update_admin(
    admin_id: str,
    payload: AdminUpdate,
    db: Session = Depends(get_db),
    actor: AdminUser = Depends(get_current_admin),
) -> AdminRead:
    admin = db.get(AdminUser, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    existing = db.scalar(select(AdminUser).where(AdminUser.email == payload.email.lower(), AdminUser.id != admin_id))
    if existing:
        raise HTTPException(status_code=409, detail="Admin email already exists")
    if actor.id == admin.id and not payload.is_active:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own admin account")

    admin.email = payload.email.lower()
    admin.full_name = payload.full_name
    admin.is_active = payload.is_active
    if payload.password:
        admin.password_hash = hash_password(payload.password)

    write_audit_log(
        db,
        actor_type="admin",
        actor_id=actor.id,
        action="admin.update",
        entity_type="admin_user",
        entity_id=admin.id,
        changes={
            "email": admin.email,
            "full_name": admin.full_name,
            "is_active": admin.is_active,
            "password_changed": bool(payload.password),
        },
    )
    db.commit()
    db.refresh(admin)
    return AdminRead.model_validate(admin)

