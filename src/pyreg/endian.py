from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.types import Bytes, Width


class Endian(StrEnum):
    BIG = "big"
    LITTLE = "little"

    @property
    def is_be(self):
        return self == Endian.BIG

    def bytes_to_int(self, b: Bytes) -> int:
        return int.from_bytes(b, byteorder=self.value, signed=False)

    def int_to_bytes(self, i: int, length: int = 4) -> bytes:
        return i.to_bytes(length=length, byteorder=self.value, signed=False)

    @staticmethod
    def int_to_int(i: int, *, width: Width = 32):
        length = width // 8
        return int.from_bytes(
            int.to_bytes(
                i,
                length=length,
                byteorder="little",
                signed=False,
            ),
            byteorder="big",
            signed=False,
        )

    @staticmethod
    def bytes_to_bytes(b: bytes):
        return b[::-1]

    @staticmethod
    def align_bytes(i: int, *, width: Width = 32):
        base = (i.bit_length() + 7) // 8
        remainder = base % width
        return base if remainder == 0 else base + (width - remainder)

    @staticmethod
    def hex_to_bytes(hex_str: str) -> bytes:
        return bytes.fromhex(hex_str)

    def hex_to_int(self, hex_str: str) -> int:
        return self.bytes_to_int(bytes.fromhex(hex_str))

    def bytes_to_list(self, b: bytes, *, width: Width) -> list[int]:
        size = len(b)
        length = width // 8

        assert size % length == 0

        return [self.bytes_to_int(b[i : i + length]) for i in range(0, size, length)]

    def list_to_bytes(self, l: list[int], *, width: Width) -> bytes:
        length = width // 8
        return b"".join(self.int_to_bytes(num, length=length) for num in l)
