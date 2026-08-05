from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.audit_log import AuditLog
from app.schemas.common import AuditLogListResponse, AuditLogRead

router = APIRouter(prefix="/audit-logs", tags=["audit_logs"])


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> AuditLogListResponse:
    rows = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)).all()
    return AuditLogListResponse(items=[AuditLogRead.model_validate(row) for row in rows])

