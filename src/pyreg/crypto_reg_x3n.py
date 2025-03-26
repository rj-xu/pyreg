import time
from dataclasses import dataclass
from enum import Enum, IntEnum, IntFlag, auto

from Libs.loglib import g_logger as logger

from .pyreg import BitBool, BitField, Endian, EnumField, Flags, RegRo, RegRw, Reserved, Trigger


class CryptoEvent(IntEnum):
    # fmt: off
    HOST_DECODE_CERT = 0 # sensor verify host's certificate: host decode cert
    SNR_DECODE_CERT  = 1 # sensor verify host's certificate: sensor decode cert
    SNR_GEN_ECDH     = 2 # generate sensor's ecdh key pair
    HOST_ECDH_RDY    = 3 # host's ecdh public key is ready
    # fmt: on

    def trigger_event(self):
        CryptoReg.GLB_CONFIG0.value.EVENT_ID = self
        CryptoReg.GLB_CONFIG0.value.EVENT_TRIG.trigger()

        # CryptoReg.GLB_CONFIG0.value.write(event, [6, 7], set_mask=Bit._5)
        # CryptoReg.GLB_CONFIG0.value.write(clear_mask=Bit._5)

        is_done = False
        for _ in range(100):
            state = CryptoReg.CRYPTO_STATE.value.flags
            if CryptoState.EVENT_DONE in state:
                if CryptoState.EVENT_STATUS not in state:
                    is_done = True
                    break
                logger.error(f"Trigger Event {self.name} Error")
                raise RuntimeError

            time.sleep(0.05)

        if is_done:
            logger.debug(f"Trigger Event {self.name} Done")
        else:
            logger.error(f"Trigger Event {self.name} TIMEOUT")
            raise TimeoutError


@dataclass
class GlbConfig0(RegRw):
    # fmt: off
    TRNG_TRIG_PARAM_TRIG    = BitField(0)
    FULL_FRAME_MODE_O       = BitField(1)
    SSK_USAGE               = BitBool(2)
    SECURE_KEY_USAGE_TRIG   = Trigger(3)
    GEOM_UPDATE             = Trigger(4)
    EVENT_TRIG              = Trigger(5)
    EVENT_ID                = EnumField[CryptoEvent]([6, 7])


class GlbConfig1(RegRw):
    RESERVED = Reserved(0)
    EMBLINE_DATA_EN = BitField(1)
    ECC256_ECDH_PUBK_FORMAT = BitField([2, 3])
    # fmt: on


class HostAddr(RegRw):
    HOST_CERTSIGNS_ADDR = BitField((0, 16))
    HOST_CERTPUBK_ADDR = BitField((16, 16))


class CryptoState(IntFlag):
    # fmt: off
    GMAC_STATE                = auto() # BYTE_0
    GMAC_READY_FLAG           = auto()
    NEW_KEY_FLAG              = auto()
    GEOM_UPDATE_DONE          = auto()
    GEOM_UPDATE_ENCOUNTER_SOF = auto()
    RESERVED                  = auto()
    FAULT_FSM_STATE           = auto()
    SRAM_INIT_DONE            = auto()
    EVENT_DONE                = auto() # BYTE_1
    EVENT_STATUS              = auto()
    HOST_ACCESS_PUB_RAM_READY = auto()
    OTP_LOAD_DONE_FLAG        = auto()
    OTP_READY                 = auto()
    SSK_CHANGE_REQ            = auto()
    FIFO_OVERFLOW             = auto()
    OV_OTP_FIELD_LOCK         = auto()
    SSK_GEN_ERR_FLAG          = auto() # BYTE_2
    HOST_ECDH_KEY_READY_FLAG  = auto()
    SENSOR_SIGN_ECDH_KEY_FLAG = auto()
    SENSOR_GEN_ECDH_KEY_FLAG  = auto()
    HOST_CERT_VERF_PASS_FLAG  = auto()
    HOST_OTP_LOCK             = auto()
    ONE_WAY_AUTHEN            = auto()
    TWO_WAY_AUTHEN            = auto()
    # fmt: on


