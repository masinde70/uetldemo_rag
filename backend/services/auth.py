"""
Production-ready authentication service with JWT tokens and HttpOnly cookies.

Features:
- JWT access tokens (short-lived, 15 min)
- JWT refresh tokens (long-lived, 7 days)
- HttpOnly cookies for token storage
- Password hashing with bcrypt
- Token refresh mechanism
- HTTPS enforcement in production
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from email_validator import EmailNotValidError, validate_email
from passlib.context import CryptContext
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import User, UserRole

# --- Configuration ---

# JWT Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE-ME-IN-PRODUCTION-use-openssl-rand-hex-32")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Cookie Settings
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"  # Set to True in production with HTTPS
COOKIE_HTTPONLY = True  # Always true for security
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")  # "strict", "lax", or "none"
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", None)  # Set to your domain in production

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Email Utilities ---

def normalize_email(value: str) -> str:
    """
    Normalize emails while allowing development-only domains (e.g., .local).
    
    Attempts full RFC validation first; if the only failure is a special-use
    development domain, falls back to a minimal shape check so local accounts
    (admin@sisuiq.local) remain usable.
    """
    raw = value.strip()
    try:
        result = validate_email(raw, check_deliverability=False)
        return result.normalized
    except EmailNotValidError as exc:  # pragma: no cover - validation path
        lowered = raw.lower()
        if lowered.count("@") == 1:
            local, domain = lowered.split("@", 1)
            if domain.endswith((".local", ".localhost")) or domain == "localhost":
                if local and domain and not domain.startswith("."):
                    return f"{local}@{domain}"
        raise ValueError("Invalid email address") from exc


# --- Pydantic Schemas ---

class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # user id
    email: str
    role: str
    exp: datetime
    iat: datetime
    type: str  # "access" or "refresh"
    jti: str  # unique token id


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: str
    name: str
    password: str
    role: UserRole = UserRole.USER

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class UserResponse(BaseModel):
    """Schema for user response (no sensitive data)."""
    id: str
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response for API."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


# --- Password Utilities ---

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT Utilities ---

def create_access_token(user: User) -> tuple[str, datetime]:
    """
    Create a short-lived access token.
    
    Returns:
        Tuple of (token_string, expiration_datetime)
    """
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "exp": expires,
        "iat": now,
        "type": "access",
        "jti": str(uuid.uuid4()),
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, expires


def create_refresh_token(user: User) -> tuple[str, datetime]:
    """
    Create a long-lived refresh token.
    
    Returns:
        Tuple of (token_string, expiration_datetime)
    """
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "exp": expires,
        "iat": now,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, expires


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT token.
    
    Returns:
        TokenPayload if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_access_token(token: str) -> Optional[TokenPayload]:
    """Verify an access token."""
    payload = decode_token(token)
    if payload and payload.type == "access":
        return payload
    return None


def verify_refresh_token(token: str) -> Optional[TokenPayload]:
    """Verify a refresh token."""
    payload = decode_token(token)
    if payload and payload.type == "refresh":
        return payload
    return None


# --- Database Operations ---

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email address."""
    normalized_email = normalize_email(email)
    result = await db.execute(select(User).where(User.email == normalized_email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get a user by ID."""
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        return None
    result = await db.execute(select(User).where(User.id == uid))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user with hashed password."""
    user = User(
        email=normalize_email(user_data.email),
        name=user_data.name,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession, 
    email: str, 
    password: str
) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    Returns:
        User if authentication successful, None otherwise
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    
    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    
    return user


async def update_user_password(
    db: AsyncSession,
    user: User,
    new_password: str
) -> User:
    """Update a user's password."""
    user.password_hash = hash_password(new_password)
    await db.commit()
    await db.refresh(user)
    return user


# --- Cookie Helpers ---

def get_cookie_settings() -> dict:
    """Get cookie settings for token storage."""
    return {
        "httponly": COOKIE_HTTPONLY,
        "secure": COOKIE_SECURE,
        "samesite": COOKIE_SAMESITE,
        "domain": COOKIE_DOMAIN,
    }


def get_access_cookie_settings() -> dict:
    """Get settings for access token cookie."""
    settings = get_cookie_settings()
    settings["max_age"] = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    settings["key"] = "access_token"
    return settings


def get_refresh_cookie_settings() -> dict:
    """Get settings for refresh token cookie."""
    settings = get_cookie_settings()
    settings["max_age"] = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    settings["key"] = "refresh_token"
    return settings


# --- User Response Helper ---

def user_to_response(user: User) -> UserResponse:
    """Convert User model to UserResponse schema."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )
