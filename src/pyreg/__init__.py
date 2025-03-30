# noqa: N999
from . import utils
from .bit import Bit, Bits, Byte, Bytes
from .device import IptDevice
from .endian import Endian
from .field import BitBool, BitEnum, BitField, BitRsvd, BitTrigger
from .log import logger
from .mask import Mask
from .reg import Reg, RegFlags, RegRo, RegRsvd, RegRw, RegWo

__version__ = "1.0.0"
__description__ = "A Python package for register operations."
__author__ = "RJ Xu"
__email__ = "rj.xu@ovt.com"

VERSION = __version__
AUTHOR = __author__

__all__ = [
    "AUTHOR",
    "VERSION",
    "Bit",
    "BitBool",
    "BitField",
    "Bits",
    "Byte",
    "Bytes",
    "Endian",
    "BitEnum",
    "IptDevice",
    "Mask",
    "Reg",
    "RegRo",
    "RegRw",
    "RegWo",
    "BitRsvd",
    "BitTrigger",
    "RegFlags",
    "RegRsvd",
    "logger",
    "utils",
]


def hello() -> str:
    return "Hello from pyreg!"
