from typing import NamedTuple, Self, overload


class Mask(NamedTuple):
    mask: int
    s: int = 0

    def get(self, val: int) -> int:
        return val & self.mask

    def set(self, val: int, by: bool = True) -> int:  # noqa: FBT001, FBT002
        return (val | self.mask) if by else self.clear(val)

    def clear(self, val: int) -> int:
        return val & ~self.mask

    def toggle(self, val: int) -> int:
        return val ^ self.mask

    def is_set(self, val: int) -> bool:
        return (val & self.mask) == self.mask

    def is_clear(self, val: int) -> bool:
        return (val & self.mask) == 0

    def __or__(self, val: Self):
        return Mask(self.mask | val.mask)

    def __and__(self, val: Self):
        return Mask(self.mask & val.mask)

    def __xor__(self, val: Self):
        return Mask(self.mask ^ val.mask)

    def __invert__(self):
        return Mask(~self.mask)

    def __lshift__(self, val: int):
        return Mask(self.mask << val)

    def __rshift__(self, val: int):
        return Mask(self.mask >> val)

    def extract(self, val: int) -> int:
        return (val & self.mask) >> self.s

    def insert(self, val: int, field: int) -> int:
        return (val & ~self.mask) | ((field << self.s) & self.mask)

    @classmethod
    def new(cls, last_s: int | tuple[int, int] | None, l: int | None, *, byte: int):
        if isinstance(last_s, tuple):
            last, s = last_s
            assert last > s
            l = last - s + 1
        elif last_s is None:
            s = 0
        else:
            s = last_s

        if l is None:
            l = 1 if last_s is not None else 8

        assert s >= 0
        assert l >= 0

        s += byte * 8
        mask = ((1 << l) - 1) << s

        return cls(mask=mask, s=s)


@overload
def Bit(s: int | tuple[int, int], *, byte: int = 0) -> Mask: ...  # pylint: disable=invalid-name
@overload
def Bit(s: int, l: int, *, byte: int = 0) -> Mask: ...  # pylint: disable=invalid-name
@overload
def Bit(*, l: int | None = None, byte: int = 0) -> Mask: ...  # pylint: disable=invalid-name
def Bit(s: int | tuple[int, int] | None = None, l: int | None = None, *, byte: int = 0) -> Mask:  # noqa: N802 # pylint: disable=invalid-name
    return Mask.new(last_s=s, l=l, byte=byte)
