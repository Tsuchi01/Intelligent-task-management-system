import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Налаштовує логування з файлами, кольорами та змінною LOG_LEVEL."""

    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Формат повідомлень
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Обробник для файлу
    file_handler = RotatingFileHandler(
        "app.log", maxBytes=1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Обробник для консолі
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Основний логер
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()  # щоб уникнути дублювання
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
