from dataclasses import dataclass, field
from pathlib import Path

from .device import Device
from .endian import ByteT
from .log import logger


@dataclass
class Binary(Device):
    file: Path
    offset: int = 0

    bin: bytes = field(init=False)

    new_file: Path = field(init=False)
    new_bin: bytearray = field(init=False)

    def __init__(self, file: Path | None = None) -> None:
        if file is None:
            logger.warning("Binary file is not specified.")
            return
        self.load(file)

    def load(self, file: Path) -> None:
        self.file = file
        with file.open(mode="rb") as fp:
            self.bin = fp.read()

    def new(self) -> None:
        self.new_bin = bytearray(self.bin)

    def save(self, new_file: Path) -> None:
        with new_file.open(mode="wb") as fp:
            fp.write(self.new_bin)

    def read(self, addr: int, size: int) -> bytes:
        b = self.bin[self.offset + addr : self.offset + addr + size]
        return b

    def write(self, addr: int, val: ByteT) -> None:
        for i in range(len(val)):
            self.new_bin[self.offset + addr + i] = val[i]

    def burst_read(self, addr: int, size: int) -> bytes:
        b = self.bin[self.offset + addr : self.offset + addr + size]
        return bytes(b)

    def burst_write(self, addr: int, vals: ByteT) -> None:
        for i, v in enumerate(vals):
            self.new_bin[self.offset + addr + i] = v
