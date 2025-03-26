from dataclasses import KW_ONLY, dataclass
from enum import IntFlag

from .access import AccessMode
from .bit_field import BitRange
from .device import Device, DeviceTable
from .endian import Endian
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
    mode: AccessMode = AccessMode.R | AccessMode.W
    default: bytes = b"\x00\x00\x00\x00"
    endian: Endian = Endian.LITTLE
    width: int = 4
    device: Device = DeviceTable.X3N.value

    def check_read(self) -> None:
        if not self.mode.is_readable:
            raise ValueError

    def check_write(self) -> None:
        if not self.mode.is_writable:
            raise ValueError

    def read(
        self,
        bf: BitRangeT | BitRange | None = None,
        # set_mask: int | None = None,
        # clear_mask: int | None = None,
    ) -> int:
        self.check_read()

        val = self.device.value.read(self.addr, self.size)

        # if set_mask and not Mask(set_mask).is_set(val):
        #     raise RegSetError(f"Reg {self.addr:#4x} not set")
        # if clear_mask and not Mask(clear_mask).is_clear(val):
        #     raise RegClearError(f"Reg {self.addr:#4x} not clear")
        if bf:
            if not isinstance(bf, BitRange):
                bf = BitRange(bf)
            val = bf.get_field(val)

        if self.endian.is_big:
            val = Endian.BIG.int_to_int(val)

        logger.trace(f"Read Reg: {self.addr:#10x} {val:#04x}")

        return val

    def read_bytes(self, size: int | None = None) -> bytes:
        self.check_read()
        size = size or self.size
        b = self.device.value.burst_read(self.addr, size)
        if self.endian.is_big:
            return self.endian.bytes_to_bytes(b)
        return b

    def write(
        self,
        val: int = 0,
        bf: BitRangeT | BitRange | None = None,
        set_mask: int | None = None,
        clear_mask: int | None = None,
    ) -> None:
        self.check_write()

        if bf or set_mask or clear_mask:
            rv = self.read()
            if bf:
                if not isinstance(bf, BitRange):
                    bf = BitRange(bf)
                rv = bf.set_field(rv, val)
            if set_mask:
                rv = Mask(set_mask).set(rv)
            if clear_mask:
                rv = Mask(clear_mask).clear(rv)
            val = rv

        if self.endian.is_big:
            val = Endian.BIG.bytes_to_int(bytes(val))

        logger.trace(f"Write Reg {self.addr:#010x}: {val:#04x}")

        return self.device.value.write(self.addr, val, self.size)

    def write_bytes(self, vals: bytes | bytearray) -> None:
        assert len(vals) <= self.size
        if len(vals) != self.size:
            logger.warning(f"Write only {len(vals)} bytes for Reg {self.addr} ")
        self.device.value.burst_write(self.addr, vals)


@dataclass
class RegRo(Reg):
    mode = AccessMode.R


@dataclass
class RegWo(Reg):
    mode = AccessMode.W


@dataclass
class RegRw(Reg):
    mode = AccessMode.R | AccessMode.W


@dataclass
class Flags[T: IntFlag](RegRo):
    @property
    def flags(self) -> T:
        val = self.read()
        enum_type: type[T] = self.__orig_class__.__args__[0]  # type: ignore
        return enum_type(val)

    def is_set(self, flag: T) -> bool:
        return bool(self.flags & flag)

    def is_clear(self, flag: T) -> bool:
        return not self.is_set(flag)
