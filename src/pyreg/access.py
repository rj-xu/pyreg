from enum import Flag, auto


class Access(Flag):
    R = auto()
    W = auto()

    @property
    def is_readable(self) -> bool:
        return Access.R in self

    @property
    def is_writable(self) -> bool:
        return Access.W in self


class Once(Flag):
    R = auto()
    W = auto()

    @property
    def is_read_once(self) -> bool:
        return Once.R in self

    @property
    def is_write_once(self) -> bool:
        return Once.W in self
