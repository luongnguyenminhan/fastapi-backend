from fastapi import APIRouter

from app.constants.messages import MessageConstants
from app.modules.admin.schemas.auth_admin import (
    AdminAuthResponse,
    AdminLoginRequest,
    AdminTokenResponse,
)
from app.modules.admin.services.auth_admin import admin_login

router = APIRouter(prefix="/admin/auth", tags=["Admin-Auth"])


@router.post("/login", response_model=AdminAuthResponse)
def login(credentials: AdminLoginRequest) -> AdminAuthResponse:
    """
    Admin login endpoint.
    Accepts username and password, returns JWT access token.

    Credentials are verified against ADMIN_USERNAME and ADMIN_PASSWORD in config.
    """
    token_data = admin_login(credentials.username, credentials.password)

    return AdminAuthResponse(success=True, message=MessageConstants.LOGIN_SUCCESS, data=AdminTokenResponse(access_token=token_data["access_token"], token_type=token_data["token_type"], expires_in=token_data["expires_in"]))
