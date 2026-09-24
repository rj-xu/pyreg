from enum import IntEnum

BITS_PER_BYTE = 8


class Size(IntEnum):
    BYTE = 1

    SZ_4K = 1024 * 4
    SZ_3K = 1024 * 3
    SZ_2K = 1024 * 2
    SZ_1K = 1024 * 1

    HWORD = 1
    WORD = 2
    DWORD = 4
    QWORD = 8

    PAGE = 256
    BLK_32K = 32 * 1024
    BLK_64K = 64 * 1024
    SECTOR = 4096
