from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from pathlib import Path
from typing import ClassVar

from .bit import Bits
from .endian import ByteT, Endian


@dataclass
class Device(ABC):
    name: str

    @abstractmethod
    def read(self, addr: int, width: int) -> int: ...

    @abstractmethod
    def write(self, addr: int, val: int, width: int) -> None: ...

    def burst_read(self, addr: int, size: int) -> bytes:
        return bytes([self.read(addr + i, 1) for i in range(size)])

    def burst_write(self, addr: int, vals: ByteT) -> None:
        for i, v in enumerate(vals):
            self.write(addr + i, v, 1)


@dataclass
class DummyDevice(Device):
    def read(self, addr: int, width: int) -> int:  # noqa: ARG002
        return 0

    def write(self, addr: int, val: int, width: int) -> None:  # noqa: ARG002
        return None


@dataclass
class IptDevice(Device):
    class Board(IntEnum):
        GAIA = 0x64
        VENUS = 0x6C

    device_id: Board = Board.VENUS
    ipt: ClassVar = field(init=False)

    def read(self, addr: int, width: int) -> int:
        # NOTE: dataWidth won't work!!!
        b = bytearray(width)
        for i in range(width):
            b[i], rs = self.ipt.read(i2cid=self.device_id, addr=addr + i, dataWidth=Bits.PER_BYTE)
            if rs is False:
                raise RuntimeError
        val = Endian.LITTLE.bytes_to_int(b)
        return val

    def write(self, addr: int, val: int, width: int) -> None:
        b = Endian.LITTLE.int_to_bytes(val)
        for i in range(width):
            ret = self.ipt.write(i2cid=self.device_id, addr=addr + i, dat=b[i], dataWidth=Bits.PER_BYTE)
            if ret is False:
                raise RuntimeError

    def burst_read(self, addr: int, size: int) -> bytes:
        b = bytearray(size)
        for i in range(size):
            b[i], rs = self.ipt.read(i2cid=self.device_id, addr=addr + i, dataWidth=Bits.PER_BYTE)
            if rs is False:
                raise RuntimeError
        return bytes(b)

    def burst_write(self, addr: int, vals: ByteT) -> None:
        for i, v in enumerate(vals):
            ret = self.ipt.write(i2cid=self.device_id, addr=addr + i, dat=v, dataWidth=Bits.PER_BYTE)
            if ret is False:
                raise RuntimeError


@dataclass
class BinFile(Device):
    FILE: Path
    OFFSET: int = 0
    BIN: bytes = field(init=False)

    new_file: Path = field(init=False)
    new_bin: bytearray = field(init=False)

    def __post_init__(self) -> None:
        with self.FILE.open(mode="rb") as fp:
            self.BIN = fp.read()

    def new(self) -> None:
        self.new_bin = bytearray(self.BIN)

    def save(self, new_file: Path) -> None:
        with new_file.open(mode="wb") as fp:
            fp.write(self.new_bin)

    def read(self, addr: int, width: int) -> int:
        b = self.BIN[self.OFFSET + addr : self.OFFSET + addr + width]
        val = Endian.LITTLE.bytes_to_int(b)
        return val

    def write(self, addr: int, val: int, width: int) -> None:
        b = Endian.LITTLE.int_to_bytes(val)
        for i in range(width):
            self.new_bin[self.OFFSET + addr + i] = b[i]

    def burst_read(self, addr: int, size: int) -> bytes:
        b = self.BIN[self.OFFSET + addr : self.OFFSET + addr + size]
        return bytes(b)

    def burst_write(self, addr: int, vals: ByteT) -> None:
        for i, v in enumerate(vals):
            self.new_bin[self.OFFSET + addr + i] = v


class DeviceTable(Enum):
    DUMMY = DummyDevice("DUMMY")
    X3N = IptDevice("X3N")
    X3G = IptDevice("X3G")


device: DeviceTable = DeviceTable.X3N
