from typing import TYPE_CHECKING

from agent.device_id import Device
from config import g_config

if TYPE_CHECKING:
    from utils.types import Bytes, Width


class Debugger:
    @classmethod
    def read(cls, *, addr: int, width: Width) -> int:
        dev, addr = Device.to_dev_addr(addr)
        return g_config.agent.read(dev=dev, addr=addr, width=width)

    @classmethod
    def write(cls, *, addr: int, val: int, width: Width) -> None:
        dev, addr = Device.to_dev_addr(addr)
        g_config.agent.write(dev=dev, addr=addr, val=val, width=width)

    @classmethod
    def burst_read(cls, *, addr: int, size: int) -> bytes:
        dev, addr = Device.to_dev_addr(addr)
        return g_config.agent.burst_read(dev=dev, addr=addr, size=size)

    @classmethod
    def burst_write(cls, *, addr: int, val: Bytes) -> None:
        dev, addr = Device.to_dev_addr(addr)
        g_config.agent.burst_write(dev=dev, addr=addr, val=val)
