from enum import IntEnum
from typing import Sequence

type ByteT = Sequence[int] | bytes | bytearray


class Bytes(IntEnum):
    BYTES_2K = 2048
    BYTES_4K = 4096


class Bit(IntEnum):
    BIT_0 = 0
    BIT_1 = 1
    BIT_2 = 2
    BIT_3 = 3
    BIT_4 = 4
    BIT_5 = 5
    BIT_6 = 6
    BIT_7 = 7

    PER_BYTE = 8

    BYTE_0 = 0
    BYTE_1 = 8
    BYTE_2 = 16
    BYTE_3 = 32
