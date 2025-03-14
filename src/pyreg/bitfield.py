from dataclasses import KW_ONLY, InitVar, dataclass, field
from typing import Any, Callable

from pyreg.log import logger

type BitfieldT = int | tuple[int, int] | list[int] | Bitfield


@dataclass
class Bitfield:
    bitfield: int | tuple[int, int] | list[int]

    name: str = ""

    _: KW_ONLY
    base: InitVar[int] = 0

    s: int = field(init=False)
    l: int = field(init=False)

    def __post_init__(self, base: int):
        match self.bitfield:
            case int():
                s = self.bitfield
                l = 1
            case tuple():
                if len(self.bitfield) != 2:
                    raise ValueError
                s = self.bitfield[0]
                l = self.bitfield[1]
            case list():
                if len(self.bitfield) != 2 or self.bitfield[0] > self.bitfield[1]:
                    raise ValueError

                s = self.bitfield[0]
                l = self.bitfield[1] - self.bitfield[0] + 1
        self.s = s
        self.l = l

    @property
    def mask(self) -> int:
        return ((1 << self.l) - 1) << self.s

    def get(self, val: int) -> int:
        return (val >> self.s) & ((1 << self.l) - 1)

    def set(self, val: int, v: int) -> int:
        return (val & ~self.mask) | ((v & ((1 << self.l) - 1)) << self.s)

    def __set_name__(self, owner: type, name: str):
        self.name = name

    def __get__(self, instance: Any, owner: type):
        if instance is None:
            logger.error("DO NOT use this field as a class attribute")
            raise AttributeError

        val = instance.read(self)
        logger.trace(f"Read {self.name}")
        return val

    def __set__(self, instance: Any, value: int):
        if instance is None:
            logger.error("DO NOT use this field as a class attribute")
            raise AttributeError

        logger.trace(f"Write {self.name}")
        instance.write(value, self)

    def __call__(self, _func: Callable[[], None]):
        # 实现装饰器功能
        return self
