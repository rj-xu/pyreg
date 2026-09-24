from dataclasses import dataclass
from enum import IntEnum, IntFlag
from typing import Final

from .reg import RegRo, RegRoNum, RegRw, RegRwNum


@dataclass(kw_only=True)
class RegEnumRw[E: IntEnum | IntFlag](RegRwNum):
    T: Final[type[E]]

    @property
    def value(self) -> E:
        return self.T(self.read())

    @value.setter
    def value(self, val: E) -> None:
        self.write(val.value)


@dataclass(kw_only=True)
class RegEnumRo[E: IntEnum | IntFlag](RegRoNum):
    T: Final[type[E]]

    @property
    def value(self) -> E:
        return self.T(self.read())


@dataclass(kw_only=True)
class RegBoolRw(RegRwNum):
    @property
    def value(self) -> bool:
        return bool(self.read())

    @value.setter
    def value(self, val: bool) -> None:
        self.write(val)


@dataclass(kw_only=True)
class RegBoolRo(RegRoNum):
    @property
    def value(self) -> bool:
        return bool(self.read())


class RegConstRo[T](RegRo):
    def __init__(self, const: T, size: int) -> None:
        super().__init__(addr=0xFFFF, size=size)
        self._const: Final = const

    @property
    def value(self) -> T:
        return self._const


class RegConstRw[T](RegRw):
    def __init__(self, const: T, size: int) -> None:
        super().__init__(addr=0xFFFF, size=size)
        self._const: Final = const

    @property
    def value(self) -> T:
        return self._const

    @value.setter
    def value(self, val: T) -> None:
        pass
