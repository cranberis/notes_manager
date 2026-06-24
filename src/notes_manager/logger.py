import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging() -> None:
    """Настройка логирования для всего приложения."""
    # Создание папки и файла для записи логов
    file_path = Path('logs/app.log')
    file_path.parent.mkdir(parents=True, exist_ok=True)
        
    # Получение корневого логера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Для логирования в файл c ротацией лог-файлов
    file_handler = RotatingFileHandler(file_path,
                                       maxBytes=1024*1024,
                                       backupCount=3)
    file_formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    
    # Для логирования в консоль
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)


if __name__ == "__main__":
    
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.debug("Уровень DEBUG, отображение только в лог-файле")
    logger.info("Уровень INFO, отображение в лог-файле и в консоли")