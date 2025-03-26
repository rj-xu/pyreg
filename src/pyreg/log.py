from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

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
    def logger(self) -> LoggerProtocol:
        return self._logger

    @logger.setter
    def logger(self, logger: Any):
        assert isinstance(logger, LoggerProtocol)
        self._logger = logger

    def trace(self, message: str) -> None:
        return self._logger.trace(message)

    def debug(self, message: str) -> None:
        return self._logger.debug(message)

    def info(self, message: str) -> None:
        return self._logger.info(message)

    def warning(self, message: str) -> None:
        return self._logger.warning(message)

    def error(self, message: str) -> None:
        return self._logger.error(message)


logger = Logger()
