import sys
import typing
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from loguru import logger

from . import decorator, plat

if typing.TYPE_CHECKING:
    from loguru import Record


class LogLv(StrEnum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@decorator.singleton
@dataclass
class Logger:
    BANNER = (
        r"""   ____            _       _ _    ___      _             """,
        r"""  / __ \____ ___  (_)___  (_) |  / (_)____(_)___  ____   """,
        r""" / / / / __ `__ \/ / __ \/ /| | / / / ___/ / __ \/ __ \  """,
        r"""/ /_/ / / / / / / / / / / / | |/ / (__  ) / /_/ / / / /  """,
        r"""\____/_/ /_/ /_/_/_/ /_/_/  |___/_/____/_/\____/_/ /_/   """,
    )

    FMT = "<level>[{time:YYYY-MM-DD HH:mm:ss}][{level:^8}]: {message}</level>\n"
    FMT_DEBUG = "<level>[{time:YYYY-MM-DD HH:mm:ss}][{level:^8}]: {message} ({file}:{line})</level>\n"
    LINE = "=" * 60

    level: str = LogLv.DEBUG
    filename: str = "temp"
    dir: Path | None = None
    file: Path = field(init=False)

    def __post_init__(self) -> None:
        def custom_format(record: "Record") -> str:
            match record["level"].name:
                case "TRACE":
                    return self.FMT_DEBUG
                case _:
                    return self.FMT

        logger.remove()
        logger.add(sys.stdout, format=custom_format, level=self.level)

        if self.dir:
            self.file = self.dir.joinpath(f"{plat.time_stamp()}_{self.filename}.log")
            logger.add(self.file, format=custom_format, level=self.level)

        logger.trace("This is TRACE")
        logger.debug("This is DEBUG")
        logger.info("This is INFO")
        logger.success("This is SUCCESS")
        logger.warning("This is WARNING")
        logger.error("This is ERROR")
        logger.critical("This is CRITICAL")

        logger.info(self.LINE)
        for line in self.BANNER:
            logger.info(line)
        logger.info(self.LINE)

    def rename(self, is_success: bool) -> None:
        logger.remove()
        if is_success:
            self.file.rename(self.file.with_suffix(".FAIL.log"))
        else:
            self.file.rename(self.file.with_suffix(".PASS.log"))
