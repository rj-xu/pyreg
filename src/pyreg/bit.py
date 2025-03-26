from enum import IntEnum, IntFlag, auto


class Bit(IntFlag):
    _0 = auto()
    _1 = auto()
    _2 = auto()
    _3 = auto()
    _4 = auto()
    _5 = auto()
    _6 = auto()
    _7 = auto()
    _8 = auto()
    _9 = auto()
    _10 = auto()
    _11 = auto()
    _12 = auto()
    _13 = auto()
    _14 = auto()
    _15 = auto()
    _16 = auto()
    _17 = auto()
    _18 = auto()
    _19 = auto()
    _20 = auto()
    _21 = auto()
    _22 = auto()
    _23 = auto()
    _24 = auto()
    _25 = auto()
    _26 = auto()
    _27 = auto()
    _28 = auto()
    _29 = auto()
    _30 = auto()
    _31 = auto()


class Byte(IntFlag):
    _0 = 0xFF
    _1 = 0xFF << 8
    _2 = 0xFF << 16
    _3 = 0xFF << 24
    _4 = 0xFF << 32
    _5 = 0xFF << 40
    _6 = 0xFF << 48
    _7 = 0xFF << 56
    ALL_32 = 0xFFFF_FFFF
    ALL_64 = 0xFFFF_FFFF_FFFF_FFFF


class Bits(IntEnum):
    PER_BYTE = 8

    BYTE_0 = 0
    BYTE_1 = 8
    BYTE_2 = 16
    BYTE_3 = 24
    BYTE_4 = 32
    BYTE_5 = 40
    BYTE_6 = 48
    BYTE_7 = 56


class Bytes(IntEnum):
    HWORD = 2
    WORD = 4
    DWORD = 8
    QWORD = 16

    _1K = 1024
    _2K = 2048
    _4K = 4096
    _8K = 8192
