from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Self, overload

from loguru import logger

from .endian import Endian
from .reg import RegRwNum

if TYPE_CHECKING:
    from utils.types import Bytes


@dataclass(frozen=True)
class Block:
    offset: int
    size: int
    is_be: bool = False

    @property
    def name(self) -> str:
        n = f"{self._name_}" if isinstance(self, Enum) else "Block"
        return n + f"({self.offset:#06x}, {self.size})"

    @property
    def endian(self) -> Endian:
        return Endian.BIG if self.is_be else Endian.LITTLE

    @property
    def reg(self):
        assert self.size in (1, 2, 4)
        return RegRwNum(self.offset, size=self.size, is_be=self.endian.is_be)

    @property
    def s_e(self):
        return self.offset, self.end

    @property
    def end(self):
        return self.offset + self.size

    @property
    def slice(self):
        return slice(*self.s_e)

    def __add__(self, other: Self):
        assert self.offset + self.size == other.offset
        return Block(self.offset, self.size + other.size, self.is_be)

    def __sub__(self, other: Self):
        if self.offset == other.offset:
            assert self.size > other.size
            return Block(self.offset + other.size, self.size - other.size, self.is_be)
        if self.offset + self.size == other.offset + other.size:
            assert self.offset < other.offset
            return Block(self.offset, self.size - other.size, self.is_be)
        raise ValueError

    def extend_to_contain(self, other: Self):
        assert self.offset + self.size <= other.offset
        size = other.offset + other.size - self.offset
        return Block(self.offset, size, self.is_be)

    def extract_sub_by[T: "BlkTable"](self, table: type[T]) -> list[T]:
        rs: list[T] = []
        my_start = self.offset
        my_end = self.offset + self.size

        for blk in table:
            blk_start = blk.offset
            blk_end = blk.offset + blk.size

            if my_start <= blk_start and blk_end <= my_end:
                rs.append(blk)

        assert my_start == rs[0].offset
        assert my_end == rs[-1].end

        return rs


class BlkTable(Block, Enum): ...


class BlkData:
    data: bytearray

    def __init__(self, b: Bytes | Path | int = 0):
        if isinstance(b, Path):
            self.data = self.load(b).data
        elif isinstance(b, int):
            self.data = bytearray(b)
        else:
            self.data = bytearray(b)

    @overload
    def __getitem__(self, key: int) -> int: ...
    @overload
    def __getitem__(self, key: slice) -> Self: ...

    def __getitem__(self, key: slice | int) -> int | Self:
        match key:
            case int():
                b = self.data[key]
                return b
            case slice():
                b = self.data[key]
                return self.__class__(b)

    def read(self, blk: Block) -> int:
        assert blk.size in (1, 2, 4)
        val = blk.endian.bytes_to_int(self.read_bytes(blk))
        logger.info(f"Read {blk.name} = {val:#x}")
        return val

    def read_bytes(self, blk: Block) -> bytes:
        s, e = blk.s_e
        val = self.data[s:e]
        logger.debug(f"Read bytes {blk.name}[{s}:{e}] = {val.hex()}")
        return bytes(val)

    def write(self, blk: Block, val: int) -> None:
        logger.info(f"Write {blk.name} = {val:#x}")
        b = blk.endian.int_to_bytes(val, length=blk.size)
        self.write_bytes(blk, b)

    def write_bytes(self, blk: Block, val: Bytes) -> None:
        assert len(val) <= blk.size
        if len(val) < blk.size:
            logger.warning(f"Only write {len(val)}/{blk.size} bytes to {blk.name}")
        s, e = blk.s_e
        logger.debug(f"Write bytes {blk.name}[{s}:{e}] = {val.hex()}")
        self.data[s : s + len(val)] = val

    @classmethod
    def load(cls, file: Path, l: int | None = None) -> Self:
        rs: bytes
        match file.suffix:
            case ".bin":
                rs = file.read_bytes()
            case ".txt":
                temp = bytearray()
                with file.open(mode="r") as fp:
                    for line in fp:
                        hex_val = line.strip()
                        if hex_val:
                            int_val = int(hex_val, 16)
                            byte_val = int_val.to_bytes(4, byteorder="little")
                            temp += byte_val
                rs = bytes(temp)
            case _:
                raise ValueError
        if l is not None:
            rs = rs[:l]
        return cls(b=rs)

    def save(self, file: Path, _l: int | None = None):
        file.parent.mkdir(parents=True, exist_ok=True)
        match file.suffix:
            case ".bin":
                with file.open("wb") as fp:
                    fp.write(self.data)
            case ".txt" | ".mif":
                with file.open("w") as fp:
                    for i in range(0, len(self.data), 4):
                        dword = int.from_bytes(self.data[i : i + 4], byteorder="little")
                        fp.write(f"{dword:08X}\n")
            case _:
                raise ValueError
        return file

    def dump(self, table: type[BlkTable]):
        for blk in table:
            s, e = blk.s_e
            val = self.read_bytes(blk)
            logger.info(f"{blk.name}[{s}:{e - 1}] = {val.hex()}")

    def fill(self, blk: Block, val: int | Bytes):
        if isinstance(val, int):
            assert 0x00 <= val <= 0xFF
            fill_data = bytes([val]) * blk.size
        else:
            if len(val) == 0:
                raise ValueError

            if len(val) >= blk.size:
                fill_data = val[: blk.size]
            else:
                full_repeats, remainder = divmod(blk.size, len(val))
                fill_data = val * full_repeats
                if remainder:
                    fill_data += val[:remainder]
        self.write_bytes(blk, fill_data)
