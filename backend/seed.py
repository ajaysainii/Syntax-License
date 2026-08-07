from datetime import UTC, datetime, timedelta

from app.db.base import __all__  # noqa: F401
from app.core.config import settings
from app.core.security import encrypt_license_key, hash_password
from app.db.session import SessionLocal
from app.models.admin_user import AdminUser
from app.models.customer import Customer
from app.models.user import User
from app.models.license import License
from app.services.licensing import create_license_key, hash_license_key


def run() -> None:
    db = SessionLocal()
    admin = db.query(AdminUser).filter(AdminUser.email == settings.admin_email.lower()).first()
    if not admin:
        admin = AdminUser(
            email=settings.admin_email.lower(),
            full_name="Syntax Administrator",
            password_hash=hash_password(settings.admin_password),
        )
        db.add(admin)

    customer = db.query(Customer).filter(Customer.email == "hello@syntaxnation.com").first()
    if not customer:
        customer = Customer(
            name="Syntax Nation",
            email="hello@syntaxnation.com",
            company="Syntax",
            notes="Seed customer",
        )
        db.add(customer)
        db.flush()

    user = db.query(User).filter(User.email == "founder@syntaxnation.com").first()
    if not user:
        user = User(
            customer_id=customer.id,
            full_name="Syntax Founder",
            email="founder@syntaxnation.com",
            role="owner",
        )
        db.add(user)
        db.flush()

    if not db.query(License).filter(License.user_id == user.id).first():
        plain = create_license_key()
        db.add(
            License(
                user_id=user.id,
                customer_id=customer.id,
                product="syntax-desktop",
                plan="enterprise",
                status="active",
                expires_at=datetime.now(UTC) + timedelta(days=365),
                features=["team-sync", "priority-support", "updates"],
                license_key_hash=hash_license_key(plain),
                license_key_encrypted=encrypt_license_key(plain),
                key_prefix=plain[:12],
            )
        )
        print(f"Seed license key: {plain}")

    db.commit()
    db.close()


if __name__ == "__main__":
    run()
