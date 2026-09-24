from collections.abc import Callable, Iterable, Sequence
from enum import IntEnum
from typing import Any, Final, Literal, TypeIs, cast, override

from rich.console import Console
from rich.table import Table

UNSET: Final = cast("Any", None)

type AnyFunc = Callable[..., Any]

type BasicType = int | float | bool | str
type BasicList = list[int] | list[float] | list[bool] | list[str]
type BasicTuple = tuple[int, ...] | tuple[float, ...] | tuple[bool, ...] | tuple[str, ...]
type BasicIterable = Iterable[int] | Iterable[float] | Iterable[bool] | Iterable[str]
type BasicSequence = Sequence[int] | Sequence[float] | Sequence[bool] | Sequence[str]

type Bytes = bytes | bytearray
type Width = Literal[8, 16, 32]
WIDTH_RANGE = (8, 16, 32)
type Bit = Literal[0, 1, 2, 3, 4, 5, 6, 7]
BIT_RANGE = (0, 1, 2, 3, 4, 5, 6, 7)


def is_width(width: int) -> TypeIs[Width]:
    return width in (8, 16, 32)


def check_val_in_width(*, val: int, width: Width) -> bool:
    match width:
        case 8:
            return 0 <= val < 0xFF
        case 16:
            return 0 <= val < 0xFFFF
        case 32:
            return 0 <= val < 0xFFFF_FFFF


class BitNum(IntEnum):
    B0 = 0
    B1 = 1
    B2 = 2
    B3 = 3
    B4 = 4
    B5 = 5
    B6 = 6
    B7 = 7

    @property
    def as_mask(self):
        return 1 << self.value


class Width2(IntEnum):
    W8 = 8
    W16 = 16
    W32 = 32

    @property
    def as_bytes(self):
        return self.value // 8

    def check_val(self, val: int) -> bool:
        return 0 <= val < (1 << self.value)

    @classmethod
    def from_int(cls, val: int) -> Width2:
        if val < 0:
            raise ValueError
        if val < 0xFF:
            return Width2.W8
        if val < 0xFFFF:
            return Width2.W16
        if val < 0xFFFF_FFFF:
            return Width2.W32
        raise ValueError


class AnyObject:
    def __getattr__(self, name: str):
        return self

    @override
    def __setattr__(self, name: str, value: Any): ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


def merge_dicts(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    merged = dict[str, Any](b)
    for key, a_val in a.items():
        b_val = b.get(key)
        if isinstance(a_val, dict) and isinstance(b_val, dict):
            sub = merge_dicts(
                cast("dict[str, Any]", a_val),
                cast("dict[str, Any]", b_val),
            )
            merged[key] = sub
        else:
            merged[key] = a_val
    return merged


def diff_dicts(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    diff = dict[str, Any]()
    for key, a_val in a.items():
        b_val = b.get(key)
        if isinstance(a_val, dict) and isinstance(b_val, dict):
            sub = diff_dicts(
                cast("dict[str, Any]", a_val),
                cast("dict[str, Any]", b_val),
            )
            if sub:
                diff[key] = sub
        elif a_val != b_val:
            diff[key] = a_val
    return diff


def serialize_bool_as_int(d: BasicType | dict[str, Any] | list[Any]) -> Any:
    if isinstance(d, dict):
        return {k: serialize_bool_as_int(v) for k, v in d.items()}
    if isinstance(d, list):
        return [serialize_bool_as_int(i) for i in d]
    if isinstance(d, bool):
        return int(d)
    return d


def remove_empty_values(d: BasicType | dict[str, Any] | list[Any]) -> Any:
    if isinstance(d, dict):
        temp = {k: remove_empty_values(v) for k, v in d.items() if v != {}}
        return {k: v for k, v in temp.items() if v != {}}
    if isinstance(d, list):
        return [remove_empty_values(i) for i in d]
    return d


def check_all_fields_is_none(v: Any) -> bool:
    if v is None:
        return True
    if not hasattr(v, "__dict__"):
        return False
    return all(check_all_fields_is_none(field) for field in v.__dict__.values())


def _int_to_hex(*, width: Width, tag: bool, lower: bool, sep: bool):
    hex_width = width // 4
    if hex_width > 4 and sep:
        hex_width += 1
    return f"{'0x' if tag else ''}{{:0{hex_width}{'_' if sep else ''}{'x' if lower else 'X'}}}"


_HEX_FORMATS = {
    (w, tg, lw, sep): _int_to_hex(width=w, tag=tg, lower=lw, sep=sep)
    for w in (8, 16, 32)
    for tg in (True, False)
    for lw in (True, False)
    for sep in (True, False)
}


def int_to_hex(val: int, *, width: Width = 32, tag: bool = True, lower: bool = False, sep: bool = False):
    fmt = _HEX_FORMATS[(width, tag, lower, sep)]
    return fmt.format(val)


def bytes_to_str(vals: Bytes) -> str:
    s = " " * 10 + " ".join(f"{i:02X}" for i in range(16)) + "  Decoded Text\n"

    size = len(vals)
    offset = 0
    while size:
        r_size = min(size, 16)
        s += (
            f"{offset:08X}  "
            + " ".join(f"{vals[offset + i]:02X}" for i in range(r_size))
            + "   " * (16 - r_size)
            + " " * 2
            + " ".join(f"{chr(vals[offset + i]) if 32 <= vals[offset + i] <= 126 else '*'}" for i in range(r_size))
            + "   " * (16 - r_size)
            + "\n"
        )
        offset += r_size
        size -= r_size

    return "\n" + s.removesuffix("\n")


def bytes_to_rich_str(vals: bytes) -> str:
    console = Console()

    table = Table(
        show_header=True,
        header_style="bold magenta",
        border_style="bright_black",
        title_style="bold blue",
        caption_style="italic green",
    )

    table.add_column("Offset", style="bold yellow", justify="right")

    for i in range(16):
        table.add_column(f"{i:02X}", style="cyan", justify="center")

    table.add_column("Decoded Text", style="green")

    size = len(vals)
    offset = 0
    while size:
        r_size = min(size, 16)
        row = [f"{offset:08X}"]

        for i in range(r_size):
            byte_val = vals[offset + i]
            hex_str = f"{byte_val:02X}"

            if 32 <= byte_val <= 126:
                style = "white"
            elif byte_val == 0x00:
                style = "dim"
            elif byte_val in [0xFF, 0xFE, 0xFD]:
                style = "red"
            else:
                style = "blue"

            row.append(f"[{style}]{hex_str}[/{style}]")

        row.extend([""] * (16 - r_size))

        text_chars: list[str] = []
        for i in range(r_size):
            byte_val = vals[offset + i]
            char = chr(byte_val) if 32 <= byte_val <= 126 else "*"

            if 32 <= byte_val <= 126:
                text_chars.append(f"[white]{char}[/white]")
            elif byte_val == 0x00:
                text_chars.append(f"[dim]{char}[/dim]")
            else:
                text_chars.append(f"[bright_black]{char}[/bright_black]")

        row.append("".join(text_chars))

        table.add_row(*row)

        offset += r_size
        size -= r_size

    with console.capture() as capture:
        console.print(table)

    return capture.get()


if __name__ == "__main__":
    print(int_to_hex(0xFF, width=8))
    print(int_to_hex(0xFF, width=16, tag=False))
    print(int_to_hex(0xFF, width=32, lower=False))

    print(bytes_to_str(b"\xff" * 1020))
    print(bytes_to_rich_str(b"\xff" * 1020))
