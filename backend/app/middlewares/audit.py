"""
Middleware для автоматического логирования изменений в аудит
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, Any
import json

from app.infrastructure.db.models import ActionType


def _mask_pii_in_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Маскировать PII поля в словаре для аудита"""
    masked = data.copy()
    
    # Поля, которые не логируются в открытом виде
    pii_fields = ["phone", "email", "hashed_password"]
    
    for field in pii_fields:
        if field in masked and masked[field]:
            if field == "phone":
                phone = str(masked[field])
                if len(phone) > 4:
                    masked[field] = phone[:5] + "***-**" + phone[-2:]
                else:
                    masked[field] = "****"
            elif field == "email":
                email = str(masked[field])
                parts = email.split("@")
                if len(parts) == 2:
                    masked[field] = f"{parts[0][:2]}***@{parts[1]}"
                else:
                    masked[field] = "***"
            elif field == "hashed_password":
                masked[field] = "***"
    
    return masked


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования мутирующих операций"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Пропускаем только мутирующие методы
        if request.method not in ["POST", "PATCH", "PUT", "DELETE"]:
            return await call_next(request)
        
        # Пропускаем служебные эндпойнты
        path = request.url.path
        if any(skip in path for skip in ["/health", "/docs", "/redoc", "/auth/token", "/auth/refresh"]):
            return await call_next(request)
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Логируем только успешные операции
        if 200 <= response.status_code < 300:
            try:
                # Получаем пользователя из токена (если есть)
                user_id = None
                if "authorization" in request.headers:
                    try:
                        from app.core.security import decode_token
                        from fastapi.security import HTTPBearer
                        security = HTTPBearer()
                        credentials = await security(request)
                        if credentials:
                            payload = decode_token(credentials.credentials)
                            user_id = payload.get("sub")
                    except Exception:
                        pass  # Не критично, если токен отсутствует или невалиден
                
                # Определяем тип действия
                action_map = {
                    "POST": ActionType.CREATE,
                    "PATCH": ActionType.UPDATE,
                    "PUT": ActionType.UPDATE,
                    "DELETE": ActionType.DELETE,
                }
                action = action_map.get(request.method)
                
                if action:
                    # Пытаемся логировать через сервис аудита
                    # Это делается асинхронно, чтобы не блокировать ответ
                    # В реальности лучше использовать отдельную задачу или очередь
                    try:
                        from app.infrastructure.db.base import AsyncSessionLocal
                        from app.domain.services.audit_service import AuditService
                        from uuid import UUID
                        
                        # Извлекаем entity_type и entity_id из пути
                        parts = path.strip("/").split("/")
                        if len(parts) >= 2:
                            entity_type = parts[1].rstrip("s")  # objects -> object
                            entity_id_str = parts[2] if len(parts) > 2 else None
                            
                            if entity_id_str:
                                try:
                                    entity_id = UUID(entity_id_str)
                                    async with AsyncSessionLocal() as session:
                                        audit_service = AuditService(session)
                                        
                                        # Для POST - логируем создание
                                        if action == ActionType.CREATE:
                                            # Получаем данные из ответа (если есть)
                                            try:
                                                body = await response.body()
                                                if body:
                                                    data = json.loads(body)
                                                    after = data if isinstance(data, dict) else {"id": str(entity_id)}
                                                else:
                                                    after = {"id": str(entity_id)}
                                                
                                                # Маскируем PII поля
                                                after = _mask_pii_in_dict(after)
                                            except:
                                                after = {"id": str(entity_id)}
                                            
                                            await audit_service.log_create(
                                                entity_type=entity_type,
                                                entity_id=entity_id,
                                                actor_id=UUID(user_id) if user_id else None,
                                                after=after,
                                                ip_address=request.client.host if request.client else None,
                                                user_agent=request.headers.get("user-agent"),
                                            )
                                            await session.commit()
                                except (ValueError, TypeError):
                                    pass  # Не критично, если не удалось распарсить ID
                    except Exception:
                        pass  # Не блокируем ответ при ошибках аудита
            except Exception:
                pass  # Не блокируем ответ при любых ошибках
        
        return response

