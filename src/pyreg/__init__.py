# noqa: N999
from . import utils
from .bit import Bit, Bits, Byte, Bytes
from .bit_field import BitBool, BitField, BitFieldBe, EnumField, Reserved, Trigger
from .device import IptDevice
from .endian import Endian
from .log import logger
from .mask import BitRange, Mask
from .reg import Flags, Reg, RegRo, RegRw, RegWo

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
    "BitFieldBe",
    "BitRange",
    "Bits",
    "Byte",
    "Bytes",
    "Endian",
    "EnumField",
    "Flags",
    "IptDevice",
    "Mask",
    "Reg",
    "RegRo",
    "RegRw",
    "RegWo",
    "Reserved",
    "Trigger",
    "logger",
    "utils",
]


def hello() -> str:
    return "Hello from pyreg!"
