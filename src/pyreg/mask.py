from typing import Sequence

from pyreg.bitfield import Bitfield, BitfieldT

type MaskT = Sequence[BitfieldT]


class Mask:
    @classmethod
    def combine(cls, bfs: MaskT) -> int:
        mask = 0
        for i in bfs:
            bf = Bitfield(i) if not isinstance(i, Bitfield) else i
            mask |= bf.mask
        return mask

    @classmethod
    def is_set(cls, val: int, bfs: MaskT) -> bool:
        mask = cls.combine(bfs)
        return (val & mask) == mask

    @classmethod
    def is_clear(cls, val: int, bfs: MaskT) -> bool:
        mask = cls.combine(bfs)
        return (val & mask) == 0

    @classmethod
    def set(cls, val: int, bfs: MaskT) -> int:
        mask = cls.combine(bfs)
        return val | mask

    @classmethod
    def clear(cls, val: int, bfs: MaskT) -> int:
        mask = cls.combine(bfs)
        return val & ~mask
