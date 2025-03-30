from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import ClassVar

from .bit import Bits
from .endian import ByteT


@dataclass
class Device(ABC):
    name: str

    @abstractmethod
    def read(self, addr: int, size: int) -> bytes: ...

    @abstractmethod
    def write(self, addr: int, val: ByteT) -> None: ...

    def burst_read(self, addr: int, size: int) -> bytes:
        return b"".join(self.read(addr + i, 1) for i in range(size))

    def burst_write(self, addr: int, vals: ByteT) -> None:
        for i in range(len(vals)):
            self.write(addr + i, vals[i : i + 1])


@dataclass
class DummyDevice(Device):
    def read(self, addr: int, size: int) -> bytes:
        return b"\xff" * size

    def write(self, addr: int, val: ByteT) -> None:
        return None


@dataclass
class IptDevice(Device):
    class Board(IntEnum):
        GAIA = 0x64
        VENUS = 0x6C

    device_id: Board = Board.VENUS
    ipt: ClassVar = field(init=False)

    def read(self, addr: int, size: int) -> bytes:
        # NOTE: dataWidth won't work!!!
        b = bytearray(size)
        for i in range(size):
            b[i], rs = self.ipt.read(
                i2cid=self.device_id, addr=addr + i, dataWidth=Bits.PER_BYTE
            )
            if rs is False:
                raise RuntimeError
        return bytes(b)

    def write(self, addr: int, val: ByteT) -> None:
        for i, v in enumerate(val):
            ret = self.ipt.write(
                i2cid=self.device_id, addr=addr + i, dat=v, dataWidth=Bits.PER_BYTE
            )
            if ret is False:
                raise RuntimeError


class DeviceTable(Enum):
    DUMMY = DummyDevice("DUMMY")
    X3N = IptDevice("X3N")
    X3G = IptDevice("X3G")


current_device: DeviceTable = DeviceTable.X3N
