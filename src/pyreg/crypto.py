from dataclasses import dataclass

from pyreg.bit import Bit
from pyreg.bitfield import Bitfield
from pyreg.device import Enum
from pyreg.reg import Reg


@dataclass
class GlbConfig(Reg):
    default = b"\x06\x03\x00\x00"

    TRNG_TRIG_PARAM_TRIG    = Bitfield( 0                      ) # Host need trig this bit after configuring all related TRNG parameter
    FULL_FRAME_MODE_O       = Bitfield( 1                      ) # A whole frame will be sent to GMAC engine
    SSK_USAGE               = Bitfield( 2                      ) # Ssk is used in 1st frame
    SECURE_KEY_USAGE_TRIG   = Bitfield( 3                      ) # Ppk case, when certificate verification pass and related register setting has configured Ssk case, Host already finished the shared ssk calculation sensor will place the key sync signal into embedded line after host and sensor both finished SSK calculation
    GEOM_UPDATE             = Bitfield( 4                      ) # Host need trig this bit when change geometry information on the fly
    EVENT_TRIG              = Bitfield( 5                      )
    EVENT_ID                = Bitfield([6,7]                   ) # 0:sensor verify host's certificate:host decode cert 1:sensor verify host's certificate:sensor decode cert 2:generate sensor's ecdh key pair 3:host's ecdh public key is ready
    RESERVED                = Bitfield( 0,      base=Bit.BYTE_1)
    EMBLINE_DATA_EN         = Bitfield( 1,      base=Bit.BYTE_1) # gmac embedded line(top/bottom/stat) involvement enable]
    ECC256_ECDH_PUBK_FORMAT = Bitfield([2, 3],  base=Bit.BYTE_1) # 0: decompressed 1: compressed 2: hybrid
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
