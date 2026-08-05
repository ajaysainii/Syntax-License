from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.customer import Customer
from app.models.user import User
from app.schemas.common import UserCreate, UserListResponse, UserRead, UserUpdate
from app.services.audit import write_audit_log

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserListResponse)
def list_users(
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> UserListResponse:
    stmt = select(User).options(joinedload(User.customer)).order_by(User.created_at.desc())
    count_stmt = select(func.count()).select_from(User)
    if q:
        term = f"%{q.strip()}%"
        predicate = or_(User.full_name.ilike(term), User.email.ilike(term))
        stmt = stmt.where(predicate)
        count_stmt = count_stmt.where(predicate)
    items = db.scalars(stmt).unique().all()
    total = db.scalar(count_stmt) or 0
    return UserListResponse(items=[UserRead.model_validate(item) for item in items], total=total)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> UserRead:
    customer = db.get(Customer, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=409, detail="User email already exists")

    user = User(
        customer_id=payload.customer_id,
        full_name=payload.full_name,
        email=payload.email.lower(),
        role=payload.role,
    )
    db.add(user)
    db.flush()
    write_audit_log(
        db,
        actor_type="admin",
        actor_id=admin.id,
        action="user.create",
        entity_type="user",
        entity_id=user.id,
        changes=payload.model_dump(),
    )
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> UserRead:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    customer = db.get(Customer, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    existing = db.scalar(select(User).where(User.email == payload.email.lower(), User.id != user_id))
    if existing:
        raise HTTPException(status_code=409, detail="User email already exists")

    user.customer_id = payload.customer_id
    user.full_name = payload.full_name
    user.email = payload.email.lower()
    user.role = payload.role
    db.add(user)
    write_audit_log(
        db,
        actor_type="admin",
        actor_id=admin.id,
        action="user.update",
        entity_type="user",
        entity_id=user.id,
        changes=payload.model_dump(),
    )
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)
