from enum import StrEnum

from pyreg.bit import ByteT


class Endian(StrEnum):
    BIG = "big"
    LITTLE = "little"

    @property
    def is_big(self):
        return self.value == Endian.BIG

    def bytes_to_int(self, b: ByteT) -> int:
        return int.from_bytes(bytes(b), byteorder=self.value, signed=False)

    def bytes_to_list(self, b: ByteT, width: int = 4) -> list[int]:
        return [self.bytes_to_int(bytes(b[i : i + width])) for i in range(0, len(b), width)]

    def int_to_int(self, i: int) -> int:
        return self.bytes_to_int(bytes(i))

    def int_to_bytes(self, i: int, width: int = 4) -> bytes:
        return i.to_bytes(width, byteorder=self.value, signed=False)

    def list_to_bytes(self, l: list[int], width: int = 4) -> bytes:
        return b"".join([self.int_to_bytes(num, width) for num in l])
