"""
Валидация загружаемых файлов
"""
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException

from app.core.config import settings


# Белый список MIME типов
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-excel",  # .xls
    "text/csv",
    "application/json",
}

# Расширения файлов
ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".pdf",
    ".xlsx", ".xls", ".csv",
    ".json",
}


def validate_file_size(file: UploadFile) -> None:
    """Проверить размер файла"""
    # В продакшене нужно читать файл порциями и проверять размер
    # Здесь упрощённая версия
    if file.size and file.size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
        )


def validate_file_type(file: UploadFile) -> None:
    """Проверить тип файла по MIME и расширению"""
    # Проверка по MIME типу
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"File type not allowed: {file.content_type}. Allowed: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    # Проверка по расширению
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"File extension not allowed: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )


async def calculate_file_hash(content: bytes) -> str:
    """Вычислить SHA-256 хэш файла"""
    return hashlib.sha256(content).hexdigest()


async def validate_and_store_file(
    file: UploadFile,
    storage_path: Path,
    quarantine: bool = False,
) -> tuple[Path, str]:
    """
    Валидировать и сохранить файл
    
    Args:
        file: Загруженный файл
        storage_path: Путь для сохранения
        quarantine: Поместить в карантин (для подозрительных файлов)
    
    Returns:
        (path, hash): Путь к сохранённому файлу и его хэш
    """
    # Валидация размера
    validate_file_size(file)
    
    # Валидация типа
    validate_file_type(file)
    
    # Читаем содержимое
    content = await file.read()
    
    # Вычисляем хэш
    file_hash = await calculate_file_hash(content)
    
    # Определяем путь сохранения
    if quarantine:
        save_dir = storage_path / "quarantine"
    else:
        save_dir = storage_path
    
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Генерируем имя файла (hash + оригинальное расширение)
    ext = Path(file.filename or "file").suffix
    filename = f"{file_hash}{ext}"
    file_path = save_dir / filename
    
    # Сохраняем файл
    file_path.write_bytes(content)
    
    return file_path, file_hash

