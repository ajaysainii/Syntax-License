from app.core.security import create_license_key, hash_license_key
from app.models.license import License
from app.schemas.common import LicenseRead


def normalize_features(features: list[str]) -> list[str]:
    return sorted({feature.strip() for feature in features if feature.strip()})


def serialize_license(license_row: License) -> LicenseRead:
    return LicenseRead(
        id=license_row.id,
        issued_to=license_row.user.full_name,
        email=license_row.user.email,
        plan=license_row.plan,
        expires_at=license_row.expires_at,
        features=license_row.features or [],
        status=license_row.status,
        product=license_row.product,
        key_prefix=license_row.key_prefix,
        created_at=license_row.created_at,
    )


__all__ = ["create_license_key", "hash_license_key", "normalize_features", "serialize_license"]

