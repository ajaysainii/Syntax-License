from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.customer import Customer
from app.schemas.common import CustomerCreate, CustomerListResponse, CustomerRead
from app.services.audit import write_audit_log

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=CustomerListResponse)
def list_customers(
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> CustomerListResponse:
    stmt = select(Customer).order_by(Customer.created_at.desc())
    count_stmt = select(func.count()).select_from(Customer)
    if q:
        term = f"%{q.strip()}%"
        predicate = or_(Customer.name.ilike(term), Customer.email.ilike(term))
        stmt = stmt.where(predicate)
        count_stmt = count_stmt.where(predicate)

    items = db.scalars(stmt).all()
    total = db.scalar(count_stmt) or 0
    return CustomerListResponse(
        items=[CustomerRead.model_validate(item) for item in items],
        total=total,
    )


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> CustomerRead:
    existing = db.scalar(select(Customer).where(Customer.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=409, detail="Customer email already exists")

    customer = Customer(
        name=payload.name,
        email=payload.email.lower(),
        company=payload.company,
        notes=payload.notes,
    )
    db.add(customer)
    db.flush()
    write_audit_log(
        db,
        actor_type="admin",
        actor_id=admin.id,
        action="customer.create",
        entity_type="customer",
        entity_id=customer.id,
        changes=payload.model_dump(),
    )
    db.commit()
    db.refresh(customer)
    return CustomerRead.model_validate(customer)

