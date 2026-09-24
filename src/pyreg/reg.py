from abc import ABC
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import cached_property
from typing import TYPE_CHECKING, ClassVar, Literal, override

from loguru import logger

from utils.types import Bytes, Width, bytes_to_str, int_to_hex

from .debugger import Debugger
from .endian import Endian

if TYPE_CHECKING:
    from .mask import Mask


class Access(Enum):
    RO = auto()
    WO = auto()
    RW = auto()
    SV = auto()
    DY = auto()


@dataclass
class Reg(ABC):
    access: ClassVar[Access]
    addr: int
    size: int
    name: str = field(init=False)

    def __post_init__(self) -> None:
        self.name = f"Reg{self.access.name}[0x{self.addr:04_X}, {self.size}]"

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"{owner.__name__}.{name} " + self.name

    @override
    def __repr__(self) -> str:
        return self.name


@dataclass
class RegRo(Reg):
    access = Access.RO

    def read_bytes(self, size: int | None = None, *, offset: int = 0) -> bytes:
        size = size if size is not None else self.size
        str_offset = f"@0x{offset:04x}" if offset else ""
        val = Debugger.burst_read(addr=self.addr + offset, size=size)

        logger.debug(f"Read bytes {self.name}{str_offset} = b'{val.hex()}'")
        return val

    def show(self):
        logger.info(f"{self.name}:")
        val = self.read_bytes()
        s = bytes_to_str(val)
        logger.info(s)

    def dump(self, *, size: int | None = None, is_be: bool | None = None, width: Width = 32):
        size = self.size if size is None else size

        step = width // 8
        for i in range(0, size, step):
            addr = self.addr + i
            val = Debugger.burst_read(addr=addr, size=step)
            if is_be:
                val = val[::-1]
            logger.info(f"{self.name} {addr:#06X} = 0x{val.hex()}")


class RegWo(Reg):
    access = Access.WO

    def write_bytes(self, val: Bytes, *, offset: int = 0) -> None:
        size = offset + len(val)
        assert size <= self.size
        str_offset = f"@0x{offset:04x}" if offset else ""
        if size != self.size:
            logger.warning(f"Write only {len(val)}/{self.size}{str_offset} bytes to {self.name}")
        logger.debug(f"Write bytes {self.name}{str_offset} = b'{val.hex()}'")
        Debugger.burst_write(addr=self.addr + offset, val=val)

    def all_set(self) -> None:
        self.write_bytes(b"\xff" * self.size)

    def all_clear(self) -> None:
        self.write_bytes(b"\x00" * self.size)

    def fill(self, val: bytes):
        val_size = len(val)

        if val_size == 0:
            raise ValueError

        if val_size > self.size:
            self.write_bytes(val[: self.size])
            return

        full_repeats, remainder = divmod(self.size, val_size)
        fill_data = (val * full_repeats) + val[:remainder]
        self.write_bytes(fill_data)


class RegRw(RegRo, RegWo):
    access = Access.RW


class RegSv(Reg):
    access = Access.SV


@dataclass
class RegDy(RegRw):
    access = Access.DY

    is_read: bool = True
    is_write: bool = True

    @override
    def read_bytes(self, size: int | None = None, *, offset: int = 0) -> bytes:
        assert self.is_read
        return super().read_bytes(size, offset=offset)

    @override
    def write_bytes(self, val: Bytes, *, offset: int = 0) -> None:
        assert self.is_write
        super().write_bytes(val, offset=offset)


@dataclass
class RegNum(Reg, ABC):
    size: Literal[1, 2, 4]  # pyright: ignore[reportIncompatibleVariableOverride]
    is_be: bool = False

    def __post_init__(self):
        super().__post_init__()
        if self.is_be:
            self.name += "(BE)"

    @cached_property
    def endian(self) -> Endian:
        return Endian.BIG if self.is_be else Endian.LITTLE

    @cached_property
    def width(self) -> Width:
        return self.size * 8


@dataclass
class RegRoNum(RegRo, RegNum):
    def read(self, mask: Mask | None = None) -> int:
        val = Debugger.read(addr=self.addr, width=self.width)
        if self.is_be:
            val = Endian.int_to_int(val, width=self.width)
        logger.debug(f"Read {self.name} = {int_to_hex(val, width=self.width, sep=True)}")
        if mask is not None:
            val = mask.extract(val)
        return val


@dataclass
class RegWoNum(RegWo, RegNum):
    def write(self, val: int) -> None:
        if self.is_be:
            val = Endian.int_to_int(val, width=self.width)
        logger.debug(f"Write {self.name} = {int_to_hex(val, width=self.width, sep=True)}")
        return Debugger.write(addr=self.addr, val=val, width=self.width)

    def trigger(self, val0: int = 1, val1: int = 0) -> None:
        self.write(val0)
        self.write(val1)


class RegRwNum(RegRoNum, RegWoNum):
    access = Access.RW

    @override
    def write(self, val: int, *, read_back: bool = False) -> None:
        super().write(val)
        if read_back:
            assert val == self.read()

    def modify(self, val: int, mask: Mask, *, read_back: bool = False) -> None:
        rv = self.read()
        wv = mask.insert(rv, val)
        return self.write(wv, read_back=read_back)

    def set_mask(self, mask: Mask) -> None:
        rv = self.read()
        if not mask.is_set(rv):
            self.write(mask.set(rv))

    def clear_mask(self, mask: Mask) -> None:
        rv = self.read()
        if not mask.is_clear(rv):
            self.write(mask.clear(rv))

    def trigger_mask(self, mask: Mask) -> None:
        rv = self.read()
        wv0 = mask.set(rv)
        wv1 = mask.clear(rv)
        self.write(wv0)
        self.write(wv1)


@dataclass
class RegRw8(RegRwNum):
    size: Literal[1, 2, 4] = field(init=False, default=1)


@dataclass
class RegRo8(RegRoNum):
    size: Literal[1, 2, 4] = field(init=False, default=1)


@dataclass
class RegWo8(RegWoNum):
    size: Literal[1, 2, 4] = field(init=False, default=1)


@dataclass
class RegRw16(RegRwNum):
    size: Literal[1, 2, 4] = field(init=False, default=2)


@dataclass
class RegRo16(RegRoNum):
    size: Literal[1, 2, 4] = field(init=False, default=2)


@dataclass
class RegWo16(RegWoNum):
    size: Literal[1, 2, 4] = field(init=False, default=2)


@dataclass
class RegRw32(RegRwNum):
    size: Literal[1, 2, 4] = field(init=False, default=4)


@dataclass
class RegRo32(RegRoNum):
    size: Literal[1, 2, 4] = field(init=False, default=4)


@dataclass
class RegWo32(RegWoNum):
    size: Literal[1, 2, 4] = field(init=False, default=4)
