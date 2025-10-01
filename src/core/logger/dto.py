from pathlib import Path
from dataclasses import dataclass
from typing import Tuple

from src.core.logger.enums import LogFormats


@dataclass
class LogFormatDTO:
    datetime_format: str = "%d.%m.%Y %H:%M"
    separator: str = " - "
    entry_format: Tuple[LogFormats, ...] = (LogFormats.TIME, LogFormats.NAME, LogFormats.LEVEL, LogFormats.MESSAGE)


@dataclass
class LogsFolderDTO:
    path: Path
    name: Path = Path("logs")
