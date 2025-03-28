import binascii

from .bit import Bits
from .endian import Endian


def is_legal_hex(s: str) -> bool: ...


def hex_to_bytes(s: str) -> bytes:
    return binascii.unhexlify(s)


def reverse_hex(s: str) -> str:
    msg = hex_to_bytes(s)
    return msg[::-1].hex()


def is_legal_bin(s: str):
    return bool(s) and set(s).issubset({"0", "1"})


def bin_to_bytes(s: str) -> bytes:
    if s == "0":
        return b"\x00"
    if len(s) <= Bits.PER_BYTE:
        return Endian.BIG.int_to_bytes(int(s, 2), width=1)
    return bin_to_bytes(s[:8]) + bin_to_bytes(s[8:])
