"""
Обработка ошибок приложения
"""
from typing import Any, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Базовый класс для ошибок приложения"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppError):
    """Ресурс не найден"""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
        )


class ValidationError(AppError):
    """Ошибка валидации"""
    
    def __init__(self, message: str, fields: Optional[dict[str, list[str]]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details={"fields": fields or {}},
        )


class UnauthorizedError(AppError):
    """Не авторизован"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )


class ForbiddenError(AppError):
    """Доступ запрещён"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )


class ConflictError(AppError):
    """Конфликт версий (оптимистическая блокировка)"""
    
    def __init__(self, message: str, diff: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            details={"diff": diff or {}},
        )


class RateLimitError(AppError):
    """Превышен лимит запросов"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
        )


async def app_error_handler(request, exc: AppError) -> JSONResponse:
    """Глобальный обработчик ошибок приложения"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )

