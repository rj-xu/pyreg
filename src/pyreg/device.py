from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from pyreg.bit import ByteT


@dataclass
class Device(ABC):
    name: str

    @abstractmethod
    def read(self, addr: int, width: int) -> int: ...

    @abstractmethod
    def write(self, addr: int, val: int, width: int) -> None: ...

    def burst_read(self, addr: int, size: int) -> list[int]:
        return [self.read(addr + i, 1) for i in range(size)]

    def burst_write(self, addr: int, vals: ByteT) -> None:
        for i, v in enumerate(vals):
            self.write(addr + i, v, 1)


@dataclass
class DummyDevice(Device):
    def read(self, addr: int, width: int) -> int:  # noqa: ARG002
        return 0

    def write(self, addr: int, val: int, width: int) -> None:  # noqa: ARG002
        return None


# @dataclass
# class IptDevice(Device):
#     from Libs.ipt import IPTDev, g_ipt

#     class Board(IntEnum):
#         GAIA = 0x64
#         VENUS = 0x6C

#     device_id: Board = Board.VENUS
#     ipt: IPTDev = g_ipt

#     def read(self, addr: int, width: int) -> int:
#         val, rs = self.ipt.read(i2cid=self.device_id, addr=addr, dataWidth=width * Bits.BYTE_1)
#         if rs is False:
#             raise RuntimeError
#         return val

#     def write(self, addr: int, val: int, width: int) -> None:
#         ret = self.ipt.write(i2cid=self.device_id, addr=addr, dat=val, dataWidth=width * Bits.PER_BYTE)
#         if ret is False:
#             raise RuntimeError


class DeviceTable(Enum):
    DUMMY = DummyDevice("DUMMY")
    # X3N = IptDevice("X3N")
    # X3G = IptDevice("X3G")


device: DeviceTable = DeviceTable.DUMMY
