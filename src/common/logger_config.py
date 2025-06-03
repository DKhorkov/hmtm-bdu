from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from datetime import datetime
from pathlib import Path

from aiologger import Logger  # type: ignore[import-untyped]
from aiologger.handlers.files import AsyncFileHandler  # type: ignore[import-untyped]
from aiologger.formatters.base import Formatter   # type: ignore[import-untyped]

from src.common.constants import LOGGERS_BY_DATE, PROJECT_ROOT_FROM_COMMON as PROJECT_ROOT
from src.common.enums import Levels


async def logger(level: Levels, message: str, logger_name: str = "HMTM_BDU") -> None:
    """Асинхронный логгер с записью в файл, организованный по датам"""
    level_mapping = {
        Levels.DEBUG: DEBUG,
        Levels.INFO: INFO,
        Levels.WARNING: WARNING,
        Levels.ERROR: ERROR,
        Levels.CRITICAL: CRITICAL
    }

    formatter: Formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    current_date: str = datetime.now().strftime("%d.%m.%Y")

    log_dir = PROJECT_ROOT / "logs"  # / -> Оператор Pathlib для объединения путей
    log_dir.mkdir(mode=0o755, exist_ok=True)  # mode=(755 - владелец читает/пишет, остальные только читают)

    # Полный путь к файлу лога
    log_filename: Path = log_dir / f"{current_date}.log"

    # Закрываем логгеры для старых дат
    old_loggers = [date for date in LOGGERS_BY_DATE if date != current_date]
    for old_date_logger in old_loggers:
        old_logger = LOGGERS_BY_DATE.pop(old_date_logger)
        await old_logger.shutdown()

    # Инициализация нового логгера для текущей даты
    if current_date not in LOGGERS_BY_DATE:
        custom_logger = Logger(name=logger_name)

        # Настройка файлового обработчика
        file_handler = AsyncFileHandler(
            filename=str(log_filename),
            mode="a",  # Режим добавления в конец файла
            encoding="utf-8",
        )
        file_handler.formatter = formatter
        file_handler.level = DEBUG  # Минимальный уровень логирования

        custom_logger.add_handler(file_handler)
        LOGGERS_BY_DATE[current_date] = custom_logger
    else:
        custom_logger = LOGGERS_BY_DATE[current_date]

    log_level = level_mapping.get(level)
    if log_level is not None:
        if log_level == DEBUG:
            await custom_logger.debug(message)
        elif log_level == INFO:
            await custom_logger.info(message)
        elif log_level == WARNING:
            await custom_logger.warning(message)
        elif log_level == ERROR:
            await custom_logger.error(message)
        elif log_level == CRITICAL:
            await custom_logger.critical(message)

    else:
        await custom_logger.error(f"Недопустимый уровень логирования: {level}, сообщение: {message}")


async def shutdown_loggers():
    """Более безопасное закрытие с поэтапной очисткой"""
    for date in list(LOGGERS_BY_DATE.keys()):
        logs = LOGGERS_BY_DATE.get(date)
        if logs:
            try:
                await logs.shutdown()
            except Exception as err:
                await logger(level=Levels.CRITICAL, message=f"Shutdown error for date {date} -- {err}")
            finally:
                LOGGERS_BY_DATE.pop(date, None)  # Гарантированное удаление
