import subprocess
import sys
import time


def is_sys_linux() -> bool:
    return sys.platform == "linux"


def is_sys_64bit() -> bool:
    return sys.maxsize > 2**32


def run_cmd(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True)  # noqa: S603
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e}"


def get_china_time() -> time.struct_time:
    return time.localtime(time.time() + 8 * 3600)


def show_time() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def time_stamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S", time.localtime())
