from typing import ClassVar

from loguru import logger


class Module:
    BASE: ClassVar[int]

    def __init_subclass__(cls):
        assert getattr(cls, "BASE", False)
        logger.info(f"Mod {cls.__name__} based on 0x{cls.BASE:04X} ({cls.__module__})")


print()
