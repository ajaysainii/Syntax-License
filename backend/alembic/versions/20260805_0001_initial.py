"""initial schema"""

from alembic import op
import sqlalchemy as sa

revision = "20260805_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
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
    op.create_index("ix_admin_users_email", "admin_users", ["email"], unique=True)

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
    op.create_index("ix_customers_email", "customers", ["email"], unique=True)
    op.create_index("ix_customers_name", "customers", ["name"], unique=False)

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
    op.create_index("ix_users_customer_id", "users", ["customer_id"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_full_name", "users", ["full_name"], unique=False)

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
        sa.Column("license_key_hash", sa.Text(), nullable=False),
        sa.Column("key_prefix", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_licenses_customer_id", "licenses", ["customer_id"], unique=False)
    op.create_index("ix_licenses_key_prefix", "licenses", ["key_prefix"], unique=False)
    op.create_index("ix_licenses_license_key_hash", "licenses", ["license_key_hash"], unique=True)
    op.create_index("ix_licenses_plan", "licenses", ["plan"], unique=False)
    op.create_index("ix_licenses_product", "licenses", ["product"], unique=False)
    op.create_index("ix_licenses_status", "licenses", ["status"], unique=False)
    op.create_index("ix_licenses_user_id", "licenses", ["user_id"], unique=False)

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
    op.create_index("ix_installations_installation_id", "installations", ["installation_id"], unique=False)
    op.create_index("ix_installations_license_id", "installations", ["license_id"], unique=False)

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
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_installations_license_id", table_name="installations")
    op.drop_index("ix_installations_installation_id", table_name="installations")
    op.drop_table("installations")
    op.drop_index("ix_licenses_user_id", table_name="licenses")
    op.drop_index("ix_licenses_status", table_name="licenses")
    op.drop_index("ix_licenses_product", table_name="licenses")
    op.drop_index("ix_licenses_plan", table_name="licenses")
    op.drop_index("ix_licenses_license_key_hash", table_name="licenses")
    op.drop_index("ix_licenses_key_prefix", table_name="licenses")
    op.drop_index("ix_licenses_customer_id", table_name="licenses")
    op.drop_table("licenses")
    op.drop_index("ix_users_full_name", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_customer_id", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_customers_name", table_name="customers")
    op.drop_index("ix_customers_email", table_name="customers")
    op.drop_table("customers")
    op.drop_index("ix_admin_users_email", table_name="admin_users")
    op.drop_table("admin_users")

