"""
Общие схемы для field-level RBAC
"""
from typing import Any, Optional
from pydantic import BaseModel, field_serializer
from uuid import UUID


def mask_phone(phone: Optional[str], should_mask: bool = True) -> Optional[str]:
    """Маскирование телефона для PII"""
    if not phone or not should_mask:
        return phone
    
    if len(phone) <= 4:
        return "****"
    
    # Маскируем середину: +7 (912) 345-67-89 -> +7 (***) ***-**89
    return phone[:5] + "***-**" + phone[-2:]


def mask_email(email: Optional[str], should_mask: bool = True) -> Optional[str]:
    """Маскирование email для PII"""
    if not email or not should_mask:
        return email
    
    parts = email.split("@")
    if len(parts) != 2:
        return email
    
    username, domain = parts
    if len(username) <= 2:
        masked_username = "**"
    else:
        masked_username = username[:2] + "***"
    
    return f"{masked_username}@{domain}"


class PIIFieldsMixin(BaseModel):
    """Миксин для маскирования PII полей"""
    
    def mask_pii(self, has_access: bool = False) -> "PIIFieldsMixin":
        """Маскировать PII поля если нет доступа"""
        if has_access:
            return self
        
        data = self.model_dump()
        
        # Маскируем телефон
        if "phone" in data and data["phone"]:
            data["phone"] = mask_phone(data["phone"])
        
        # Маскируем email (если есть)
        if "email" in data and data["email"]:
            data["email"] = mask_email(data["email"])
        
        # Создаём новый экземпляр с замаскированными данными
        return self.__class__(**data)

