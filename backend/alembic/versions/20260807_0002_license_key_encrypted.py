"""store encrypted license keys for admin reveal"""

from alembic import op
import sqlalchemy as sa

revision = "20260807_0002"
down_revision = "20260805_0001"
branch_labels = None
depends_on = None


def _has_index(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "admin_users" not in tables:
        op.create_table(
            "admin_users",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("full_name", sa.String(length=255), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        tables.add("admin_users")
        inspector = sa.inspect(bind)
    if not _has_index(inspector, "admin_users", "ix_admin_users_email"):
        op.create_index("ix_admin_users_email", "admin_users", ["email"], unique=True)

    if "customers" not in tables:
        op.create_table(
            "customers",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("company", sa.String(length=255), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        tables.add("customers")
        inspector = sa.inspect(bind)
    if not _has_index(inspector, "customers", "ix_customers_email"):
        op.create_index("ix_customers_email", "customers", ["email"], unique=True)
    if not _has_index(inspector, "customers", "ix_customers_name"):
        op.create_index("ix_customers_name", "customers", ["name"], unique=False)

    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("customer_id", sa.String(length=36), sa.ForeignKey("customers.id"), nullable=False),
            sa.Column("full_name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("role", sa.String(length=120), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        tables.add("users")
        inspector = sa.inspect(bind)
    if not _has_index(inspector, "users", "ix_users_customer_id"):
        op.create_index("ix_users_customer_id", "users", ["customer_id"], unique=False)
    if not _has_index(inspector, "users", "ix_users_email"):
        op.create_index("ix_users_email", "users", ["email"], unique=True)
    if not _has_index(inspector, "users", "ix_users_full_name"):
        op.create_index("ix_users_full_name", "users", ["full_name"], unique=False)

    if "licenses" not in tables:
        op.create_table(
            "licenses",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("customer_id", sa.String(length=36), sa.ForeignKey("customers.id"), nullable=False),
            sa.Column("product", sa.String(length=120), nullable=False),
            sa.Column("plan", sa.String(length=120), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("features", sa.JSON(), nullable=False),
            sa.Column("license_key_hash", sa.String(length=64), nullable=False),
            sa.Column("key_prefix", sa.String(length=24), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        tables.add("licenses")
        inspector = sa.inspect(bind)
    if not _has_index(inspector, "licenses", "ix_licenses_customer_id"):
        op.create_index("ix_licenses_customer_id", "licenses", ["customer_id"], unique=False)
    if not _has_index(inspector, "licenses", "ix_licenses_key_prefix"):
        op.create_index("ix_licenses_key_prefix", "licenses", ["key_prefix"], unique=False)
    if not _has_index(inspector, "licenses", "ix_licenses_license_key_hash"):
        op.create_index("ix_licenses_license_key_hash", "licenses", ["license_key_hash"], unique=True)
    if not _has_index(inspector, "licenses", "ix_licenses_plan"):
        op.create_index("ix_licenses_plan", "licenses", ["plan"], unique=False)
    if not _has_index(inspector, "licenses", "ix_licenses_product"):
        op.create_index("ix_licenses_product", "licenses", ["product"], unique=False)
    if not _has_index(inspector, "licenses", "ix_licenses_status"):
        op.create_index("ix_licenses_status", "licenses", ["status"], unique=False)
    if not _has_index(inspector, "licenses", "ix_licenses_user_id"):
        op.create_index("ix_licenses_user_id", "licenses", ["user_id"], unique=False)

    if "installations" not in tables:
        op.create_table(
            "installations",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("license_id", sa.String(length=36), sa.ForeignKey("licenses.id"), nullable=False),
            sa.Column("installation_id", sa.String(length=255), nullable=False),
            sa.Column("hostname", sa.String(length=255), nullable=True),
            sa.Column("platform", sa.String(length=120), nullable=True),
            sa.Column("version", sa.String(length=120), nullable=True),
            sa.Column("first_seen_ip", sa.String(length=64), nullable=True),
            sa.Column("last_seen_ip", sa.String(length=64), nullable=True),
            sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
        tables.add("installations")
        inspector = sa.inspect(bind)
    if not _has_index(inspector, "installations", "ix_installations_installation_id"):
        op.create_index("ix_installations_installation_id", "installations", ["installation_id"], unique=False)
    if not _has_index(inspector, "installations", "ix_installations_license_id"):
        op.create_index("ix_installations_license_id", "installations", ["license_id"], unique=False)

    if "audit_logs" not in tables:
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("actor_type", sa.String(length=50), nullable=False),
            sa.Column("actor_id", sa.String(length=36), nullable=True),
            sa.Column("action", sa.String(length=120), nullable=False),
            sa.Column("entity_type", sa.String(length=120), nullable=False),
            sa.Column("entity_id", sa.String(length=36), nullable=True),
            sa.Column("changes", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
        tables.add("audit_logs")
        inspector = sa.inspect(bind)
    if not _has_index(inspector, "audit_logs", "ix_audit_logs_action"):
        op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)

    license_columns = {column["name"] for column in inspector.get_columns("licenses")}
    if "license_key_encrypted" not in license_columns:
        op.add_column("licenses", sa.Column("license_key_encrypted", sa.String(length=512), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "licenses" in inspector.get_table_names():
        license_columns = {column["name"] for column in inspector.get_columns("licenses")}
        if "license_key_encrypted" in license_columns:
            op.drop_column("licenses", "license_key_encrypted")
