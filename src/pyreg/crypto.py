from dataclasses import dataclass

from pyreg.bit import Bit
from pyreg.bitfield import Bitfield
from pyreg.device import Enum
from pyreg.reg import Reg


@dataclass
class GlbConfig(Reg):
    TRNG_TRIG_PARAM_TRIG    = Bitfield( 0                      )
    FULL_FRAME_MODE_O       = Bitfield( 1                      )
    SSK_USAGE               = Bitfield( 2                      )
    SECURE_KEY_USAGE_TRIG   = Bitfield( 3                      )
    GEOM_UPDATE             = Bitfield( 4                      )
    EVENT_TRIG              = Bitfield( 5                      )
    EVENT_ID                = Bitfield([6, 7]                  )
    RESERVED                = Bitfield( 0, base=Bit.BYTE_1     )
    EMBLINE_DATA_EN         = Bitfield( 1, base=Bit.BYTE_1     )
    ECC256_ECDH_PUBK_FORMAT = Bitfield([2, 3], base=Bit.BYTE_1 )
    RESERVED_1              = Bitfield((4, 20), base=Bit.BYTE_1)


class CryptoReg(Enum):
    GLB_CONFIG = GlbConfig(0x1A00)


if __name__ == "__main__":
    a = CryptoReg.GLB_CONFIG.value.TRNG_TRIG_PARAM_TRIG
    # CryptoReg.GLB_CONFIG.value.TRNG_TRIG_PARAM_TRIG = 1.2
    CryptoReg.GLB_CONFIG.value.TRNG_TRIG_PARAM_TRIG = 1

    b = CryptoReg.GLB_CONFIG.value.FULL_FRAME_MODE_O
    c = GlbConfig.EVENT_ID

    pass
