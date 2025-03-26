from dataclasses import KW_ONLY, InitVar, dataclass, field


@dataclass
class Mask:
    mask: int

    # @classmethod
    # def bit(cls, b: int) -> Self:
    #     return cls(1 << b)

    # @classmethod
    # def field(cls, s: int, l: int) -> Self:
    #     return cls(((1 << l) - 1) << s)

    # @classmethod
    # def range(cls, r: list[int]) -> Self:
    #     assert len(r) == 2
    #     s, e = r
    #     assert s <= e
    #     l = e - s + 1
    #     return cls(((1 << l) - 1) << s)

    def get(self, val: int) -> int:
        return val & self.mask

    def set(self, val: int) -> int:
        return val | self.mask

    def clear(self, val: int) -> int:
        return val & ~self.mask

    def toggle(self, val: int) -> int:
        return val ^ self.mask

    def is_set(self, val: int) -> bool:
        return (val & self.mask) == self.mask

    def is_clear(self, val: int) -> bool:
        return (val & self.mask) == self.mask


type BitRangeT = int | tuple[int, int] | list[int]


@dataclass
class BitRange(Mask):
    bitfield: InitVar[BitRangeT]
    _: KW_ONLY
    base: InitVar[int] = 0

    s: int = field(init=False)
    l: int = field(init=False)
    mask: int = field(init=False)

    def __post_init__(self, bitfield: BitRangeT, base: int):
        match bitfield:
            case int():
                s = bitfield
                l = 1
            case tuple():
                if len(bitfield) != 2:
                    raise ValueError
                s = bitfield[0]
                l = bitfield[1]
            case list():
                if len(bitfield) != 2 or bitfield[0] > bitfield[1]:
                    raise ValueError

                s = bitfield[0]
                l = bitfield[1] - bitfield[0] + 1
        self.s = s + base
        self.l = l
        self.mask = ((1 << l) - 1) << s

    def get(self, val: int) -> int:
        return val & self.mask

    def set(self, val: int) -> int:
        return val | self.mask

    @property
    def tuple(self) -> tuple[int, int]:
        return (self.s, self.l)

    def get_field(self, val: int) -> int:
        return (val >> self.s) & ((1 << self.l) - 1)

    def set_field(self, val: int, v: int) -> int:
        return (val & ~self.mask) | ((v & ((1 << self.l) - 1)) << self.s)
