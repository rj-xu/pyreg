import pickle
from pathlib import Path
from typing import Any

_PICKLE = Path(__file__).parent


def read_pickle(val_name: str) -> Any:
    path = _PICKLE.joinpath(f"{val_name}.pickle")
    with path.open("rb") as f:
        return pickle.load(f)  # noqa: S301


def save_pickle(filename: str, val: Any) -> None:
    path = _PICKLE.joinpath(f"{filename}.pickle")
    if not path.exists():
        with path.open("wb") as f:
            pickle.dump(val, f)
