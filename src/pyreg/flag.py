from enum import IntFlag
from functools import cache
from typing import Self, overload

from loguru import logger

from config.err_id import ErrId
from utils.types import BIT_RANGE

from .reg import RegRoNum, RegRwNum


class FlagRo(IntFlag):
    reg: RegRoNum  # pyright: ignore[reportUninitializedInstanceVariable]

    @classmethod
    def flag(cls) -> Self:
        f = cls(cls.reg.read())
        logger.info(f"{cls.__name__}: {f.name} ")
        return f

    def is_set(self) -> bool:
        return self in self.flag()

    def is_clear(self) -> bool:
        return self not in self.flag()

    @classmethod
    @cache
    def sum(cls):
        valid_flags = (i for i in cls if i.name is not None and not i.name.startswith(("RSVD", "RESERVED")))
        return cls(sum(valid_flags))

    @property
    def err_id(self) -> ErrId:
        bit_pos = self.value.bit_length() - 1
        if bit_pos > 7:
            actual_addr = self.reg.addr + (bit_pos // 8)
            actual_bit = bit_pos % 8
        else:
            actual_addr = self.reg.addr
            actual_bit = bit_pos
        assert actual_bit in BIT_RANGE
        return ErrId(actual_addr, actual_bit)


class FlagRw(FlagRo):
    reg: RegRwNum  # pyright: ignore[reportIncompatibleVariableOverride]

    def set(self) -> None:
        val = self.flag() | self
        self.reg.write(val)

    def clear(self) -> None:
        val = self.flag() & ~self
        self.reg.write(val)

    def toggle(self) -> None:
        val = self.flag() ^ self
        self.reg.write(val)

    @classmethod
    def all_set(cls) -> None:
        cls.reg.write(cls.sum())

    @classmethod
    def all_clear(cls) -> None:
        cls.reg.write(0)

    def trigger(self) -> None:
        self.set()
        self.clear()

    def clear_and_set(self) -> None:
        self.reg.write(self)

    def clear_and_trigger(self) -> None:
        self.clear_and_set()
        self.all_clear()


@overload
def Flag(reg: RegRwNum) -> type[FlagRw]: ...  # pylint: disable=invalid-name
@overload
def Flag(reg: RegRoNum) -> type[FlagRo]: ...  # pylint: disable=invalid-name
def Flag(reg: RegRoNum | RegRwNum) -> type[FlagRo | FlagRw]:  # noqa: N802 # pylint: disable=invalid-name
    if isinstance(reg, RegRwNum):

        class _FlagRw(FlagRw): ...

        _FlagRw.reg = reg
        return _FlagRw

    class _FlagRo(FlagRo): ...

    _FlagRo.reg = reg
    return _FlagRo
