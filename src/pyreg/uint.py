from typing import ClassVar, Literal, Self, overload


class Uint(int):
    BIT_WIDTH: ClassVar[Literal[8, 16, 32, 64]] = 32

    def __new__(cls, value: int | str):
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

        match cls.BIT_WIDTH:
            case 8:
                limit = 0xFF
            case 16:
                limit = 0xFFFF
            case 32:
                limit = 0xFFFF_FFFF
            case 64:
                limit = 0xFFFF_FFFF_FFFF_FFFF
            case _:
                raise ValueError(f"Invalid BIT_WIDTH {cls.BIT_WIDTH}")

        if not 0 <= value <= limit:
            raise ValueError(f"Value {value} out of range for Uint{cls.BIT_WIDTH}")

        self = super().__new__(cls, value)
        return self

    def __str__(self) -> str:
        return self.hex()

    def __contains__(self, mask: int, /) -> bool:
        return mask & self == mask

    @overload
    def __getitem__(self, sl: int, /) -> bool: ...
    @overload
    def __getitem__(self, sl: slice, /) -> Self: ...
    def __getitem__(self, sl: int | slice) -> Self | bool:
        if isinstance(sl, int):
            if sl < 0:
                sl += self.BIT_WIDTH
            if not 0 <= sl < self.BIT_WIDTH:
                raise IndexError(f"Index {sl} out of range for Uint{self.BIT_WIDTH}")
            return bool((self >> sl) & 0x1)

        step = sl.step or 1
        if step == 0:
            raise ValueError("Slice step cannot be zero")

        if sl.start is not None:
            start = sl.start
            if start < 0:
                start += self.BIT_WIDTH
        else:
            start = 0 if step > 0 else (self.BIT_WIDTH - 1)

        if sl.stop is not None:
            stop = sl.stop
            if stop < 0:
                stop += self.BIT_WIDTH
        else:
            stop = self.BIT_WIDTH if step > 0 else -1

        result = 0
        bits = list(range(start, stop, step))

        if step < 0:
            bits = sorted(bits, reverse=True)

        for i, b in enumerate(bits):
            result |= ((self >> b) & 0x1) << i

        return self.__class__(result)

    def hex(self):
        if self < 0x10000:
            s = f"{self:04X}"
        elif self < 0x1_0000_0000:
            s = f"{self:08X}"
        else:
            raise ValueError(f"Value {self} out of range for Uint32")
        s = "_".join(s[i : i + 4] for i in range(0, len(s), 4))
        return "0x" + s

    def bin(self):
        if self < 0x100:
            s = f"{self:08b}"
        elif self < 0x1_0000:
            s = f"{self:016b}"
        elif self < 0x1_0000_0000:
            s = f"{self:032b}"
        else:
            raise ValueError(f"Value {self} out of range for Uint32")
        s = "_".join(s[i : i + 4] for i in range(0, len(s), 4))
        return "0b" + s


class U8(Uint):
    BIT_WIDTH = 8


class U16(Uint):
    BIT_WIDTH = 16


class U32(Uint):
    BIT_WIDTH = 32


if __name__ == "__main__":
    a = U32(0x12345678)
    print(a)
    print(a.bin())
    x = a[:16]
    print(x)
    x = a[:3]
    print(x)
    x = a[3:]
    print(x)
    x = a[::-1]
    print(x)
    print(x.bin())

    a = U16(0x1234)
