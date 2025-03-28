from enum import StrEnum
from typing import Literal, Sequence

type ByteT = Sequence[int] | bytes | bytearray
type DataWidthT = Literal[1, 2, 4, 8]


class Endian(StrEnum):
    BIG = "big"
    LITTLE = "little"

    @property
    def is_big(self):
        return self.value == Endian.BIG

    def bytes_to_int(self, b: ByteT) -> int:
        return int.from_bytes(bytes(b), byteorder=self.value, signed=False)

    def bytes_to_list(self, b: ByteT, width: int = 4) -> list[int]:
        if len(b) % width != 0:
            raise ValueError(f"Invalid bytes length: {len(b)}")
        return [self.bytes_to_int(bytes(b[i : i + width])) for i in range(0, len(b), width)]

    def bytes_to_bytes(self, b: ByteT) -> bytes:
        return bytes(b[::-1])

    def int_to_int(self, i: int, width: int = 4) -> int:
        return self.bytes_to_int(self.int_to_bytes(i, width)[::-1])

    def int_to_bytes(self, i: int, width: int = 4) -> bytes:
        return i.to_bytes(length=width, byteorder=self.value, signed=False)

    def list_to_bytes(self, l: list[int], width: int = 4) -> bytes:
        return b"".join([self.int_to_bytes(num, width) for num in l])

    @classmethod
    def bits_to_bytes(cls, bits: int, aligned_width: int = 4):
        assert bits >= 0
        assert aligned_width >= 0
        base = (bits + 7) // 8
        remainder = base % aligned_width
        return base if remainder == 0 else base + (aligned_width - remainder)
