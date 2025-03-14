from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import loguru


@runtime_checkable
class LoggerProtocol(Protocol):
    def trace(self, message: str) -> None: ...
    def debug(self, message: str) -> None: ...
    def info(self, message: str) -> None: ...
    def warning(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...


@dataclass
class Logger:
    _logger: LoggerProtocol

    def __init__(self):
        loguru.logger.remove()
        loguru.logger.add(lambda msg: print(msg, end=""), level="TRACE")
        assert isinstance(loguru.logger, LoggerProtocol)
        self._logger = loguru.logger

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger: LoggerProtocol):
        assert isinstance(loguru.logger, LoggerProtocol)
        self._logger = logger


logger = Logger().logger
