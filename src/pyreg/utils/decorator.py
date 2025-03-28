import time
import warnings
from functools import wraps
from typing import Callable


def deprecated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"'{func.__name__}' is deprecated and will be removed in a future version",
            DeprecationWarning,
            stacklevel=2,
        )
        return func(*args, **kwargs)

    return wrapper


def singleton[T, **P](cls: type[T]):
    instances: dict[type[T], T] = {}

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


def timeout_check(timeout: float = 5.0, delay: float = 0.05):
    def decorator(func: Callable[[], bool]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            max_retries = int(timeout / delay)
            for _ in range(max_retries):
                if func(*args, **kwargs):
                    return True
                time.sleep(delay)
            return False

        return wrapper

    return decorator


def retry(max_attempts: int = 3, delay: float = 0.1):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
            return None

        return wrapper

    return decorator


def wait_for(stop_condition: Callable[[], bool], delay: float = 0.1):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            while not stop_condition():
                func(*args, **kwargs)
                time.sleep(delay)

        return wrapper

    return decorator
