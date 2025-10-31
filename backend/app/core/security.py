"""
Безопасность: JWT, хеширование паролей, scopes
"""
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.errors import UnauthorizedError, ForbiddenError


# Password hashing
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Создание JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Создание JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Декодирование JWT токена"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise UnauthorizedError("Invalid token")


def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """Получение payload из токена"""
    return decode_token(token)


# Scopes (разрешения)
SCOPES = {
    "admin": "admin:*",
    "objects:read": "objects:read",
    "objects:write": "objects:write",
    "visits:read": "visits:read",
    "visits:write": "visits:write",
    "customers:read": "customers:read",
    "customers:write": "customers:write",
    "users:read": "users:read",
    "users:write": "users:write",
    "reports:read": "reports:read",
    "reports:write": "reports:write",
    "audit:read": "audit:read",
}


def get_scopes_from_role(role: str) -> List[str]:
    """Получение списка scopes для роли"""
    role_scopes = {
        "ADMIN": [
            SCOPES["admin"],
            SCOPES["objects:read"],
            SCOPES["objects:write"],
            SCOPES["visits:read"],
            SCOPES["visits:write"],
            SCOPES["customers:read"],
            SCOPES["customers:write"],
            SCOPES["users:read"],
            SCOPES["users:write"],
            SCOPES["reports:read"],
            SCOPES["reports:write"],
            SCOPES["audit:read"],
        ],
        "SUPERVISOR": [
            SCOPES["objects:read"],
            SCOPES["objects:write"],
            SCOPES["visits:read"],
            SCOPES["visits:write"],
            SCOPES["customers:read"],
            SCOPES["customers:write"],
            SCOPES["users:read"],
            SCOPES["reports:read"],
            SCOPES["reports:write"],
        ],
        "ENGINEER": [
            SCOPES["objects:read"],
            SCOPES["visits:read"],
            SCOPES["visits:write"],
            SCOPES["customers:read"],
            SCOPES["customers:write"],
        ],
    }
    return role_scopes.get(role, [])


def require_scopes(*required_scopes: str):
    """Декоратор для проверки scopes"""
    def _check_scopes(payload: dict = Depends(get_token_payload)) -> dict:
        token_scopes = payload.get("scopes", [])
        
        # Admin имеет все права
        if "admin:*" in token_scopes:
            return payload
        
        for scope in required_scopes:
            if scope not in token_scopes:
                raise ForbiddenError(f"Missing required scope: {scope}")
        
        return payload
    
    return _check_scopes

