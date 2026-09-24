import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Callable


def delay(seconds: float = 1):
    logger.warning(f"Delay {seconds}s")
    return time.sleep(seconds)


def wait_for(
    func: Callable[[], bool],
    /,
    *,
    timeout: float | None = 10,
    retry: int | None = None,
    delay: float = 0.1,
    fail: Callable[[], bool] | None = None,
) -> None:
    start_time = time.monotonic()
    attempt = 0

    while True:
        if func():
            return

        if fail and fail():
            raise RuntimeError("Wait aborted due to fail condition triggered")

        if timeout is not None and time.monotonic() - start_time >= timeout:
            raise TimeoutError(f"Wait timed out after {timeout} seconds")
        if retry is not None and attempt >= retry:
            raise TimeoutError(f"Wait timed out after {retry} retries")

        time.sleep(delay)
        attempt += 1


def wait_for_state[T](
    func: Callable[[], T],
    state: T | list[T],
    /,
    *,
    timeout: float | None = 10,
    retry: int | None = None,
    delay: float = 0.1,
    fail: T | list[T] | None = None,
) -> T:
    if not isinstance(state, list):
        state = [state]
    if fail is not None and not isinstance(fail, list):
        fail = [fail]

    start_time = time.monotonic()
    attempt = 0

    while True:
        val = func()

        if val in state:
            return val

        if fail is not None and val in fail:
            raise RuntimeError(f"{val=}")

        if timeout is not None and time.monotonic() - start_time >= timeout:
            raise TimeoutError(f"Wait timed out after {timeout} seconds")

        if retry is not None and attempt >= retry:
            raise TimeoutError(f"Wait timed out after {retry} retries")

        time.sleep(delay)
        attempt += 1


def wait_for_click(message: str = "Click to continue") -> bool:
    title = "Waiting"
    root = tk.Tk()
    root.withdraw()
    root.attributes(topmost=True)  # pyright: ignore[reportUnknownMemberType]
    result = messagebox.askokcancel(title, message)
    root.destroy()
    return result


def wait_for_input_int(message: str = "Please enter integer:", *, default: int | None = None) -> int | None:
    title = "Waiting"
    root = tk.Tk()
    root.withdraw()
    rs = simpledialog.askinteger(title, message, initialvalue=default)
    root.destroy()
    return rs


def wait_for_input_float(message: str = "Please enter float:", *, default: float | None = None) -> float | None:
    title = "Waiting"
    root = tk.Tk()
    root.withdraw()
    rs = simpledialog.askfloat(title, message, initialvalue=default)
    root.destroy()
    return rs


def wait_for_input_str(message: str = "Please enter string:", *, default: str | None = None) -> str | None:
    title = "Waiting"
    root = tk.Tk()
    root.withdraw()
    rs = simpledialog.askstring(title, message, initialvalue=default)
    root.destroy()
    return rs
