from typing import Callable


def singleton[T, **P](cls: type[T]) -> Callable[..., T]:
    instances: dict[type[T], T] = {}

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
