import hashlib
import hmac
import secrets
from base64 import urlsafe_b64encode
from datetime import UTC, datetime, timedelta

from cryptography.fernet import Fernet, InvalidToken
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
license_key_cipher = Fernet(
    urlsafe_b64encode(hashlib.sha256(settings.license_hmac_secret.encode("utf-8")).digest())
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str) -> str:
    now = datetime.now(UTC)
    expires = now + timedelta(minutes=settings.jwt_expiration_minutes)
    return jwt.encode(
        {"sub": subject, "iat": int(now.timestamp()), "exp": int(expires.timestamp())},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def hash_license_key(license_key: str) -> str:
    return hmac.new(
        settings.license_hmac_secret.encode("utf-8"),
        license_key.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_license_key() -> str:
    chunks = [secrets.token_hex(3).upper() for _ in range(4)]
    return f"SYNTAX-{'-'.join(chunks)}"


def encrypt_license_key(license_key: str) -> str:
    return license_key_cipher.encrypt(license_key.encode("utf-8")).decode("utf-8")


def decrypt_license_key(encrypted_license_key: str) -> str | None:
    try:
        return license_key_cipher.decrypt(encrypted_license_key.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return None