class CryptoReg(Enum):
    # fmt: off
    GLB_CONFIG0           = GlbConfig0(0x1A00, size=1)
    GLB_CONFIG1           = GlbConfig1(0x1A01, size=1)
    HOST_ADDR             = HostAddr(0x1A04)
    TRNG_PARAM0           = RegRw(0x1A08)
    TRNG_PARAM1           = RegRw(0x1A0C)
    RSV                   = RegRw(0x1A10)
    PIXEL_PARAM           = RegRw(0x1A14)
    NONCE                 = RegRw(0x1A18, size=16)
    GEOM0_ROWS_PARAM      = RegRw(0x1A28)
    GEOM0_B2H             = RegRw(0x1A2C)
    RSV_1                 = RegRw(0x1A30, size=0x0C)
    FAULT_PARAM           = RegRw(0x1A3C)
    IV0                   = RegRw(0x1A40, size=12)
    DUMMY_REQ             = RegRw(0x1A4C)
    FAULT_LATCH           = RegRw(0x1A50)
    STICKY_FAULT          = RegRw(0x1A54)
    RSV_2                 = RegRw(0x1A58)
    GMAC0                 = RegRo(0x1A5C)
    GMAC1                 = RegRo(0x1A60)
    GMAC2                 = RegRo(0x1A64)
    GMAC3                 = RegRo(0x1A68)
    CRYPTO_STATE          = Flags[CryptoState](0x1A6C)
    OTP_OPEN_CRC          = RegRo(0x1A70)
    OTP_DEFINE_MAX_FN     = RegRo(0x1A74)
    UID                   = RegRo(0x1A78, size=6, endian=Endian.BIG)
    FRAME_COUNTER         = RegRo(0x1A80)
    SSK_FRAME_COUNTER     = RegRo(0x1A84)
    TRNG_HEALTH_TEST_FLAG = RegRo(0x1A88)
    HOST_CERT_PUBK        = RegRo(0x1A90)
    # fmt: on


class CryptoRam(Enum):
    # PRIVATE AREA
    # from DE
    # fmt: off
    HOST_CERT_PUBK_DEBUG      = RegRo(0x1A90, size=68)
    HOST_CERT_PUBK_SIGN_DEBUG = RegRo(0x1AD4, size=64)
    SNR_ECDH_PUBK             = RegRo(0x1B17, size=65)
    SNR_ECDH_PUBK_SIGN        = RegRo(0x1B58, size=64)
    SNR_CERT_LEN              = RegRo(0x1B98, size=4, endian=Endian.BIG)
    SNR_CERT                  = RegRo(0x1B9C, size=348)
    HOST_ECDH_PUBK            = RegRw(0x1CFB, size=65)
    HOST_ECDH_PUBK_SIGN       = RegRw(0x1D3C, size=64)
    HOST_CERT                 = RegRw(0x1D7C, size=852)
    # fmt: on


class CryptoOtp(Enum):
    # PRIVATE AREA
    # from FW
    # fmt: off
    SNR_OTP_LOCK   = RegRo(addr=0x5000, size=4)
    PPK            = RegRo(addr=0x5004, size=32)
    SNR_PRVK       = RegRo(addr=0x5024, size=32)
    CRC0           = RegRo(addr=0x5044, size=4)
    UID            = RegRo(addr=0x5048, size=6)
    SNR_CERT_LEN   = RegRo(addr=0x504E, size=4, endian=Endian.BIG)
    SNR_CERT       = RegRo(addr=0x5050, size=344)
    FRAME_NUMBER   = RegRo(addr=0x51A8, size=4)
    CRC1           = RegRo(addr=0x51AC, size=4)
    USER_PUBK_LOCK = RegRo(addr=0x51B0, size=4)
    HOST_AUTH_MODE = RegRo(addr=0x51B4, size=4)
    USER_GLB_PUBK  = RegRo(addr=0x51B8, size=68)
    CRC2           = RegRo(addr=0x51FC, size=4)
    # fmt: on
