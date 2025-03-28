from dataclasses import dataclass, field
from typing import Self, overload


class Uint32(int):
    def __new__(cls, value: int | str, /):
        if isinstance(value, str):
            match value[:2]:
                case "0b" | "0B":
                    value = value[2:]
                    base = 2
                case "0o" | "0O":
                    value = value[2:]
                    base = 8
                case "0x" | "0X":
                    value = value[2:]
                    base = 16
                case _:
                    base = 16
            value = int(value, base)
        assert value >= 0, "Hex must be positive"
        self = super().__new__(cls, value)
        return self

    def __str__(self) -> str:
        if self < 2**32:
            return f"{self:#010x}"
        return f"{self:#x}"

    def __contains__(self, mask: int, /) -> bool:
        return mask & self == mask

    @overload
    def __getitem__(self, sl: int, /) -> bool: ...
    @overload
    def __getitem__(self, sl: slice, /) -> int: ...
    def __getitem__(self, sl: int | slice) -> int | bool:
        if isinstance(sl, int):
            if sl < 0:
                sl += 32
            assert 0 <= sl < 32
            return bool((self >> sl) & 0x1)

        step = sl.step or 1

        assert step != 0
        start, stop = (0, 32) if step > 0 else (31, -1)

        if start < 0:
            start += 32
        if stop < 0:
            stop += 32

        result = 0
        bits = list(range(start, stop, step))

        if step < 0:
            bits = sorted(bits, reverse=True)

        for i, b in enumerate(bits):
            result |= ((self >> b) & 0x1) << i

        return result


class Mask(Uint32):
    @classmethod
    def bit(cls, b: int) -> Self:
        return cls(1 << b)

    @classmethod
    def field(cls, s: int, l: int) -> Self:
        return cls(((1 << l) - 1) << s)

    @classmethod
    def range(cls, s: int, e: int) -> Self:
        assert s < e
        l = e - s + 1
        return cls(((1 << l) - 1) << s)

    def get(self, val: int) -> int:
        return val & self

    def set(self, val: int) -> int:
        return val | self

    def clear(self, val: int) -> int:
        return val & ~self

    def toggle(self, val: int) -> int:
        return val ^ self

    def is_set(self, val: int) -> bool:
        return (val & self) == self

    def is_clear(self, val: int) -> bool:
        return (val & self) == 0


@dataclass
class BitMask(Mask):
    s: int = field(init=False)
    l: int = field(init=False)

    def __new__(cls, s: int | tuple[int, int], l: int = 1, /, *, base: int = 0):
        if isinstance(s, tuple):
            s, e = s
            assert s < e
            l = e - s + 1
        s += base

        assert s >= 0
        assert l > 0

        mask = ((1 << l) - 1) << s
        self = super().__new__(cls, mask)
        self.s = s
        self.l = l
        return self

    @property
    def s_l(self) -> tuple[int, int]:
        return self.s, self.l

    def get_field(self, val: int) -> int:
        return (val >> self.s) & ((1 << self.l) - 1)

    def set_field(self, val: int, v: int) -> int:
        return (val & ~self) | ((v & ((1 << self.l) - 1)) << self.s)


mask = Uint32(0xCAFEBABE)

print(mask[31])  # 访问最高位 → True
print(mask[8:16])  # 获取8-15位 → 0xBE
print(mask[24:16:-1])  # 逆序获取24-17位 → 0xCA
print(mask[::-4])  # 每4位取反序 → 计算结果...
