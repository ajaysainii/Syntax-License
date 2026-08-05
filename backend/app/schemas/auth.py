from pydantic import BaseModel, EmailStr

from app.schemas.common import AdminRead


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminRead

