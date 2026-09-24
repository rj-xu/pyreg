from abc import ABC, abstractmethod
from enum import IntEnum, IntFlag
from typing import Final, Self, overload, override

from loguru import logger

from pyreg.endian import Endian

from .mask import Bit, Mask
from .reg import RegRoNum, RegRwNum


class Field[T, R: RegRoNum | RegRwNum = RegRoNum](ABC):
    @overload
    def __init__(self, s: int | tuple[int, int], *, byte: int = 0) -> None: ...
    @overload
    def __init__(self, s: int, l: int, *, byte: int = 0) -> None: ...
    @overload
    def __init__(self, *, l: int | None = None, byte: int = 0) -> None: ...
    def __init__(self, s: int | tuple[int, int] | None = None, l: int | None = None, *, byte: int = 0) -> None:
        self.mask: Final = Mask.new(last_s=s, l=l, byte=byte)

    def __set_name__(self, owner: type[R], name: str) -> None:
        self.name: str = name

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...
    @overload
    def __get__(self, instance: R, owner: type) -> T: ...
    @abstractmethod
    def __get__(self, instance: R | None, owner: type) -> T | Self: ...

    @abstractmethod
    def __set__(self, instance: RegRwNum, val: T) -> None: ...


class BitField(Field[int]):
    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...
    @overload
    def __get__(self, instance: RegRoNum, owner: type) -> int: ...
    @override
    def __get__(self, instance: RegRoNum | None, owner: type) -> int | Self:
        if instance is None:
            return self
        val = instance.read(self.mask)
        logger.info(f"Read Reg {instance.name}.{self.name} = {val:#x}")
        return val

    @override
    def __set__(self, instance: RegRwNum, val: int):
        logger.info(f"Write Reg {instance.name}.{self.name} = {val:#x}")
        instance.modify(val, self.mask)


class BitCross16(Field[int]):
    def __init__(self, *, byte: int, bit_len: int):
        assert 8 < bit_len < 16
        super().__init__(l=16, byte=byte)
        self.le_mask = Bit(0, bit_len)
        self.mask_high = Bit(self.mask.s, bit_len - 8)
        self.mask_low = Bit(self.mask.s + 8, 8)

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...
    @overload
    def __get__(self, instance: RegRoNum, owner: type) -> int: ...
    @override
    def __get__(self, instance: RegRoNum | None, owner: type) -> int | Self:
        if instance is None:
            return self
        val = instance.read(self.mask)
        val = Endian.int_to_int(val, width=16)
        val = self.le_mask.extract(val)
        logger.info(f"Read Reg {instance.name}.{self.name} = {val:#x}")
        return val

    @override
    def __set__(self, instance: RegRwNum, val: int):
        logger.info(f"Write Reg {instance.name}.{self.name} = {val:#x}")
        val = self.le_mask.get(val)
        rv = instance.read()
        wv = self.mask_high.insert(rv, val >> 8)
        wv = self.mask_low.insert(wv, val)
        instance.write(wv)


class BitTrigger(Field["BitTrigger", RegRwNum]):
    @override
    def __get__(self, instance: RegRwNum | None, owner: type) -> Self:
        if instance is None:
            return self
        if not getattr(self, "_instance", False):
            self._instance = instance
        return self

    @override
    def __set__(self, instance: RegRwNum, val: Self) -> None:
        raise NotImplementedError

    def trigger(self, *, trig0: int = 1, trig1: int = 0):
        logger.info(f"Trigger {self._instance.name}.{self.name}: {trig0} -> {trig1}")
        rv = self._instance.read()
        wv0 = self.mask.insert(rv, trig0)
        wv1 = self.mask.insert(rv, trig1)
        self._instance.write(wv0)
        self._instance.write(wv1)


class BitEnum[E: IntEnum | IntFlag](Field[E]):
    @overload
    def __init__(self, s: int | tuple[int, int], *, byte: int = 0, T: type[E]) -> None: ...  # noqa: N803
    @overload
    def __init__(self, s: int, l: int, *, byte: int = 0, T: type[E]) -> None: ...  # noqa: N803
    @overload
    def __init__(self, *, l: int | None = None, byte: int = 0, T: type[E]) -> None: ...  # noqa: N803

    def __init__(
        self,
        s: int | tuple[int, int] | None = None,
        l: int | None = None,
        *,
        byte: int = 0,
        T: type[E],  # noqa: N803
    ) -> None:
        super().__init__(s=s, l=l, byte=byte)  # pyright: ignore[reportArgumentType]  # ty: ignore[invalid-argument-type]
        self.T: Final = T

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...
    @overload
    def __get__(self, instance: RegRoNum, owner: type) -> E: ...
    @override
    def __get__(self, instance: RegRoNum | None, owner: type) -> E | Self:
        if instance is None:
            return self

        val = self.T(instance.read(self.mask))
        logger.info(f"Read {instance.name}.{self.name} = {val.name}")
        return val

    @override
    def __set__(self, instance: RegRwNum, val: E):
        logger.info(f"Write {instance.name}.{self.name} = {val.name}")
        instance.modify(val, self.mask)


class BitBool(Field[bool]):
    def __init__(self, s: int, *, byte: int = 0):
        super().__init__(s, byte=byte)

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...
    @overload
    def __get__(self, instance: RegRoNum, owner: type) -> bool: ...
    @override
    def __get__(self, instance: RegRoNum | None, owner: type) -> bool | Self:
        if instance is None:
            return self
        val = bool(instance.read(self.mask))
        logger.info(f"Read {instance.name}.{self.name} = {val}")
        return val

    @override
    def __set__(self, instance: RegRwNum, val: bool):
        logger.info(f"Write {instance.name}.{self.name} = {val}")
        instance.modify(int(val), self.mask)


class BitRsvd(Field[None]):
    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...
    @overload
    def __get__(self, instance: RegRoNum, owner: type) -> None: ...
    @override
    def __get__(self, instance: RegRoNum | None, owner: type) -> Self | None:
        if instance is None:
            return self
        raise NotImplementedError

    @override
    def __set__(self, instance: RegRwNum | None, val: None) -> None:
        raise NotImplementedError


class BitConst[T](Field[T]):
    def __init__(self, const: T) -> None:
        super().__init__(s=0, l=1, byte=0)
        self.const: Final = const

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...
    @overload
    def __get__(self, instance: RegRoNum, owner: type) -> T: ...
    @override
    def __get__(self, instance: RegRoNum | None, owner: type) -> T | Self:
        if instance is None:
            return self
        return self.const

    @override
    def __set__(self, instance: RegRwNum | None, val: T) -> None:
        pass
