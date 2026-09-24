import getpass
import queue
import shutil
import subprocess
import sys
import threading
import time
import zoneinfo
from datetime import datetime
from typing import TYPE_CHECKING, Any, TextIO
from warnings import deprecated
from zoneinfo import ZoneInfo

import psutil
from loguru import logger
from tqdm import tqdm

if TYPE_CHECKING:
    from pathlib import Path

OS_IS_LINUX = sys.platform == "linux"
OS_IS_64BIT = sys.maxsize > 2**32
SHELL_IS_UTF8 = sys.stdout.encoding == "utf-8"
PY_IS_DEBUG = "debugpy" in sys.modules
USER = getpass.getuser()
BEIJING_TZ = zoneinfo.ZoneInfo("Asia/Shanghai")


def local_time(fmt: str = r"%Y-%m-%d %H:%M:%S") -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime(fmt)


def before_date(expected_date_str: str) -> bool:
    expected_date_obj = datetime.strptime(expected_date_str, "%Y%m%d").replace(tzinfo=BEIJING_TZ).date()
    current_date = datetime.now(BEIJING_TZ).date()
    return current_date < expected_date_obj


def run_cmd(
    cmd: list[Any],
    cwd: Path | None = None,
    timeout: int = 60,
    *,
    show: bool = True,
) -> tuple[int, list[str], list[str]]:
    logger.info(f"> {' '.join(map(str, cmd))}")
    result = subprocess.run(  # noqa: S603
        cmd,
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=timeout,
    )
    stdout = result.stdout.splitlines()
    stderr = result.stderr.splitlines()

    if show:
        for l in stdout:
            logger.debug(l)
        for l in stderr:
            logger.debug(l)

    return result.returncode, stdout, stderr


