"""
Authentication router with JWT tokens and HttpOnly cookies.

Endpoints:
- POST /api/auth/login - Login with email/password
- POST /api/auth/logout - Logout (clear cookies)
- POST /api/auth/refresh - Refresh access token
- GET /api/auth/me - Get current user info
- POST /api/auth/register - Register new user (admin only)
- PUT /api/auth/password - Change password
"""

from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.models import User, UserRole
from backend.services.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    UserCreate,
    UserLogin,
    UserResponse,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    create_user,
    get_access_cookie_settings,
    get_refresh_cookie_settings,
    get_user_by_email,
    get_user_by_id,
    hash_password,
    normalize_email,
    update_user_password,
    user_to_response,
    verify_access_token,
    verify_password,
    verify_refresh_token,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Security scheme for Swagger UI
security = HTTPBearer(auto_error=False)


# --- Pydantic Schemas ---

class LoginRequest(BaseModel):
    """Login request body."""
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class LoginResponse(BaseModel):
    """Login response."""
    message: str
    user: UserResponse
    expires_in: int


class RegisterRequest(BaseModel):
    """Register request body."""
    email: str
    name: str
    password: str
    role: str = "user"

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class PasswordChangeRequest(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str


# --- Dependencies ---

async def get_current_user(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from cookie or Authorization header.
    
    Raises HTTPException 401 if not authenticated.
    """
    token = access_token
    
    # Also check Authorization header for API clients
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_id(db, payload.sub)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify they are an admin.
    
    Raises HTTPException 403 if not admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def get_optional_user(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    Does not raise exception for unauthenticated requests.
    """
    try:
        return await get_current_user(request, access_token, db)
    except HTTPException:
        return None


# --- Endpoints ---

@router.post("/login", response_model=LoginResponse)
async def login(
    response: Response,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password.
    
    Sets HttpOnly cookies for access and refresh tokens.
    """
    user = await authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Create tokens
    access_token, _ = create_access_token(user)
    refresh_token, _ = create_refresh_token(user)
    
    # Set HttpOnly cookies
    access_settings = get_access_cookie_settings()
    response.set_cookie(
        key=access_settings["key"],
        value=access_token,
        max_age=access_settings["max_age"],
        httponly=access_settings["httponly"],
        secure=access_settings["secure"],
        samesite=access_settings["samesite"],
        domain=access_settings.get("domain"),
    )
    
    refresh_settings = get_refresh_cookie_settings()
    response.set_cookie(
        key=refresh_settings["key"],
        value=refresh_token,
        max_age=refresh_settings["max_age"],
        httponly=refresh_settings["httponly"],
        secure=refresh_settings["secure"],
        samesite=refresh_settings["samesite"],
        domain=refresh_settings.get("domain"),
        path="/api/auth/refresh",  # Only send to refresh endpoint
    )
    
    return LoginResponse(
        message="Login successful",
        user=user_to_response(user),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    """
    Logout by clearing authentication cookies.
    """
    # Clear access token cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=get_access_cookie_settings()["secure"],
        samesite=get_access_cookie_settings()["samesite"],
    )
    
    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=get_refresh_cookie_settings()["secure"],
        samesite=get_refresh_cookie_settings()["samesite"],
        path="/api/auth/refresh",
    )
    
    return MessageResponse(message="Logged out successfully")


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    
    The refresh token is automatically sent via HttpOnly cookie.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )
    
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    user = await get_user_by_id(db, payload.sub)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new access token
    access_token, _ = create_access_token(user)
    
    # Set new access token cookie
    access_settings = get_access_cookie_settings()
    response.set_cookie(
        key=access_settings["key"],
        value=access_token,
        max_age=access_settings["max_age"],
        httponly=access_settings["httponly"],
        secure=access_settings["secure"],
        samesite=access_settings["samesite"],
        domain=access_settings.get("domain"),
    )
    
    return LoginResponse(
        message="Token refreshed",
        user=user_to_response(user),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    """
    return user_to_response(current_user)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Register a new user (admin only).
    
    Only admins can create new users.
    """
    # Check if email already exists
    existing = await get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Validate role
    try:
        role = UserRole(user_data.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}",
        )
    
    # Create user
    new_user = await create_user(
        db,
        UserCreate(
            email=user_data.email,
            name=user_data.name,
            password=user_data.password,
            role=role,
        ),
    )
    
    return user_to_response(new_user)


@router.put("/password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change current user's password.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    # Validate new password
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )
    
    # Update password
    await update_user_password(db, current_user, password_data.new_password)
    
    return MessageResponse(message="Password updated successfully")


@router.get("/verify")
async def verify_auth(current_user: User = Depends(get_current_user)):
    """
    Verify that the current authentication is valid.
    
    Returns 200 if authenticated, 401 otherwise.
    """
    return {
        "authenticated": True,
        "user_id": str(current_user.id),
        "role": current_user.role.value,
    }
