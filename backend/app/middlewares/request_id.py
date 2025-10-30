"""
Middleware для добавления request_id в каждый запрос
"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Добавляет уникальный request_id к каждому запросу"""
    
    async def dispatch(self, request: Request, call_next):
        # Генерируем или используем существующий request_id
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Сохраняем в state для использования в логах
        request.state.request_id = request_id
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Добавляем request_id в заголовки ответа
        response.headers["X-Request-ID"] = request_id
        
        return response

