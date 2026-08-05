import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class License(Base):
    __tablename__ = "licenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), index=True)
    product: Mapped[str] = mapped_column(String(120), index=True)
    plan: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(50), index=True, default="active")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    features: Mapped[list[str]] = mapped_column(JSON, default=list)
    license_key_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    key_prefix: Mapped[str] = mapped_column(String(24), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    user = relationship("User", back_populates="licenses")
    customer = relationship("Customer", back_populates="licenses")
    installations = relationship("Installation", back_populates="license", cascade="all, delete-orphan")
