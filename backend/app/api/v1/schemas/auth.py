"""
Pydantic схемы для авторизации
"""
from pydantic import BaseModel, EmailStr, Field


class TokenRequest(BaseModel):
    """Запрос токена (OAuth2 password)"""
    username: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, description="Пароль")


class TokenResponse(BaseModel):
    """Ответ с токенами"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Запрос обновления access token"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Запрос сброса пароля"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Подтверждение сброса пароля"""
    token: str
    new_password: str = Field(..., min_length=8)

