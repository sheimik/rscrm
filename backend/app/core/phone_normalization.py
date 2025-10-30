"""
Нормализация телефонов в формате E.164
"""
import re
from typing import Optional


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    """
    Нормализовать телефон в формате E.164 (+79991234567)
    
    Поддерживает:
    - +7 (999) 123-45-67
    - 8 (999) 123-45-67
    - 89991234567
    - +79991234567
    - 79991234567
    """
    if not phone:
        return None
    
    # Убираем все символы кроме цифр и +
    cleaned = re.sub(r"[^\d+]", "", phone)
    
    # Если начинается с 8, заменяем на +7
    if cleaned.startswith("8"):
        cleaned = "+7" + cleaned[1:]
    
    # Если начинается с 7 без +, добавляем +
    if cleaned.startswith("7") and not cleaned.startswith("+7"):
        cleaned = "+" + cleaned
    
    # Проверяем формат E.164 для российских номеров
    # +7XXXXXXXXXX (11 цифр после +7)
    if not cleaned.startswith("+7"):
        return None
    
    # Убираем +7 и проверяем длину
    digits = cleaned[2:]
    if len(digits) != 10:
        return None
    
    # Проверяем, что все цифры
    if not digits.isdigit():
        return None
    
    return f"+7{digits}"


def validate_phone(phone: Optional[str]) -> bool:
    """Проверить, что телефон валиден после нормализации"""
    normalized = normalize_phone(phone)
    if not normalized:
        return False
    
    # E.164 для российских номеров: +7XXXXXXXXXX
    pattern = r"^\+7\d{10}$"
    return bool(re.match(pattern, normalized))

