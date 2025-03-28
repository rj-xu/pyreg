from dataclasses import KW_ONLY, dataclass, field
from enum import IntFlag
from typing import Any

from .access import Access
from .device import Device, current_device
from .endian import Endian
from .field import BitMask
from .log import logger
from .mask import BitRangeT, Mask


class RegError(Exception): ...


class RegSetError(RegError): ...


class RegClearError(RegError): ...


@dataclass
class Reg:
    addr: int
    size: int = 4
    _: KW_ONLY
    mode: Access = Access.R | Access.W
    default: bytes = b"\x00\x00\x00\x00"
    endian: Endian = Endian.LITTLE
    width: int = 4
    device: Device = field(default_factory=lambda: current_device.value)

    def check_read(self) -> None:
        if not self.mode.is_readable:
            raise ValueError

    def check_write(self) -> None:
        if not self.mode.is_writable:
            raise ValueError

    def read(self, bf: BitRangeT | BitMask | None = None) -> int:
        self.check_read()

        val = self.device.read(self.addr, self.size)
        val = self.endian.bytes_to_int(val)

        if bf:
            if not isinstance(bf, BitMask):
                bf = BitMask(bf)
            val = bf.get_field(val)

        logger.trace(f"Read Reg: {self.addr:#10x} {val:#04x}")

        return val

    def check(
        self,
        bf: BitRangeT | BitMask | None = None,
        set_mask: int | None = None,
        clear_mask: int | None = None,
    ) -> tuple[int, bool, bool]:
        self.check_read()

        val = self.device.read(self.addr, self.size)
        val = self.endian.bytes_to_int(val)

        logger.trace(f"Read Reg: {self.addr:#10x} {val:#04x}")

        is_set = True
        is_clear = True
        if set_mask is not None and not Mask(set_mask).is_set(val):
            logger.warning(f"Reg {self.addr:#4x} not set")
            is_set = False
        if clear_mask is not None and not Mask(clear_mask).is_clear(val):
            logger.warning(f"Reg {self.addr:#4x} not clear")
            is_clear = False
        if bf is not None:
            if not isinstance(bf, BitMask):
                bf = BitMask(bf)
            val = bf.get_field(val)

        logger.trace(f"Check Reg: {self.addr:#10x}={val:#04x}, {is_set=}, {is_clear=}")

        return val, is_set, is_clear

    def read_bytes(self, size: int | None = None) -> bytes:
        self.check_read()
        size = size or self.size
        b = self.device.burst_read(self.addr, size)
        if self.endian.is_big:
            return self.endian.bytes_to_bytes(b)
        return b

    def write(self, val: int = 0) -> None:
        self.check_write()

        logger.trace(f"Write Reg {self.addr:#010x}: {val:#04x}")
        b = self.endian.int_to_bytes(val, self.size)
        return self.device.write(self.addr, b)

    def modify(
        self,
        val: int = 0,
        bf: BitRangeT | BitMask | None = None,
        set_mask: int | None = None,
        clear_mask: int | None = None,
    ):
        self.check_read()
        self.check_write()

        rv = self.read()
        logger.trace(f"Read Reg: {self.addr:#10x} {rv:#04x}")

        if bf is not None:
            if not isinstance(bf, BitMask):
                bf = BitMask(bf)
            rv = bf.set_field(rv, val)
        if set_mask is not None:
            rv = Mask(set_mask).set(rv)
        if clear_mask is not None:
            rv = Mask(clear_mask).clear(rv)
        val = rv

        logger.trace(f"Modify Reg {self.addr:#010x}: {val:#04x}")
        b = self.endian.int_to_bytes(val, self.size)
        return self.device.write(self.addr, b)

    def write_bytes(self, vals: bytes | bytearray) -> None:
        assert len(vals) <= self.size
        if len(vals) != self.size:
            logger.warning(f"Write only {len(vals)} bytes for Reg {self.addr} ")
        self.device.burst_write(self.addr, vals)


@dataclass
class RegRo(Reg):
    mode = Access.R


@dataclass
class RegWo(Reg):
    mode = Access.W


@dataclass
class RegRw(Reg):
    mode = Access.R | Access.W


@dataclass
class RegRsvd(Reg):
    mode = Access(0)


@dataclass
class RegFlags[T: IntFlag](RegRo):
    @property
    def flags(self) -> T:
        val = self.read()
        enum_type: type[T] = self.__orig_class__.__args__[0]  # type: ignore
        return enum_type(val)

    def is_set(self, flag: T) -> bool:
        val = self.read()
        return flag & val == flag

    def is_clear(self, flag: T) -> bool:
        val = self.read()
        return flag & val == 0