def open_pipe(cmd: list[Any], cwd: Path | None = None):
    process = subprocess.Popen(  # noqa: S603
        [str(i) for i in cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        # bufsize=1,
    )

    assert process.stdout is not None
    assert process.stderr is not None

    return process, process.stdout, process.stderr


def read_pipe(pipe: TextIO, output_queue: queue.Queue[str | None]):
    try:
        for line in iter(pipe.readline, ""):
            output_queue.put(line)
        pipe.close()
    except Exception as e:  # noqa: BLE001
        output_queue.put(f"Error reading pipe: {e}")
    finally:
        output_queue.put(None)


def run_cmd_with_bar(
    cmd: list[Any],
    cwd: Path | None = None,
    timeout: int = 60,
    *,
    show: bool = True,
    desc: str = "",
    color: str = "green",
) -> tuple[int, list[str], list[str]]:
    if PY_IS_DEBUG:
        return run_cmd(cmd, cwd, timeout, show=show)

    logger.info(f"> {' '.join(map(str, cmd))}")
    process, stdout, stderr = open_pipe(cmd, cwd)

    stdout_queue: queue.Queue[str | None] = queue.Queue()
    stderr_queue: queue.Queue[str | None] = queue.Queue()

    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    stdout_thread = threading.Thread(target=read_pipe, args=(stdout, stdout_queue))
    stderr_thread = threading.Thread(target=read_pipe, args=(stderr, stderr_queue))

    stdout_thread.daemon = True
    stderr_thread.daemon = True

    stdout_thread.start()
    stderr_thread.start()

    def record_pipe() -> None:
        try:
            while True:
                line = stdout_queue.get_nowait()
                if line is None:
                    break
                line = line.rstrip()
                stdout_lines.append(line)
                if show:
                    logger.info(line)
        except queue.Empty:
            pass

        try:
            while True:
                line = stderr_queue.get_nowait()
                if line is None:
                    break
                line = line.rstrip()
                stderr_lines.append(line)
                if show:
                    logger.error(line)
        except queue.Empty:
            pass

    start_time = time.time()
    with tqdm(
        total=timeout,
        desc=f"\033[1m[{local_time()}][  BAR   ]: {desc}",
        bar_format="{l_bar}{bar}| {n:.1f}/{total_fmt} s",
        colour=color,
    ) as pbar:
        while process.poll() is None:
            record_pipe()

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                try:
                    p = psutil.Process(process.pid)
                    status = p.status()
                    logger.warning(f"Process {process.pid} status: {status}")
                except psutil.NoSuchProcess:
                    logger.error(f"Process {process.pid} no longer exists")

                process.terminate()
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()

                pbar.close()
                logger.error("Subprocess TIMEOUT")

                record_pipe()
                return -1, stdout_lines, stderr_lines

            time.sleep(0.1)
            pbar.update(0.1)

        pbar.n = pbar.total
        pbar.refresh()

    record_pipe()

    return process.returncode, stdout_lines, stderr_lines


def delete(src: Path) -> bool:
    if src.exists():
        if src.is_dir():
            shutil.rmtree(src)
        else:
            src.unlink()
        return True
    return False


# def create(src: Path, *, replace: bool = False, is_dir: bool | None = None):
#     if src.exists():
#         if replace:
#             delete(src)
#         else:
#             raise FileExistsError(src)

#     src.parent.mkdir(parents=True, exist_ok=True)

#     if is_dir is None:
#         is_dir = not bool(src.suffix)

#     if is_dir:
#         src.mkdir()
#     else:
#         src.touch()


def create_target(src: Path, dst: Path | None, *, replace: bool = False, keep: bool = False, rename: str = ""):
    if not src.exists():
        raise FileNotFoundError(src)
    if dst is None:
        dst = src.parent
    else:
        assert not dst.is_file()
        dst.mkdir(parents=True, exist_ok=True)
    target = dst / (rename or src.name)
    if target.exists():
        if replace:
            if keep:
                raise ValueError("Can not replace and keep")
            delete(target)
        elif keep:
            filename, ext = target.stem, target.suffix

            i = 1
            while (dst / f"{filename}_{i}{ext}").exists():
                i += 1
            target = dst / f"{filename}_{i}{ext}"
        else:
            raise FileExistsError(dst)
    return target


def is_subdir(a: Path, b: Path) -> bool:
    try:
        a.resolve().relative_to(b.resolve())
    except ValueError:
        return False
    return True


@deprecated("use copy_into instead")
def copy(src: Path, dst: Path | None = None, *, replace: bool = False, keep: bool = False, rename: str = ""):
    target = create_target(src, dst, replace=replace, keep=keep, rename=rename)

    if src.is_file():
        shutil.copy2(src, target)
    elif is_subdir(target, src):
        for item in src.iterdir():
            if item.resolve() == target.resolve():
                continue
            if item.is_file():
                shutil.copy2(item, target)
            else:
                shutil.copytree(item, target)
    else:
        shutil.copytree(src, target)
    return target


@deprecated("use move_into instead")
def move(src: Path, dst: Path | None = None, *, replace: bool = False, keep: bool = False, rename: str = ""):
    target = create_target(src, dst, replace=replace, keep=keep, rename=rename)

    if is_subdir(target, src):
        for item in src.iterdir():
            if item.resolve() == target.resolve():
                continue
            shutil.move(src, target)
    else:
        shutil.move(src, target)
    return target


# def merge(
#     src: Path,
#     dst: Path,
#     *,
#     replace: bool = False,
#     keep: bool = False,
#     rename: str = "",
#     del_src: bool = False,
# ):
#     if not src.is_dir():
#         raise ValueError(f"{src} is not a dir")
#     if dst.is_file():
#         raise ValueError(f"{dst} is a file")

#     for item in src.iterdir():
#         move(item, dst, replace=replace, keep=keep)
#     if del_src and not is_subdir(dst, src):
#         delete(src)
#     if rename:
#         dst = dst.rename(dst.parent / rename)
#     return dst


# def rename(
#     src: Path,
#     name: str = "",
#     *,
#     replace: bool = False,
#     keep: bool = False,
#     use_copy: bool = False,
#     prefix: str = "",
#     suffix: str = "",
# ):
#     if not name:
#         name = src.stem
#     if prefix:
#         name = prefix + name
#     if suffix:
#         name += suffix

#     dst = create_target(src, None, replace=replace, keep=keep, rename=name)

#     if use_copy:
#         return copy(src, None, replace=replace, rename=name)
#     return src.rename(dst)
