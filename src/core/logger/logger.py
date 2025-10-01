from logging import DEBUG
from pathlib import Path
from typing import Optional

from aiologger import Logger as AioLogger  # type: ignore[import-untyped]
from aiologger.handlers.files import AsyncFileHandler  # type: ignore[import-untyped]
from aiologger.formatters.base import Formatter  # type: ignore[import-untyped]

from src.core.logger.enums import Levels
from src.core.logger.settings import LoggerSettings


class Logger:
    def __init__(self, settings: LoggerSettings) -> None:
        self._settings: LoggerSettings = settings
        self._logger: Optional[AioLogger] = None

    async def write_log(self, level: Levels, message: str) -> None:
        try:
            log_method = getattr(self._logger, level.value.lower())
            await log_method(message)

        except AttributeError:  # Подавление приоритета исключения при других ошибках
            pass

    async def _create_folder(self) -> None:
        self._settings.dir.mkdir(mode=0o755, exist_ok=True)

    async def init_logger(self, logger_name: str = "SERVICE") -> None:
        if self._logger:
            return

        await self._create_folder()

        log_file: Path = self._settings.dir / self._settings.filename
        self._logger = AioLogger(name=logger_name)

        file_handler: AsyncFileHandler = AsyncFileHandler(
            filename=str(log_file),
            mode="a",
            encoding="utf-8",
        )
        file_handler.formatter = Formatter(
            fmt=self._settings.entry_format,
            datefmt=self._settings.datetime_format
        )
        file_handler.level = DEBUG

        self._logger.add_handler(file_handler)

    async def shutdown(self):
        if self._logger:
            await self._logger.shutdown()
