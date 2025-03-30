from dataclasses import InitVar, dataclass, field
from typing import Self


@dataclass
class Mask:
    mask: int

    @classmethod
    def field(cls, s: int, l: int = 1) -> Self:
        return cls(((1 << l) - 1) << s)

    @classmethod
    def range(cls, s: int, e: int) -> Self:
        assert s < e
        l = e - s + 1
        return cls(((1 << l) - 1) << s)

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
        return (val & self.mask) == 0


type BitT = int | tuple[int, int] | list[int]


@dataclass
class BitMask(Mask):
    mask: int = field(init=False)
    s: int = field(init=False)
    l: int = field(init=False)

    bit: InitVar[BitT]
    base: InitVar[int] = 0

    def __post_init__(self, bit: BitT, base: int) -> None:
        match bit:
            case int():
                s = bit
                l = 1
            case tuple():
                s, l = bit
            case list():
                assert len(bit) == 2
                s, e = bit[0], bit[1]
                l = e - s + 1

        s += base

        assert s >= 0
        assert l > 0

        mask = ((1 << l) - 1) << s
        super().__init__(mask)
        self.s = s
        self.l = l

    @property
    def sl(self) -> tuple[int, int]:
        return self.s, self.l

    def get_field(self, val: int) -> int:
        return (val >> self.s) & ((1 << self.l) - 1)

    def set_field(self, val: int, v: int) -> int:
        return (val & ~self.mask) | ((v & ((1 << self.l) - 1)) << self.s)
