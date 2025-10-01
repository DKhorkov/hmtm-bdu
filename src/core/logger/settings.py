from pathlib import Path

from src.core.logger.dto import LogFormatDTO, LogsFolderDTO


class LoggerSettings:
    def __init__(self, log_format: LogFormatDTO, logs_folder: LogsFolderDTO):
        self.dir: Path = logs_folder.path / logs_folder.name
        self.entry_format: str = log_format.separator.join(str(arg.value) for arg in log_format.entry_format)
        self.datetime_format: str = log_format.datetime_format
        self.filename: str = "hmtm_bdu.log"
