"""
Middleware для логирования запросов
"""
import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Логирование всех HTTP запросов"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Извлекаем данные запроса
        request_id = getattr(request.state, "request_id", None)
        method = request.method
        path = request.url.path
        query_params = str(request.query_params)
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Получаем user_id из токена (если есть)
        user_id = None
        try:
            if "authorization" in request.headers:
                from app.core.security import decode_token
                from fastapi.security import HTTPBearer
                security = HTTPBearer()
                credentials = await security(request)
                if credentials:
                    payload = decode_token(credentials.credentials)
                    user_id = payload.get("sub")
        except Exception:
            pass  # Не критично, если токен отсутствует или невалиден
        
        # Выполняем запрос
        try:
            response = await call_next(request)
            status_code = response.status_code
            error = None
        except Exception as exc:
            status_code = 500
            error = str(exc)
            raise
        finally:
            # Логируем запрос
            duration = time.time() - start_time
            
            log_data = {
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_params": query_params,
                "status_code": status_code,
                "duration": duration,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "user_id": user_id,
            }
            
            if error:
                log_data["error"] = error
            
            if status_code >= 500:
                logger.error("request_completed", **log_data)
            elif status_code >= 400:
                logger.warning("request_completed", **log_data)
            else:
                logger.info("request_completed", **log_data)
        
        return response

