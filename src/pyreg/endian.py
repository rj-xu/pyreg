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

    def bytes_to_list(self, b: ByteT, width: DataWidthT = 4) -> list[int]:
        if len(b) % width != 0:
            raise ValueError(f"Invalid bytes length: {len(b)}")
        return [self.bytes_to_int(bytes(b[i : i + width])) for i in range(0, len(b), width)]

    def bytes_to_bytes(self, b: ByteT) -> bytes:
        return bytes(b[::-1])

    def int_to_int(self, i: int) -> int:
        return self.bytes_to_int(self.int_to_bytes(i)[::-1])

    def int_to_bytes(self, i: int, width: DataWidthT = 4) -> bytes:
        return i.to_bytes(width, byteorder=self.value, signed=False)

    def list_to_bytes(self, l: list[int], width: DataWidthT = 4) -> bytes:
        return b"".join([self.int_to_bytes(num, width) for num in l])
