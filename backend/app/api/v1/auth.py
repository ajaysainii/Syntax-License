from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.auth import AdminLoginRequest, TokenResponse
from app.schemas.common import AdminRead
from app.services.audit import write_audit_log
from app.core.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: AdminLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    admin = db.scalar(select(AdminUser).where(AdminUser.email == payload.email.lower()))
    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
        )

    token = create_access_token(str(admin.id))
    write_audit_log(
        db,
        actor_type="admin",
        actor_id=admin.id,
        action="admin.login",
        entity_type="admin_user",
        entity_id=admin.id,
        changes={"email": admin.email},
    )
    db.commit()
    return TokenResponse(access_token=token, admin=AdminRead.model_validate(admin))


@router.get("/me", response_model=AdminRead)
def me(admin: AdminUser = Depends(get_current_admin)) -> AdminRead:
    return AdminRead.model_validate(admin)

