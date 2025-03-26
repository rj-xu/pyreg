from enum import Flag, auto


class AccessMode(Flag):
    R = auto()
    W = auto()
    # R_ONCE = auto()
    # W_ONCE = auto()

    @property
    def is_readable(self) -> bool:
        return AccessMode.R in self

    @property
    def is_writable(self) -> bool:
        return AccessMode.W in self
