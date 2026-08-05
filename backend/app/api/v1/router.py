from fastapi import APIRouter

from app.api.v1 import admins, auth, customers, licenses, users, audit_logs

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(admins.router)
api_router.include_router(customers.router)
api_router.include_router(users.router)
api_router.include_router(licenses.router)
api_router.include_router(audit_logs.router)
