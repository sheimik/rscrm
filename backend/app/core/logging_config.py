"""
Конфигурация логирования с loguru
"""
import sys
from loguru import logger
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = "logs/app.log"):
    """
    Настройка логирования loguru
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Путь к файлу логов
    """
    # Удаляем стандартный обработчик
    logger.remove()
    
    # Формат логов
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Консольный вывод с цветами
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # Файловый вывод
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file,
        format=log_format,
        level=log_level,
        rotation="10 MB",  # Ротация при достижении 10 MB
        retention="7 days",  # Хранить логи 7 дней
        compression="zip",  # Сжимать старые логи
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Асинхронное логирование
    )
    
    # Отдельный файл для ошибок
    error_log_file = str(log_path.parent / "error.log")
    logger.add(
        error_log_file,
        format=log_format,
        level="ERROR",
        rotation="10 MB",
        retention="30 days",  # Ошибки храним дольше
        compression="zip",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )
    
    return logger


def get_logger(name: str = None):
    """
    Получить логгер для модуля
    
    Args:
        name: Имя модуля (обычно __name__)
    
    Returns:
        Logger instance
    """
    if name:
        return logger.bind(module=name)
    return logger

