import numpy as np
from typing import Callable, Dict, cast, Any
import os.path
from pprint import pprint


def np_load_or_create(filename: str, f: Callable[[], np.ndarray]) -> np.ndarray:
    if not os.path.exists(filename):
        np.save(filename, f())
    return cast(np.ndarray,  np.load(filename))


def np_load_or_createz(filename: str, f: Callable[[], Dict[Any, np.ndarray]]) -> Dict[Any, np.ndarray]:
    dispatch = {
        'str': lambda x: x,
        'float': lambda x: float(x),
        'int': lambda x: int(x),
        'bool': lambda x: True if x.lower() in ("yes", "true") else False
    }

    def pack_key(k: Any) -> str:
        typ = type(k).__name__
        if typ not in dispatch:
            raise RuntimeError(f'Unhandled type {type(k)}')
        return f"{typ}__{k}"

    def unpack_key(k: str) -> Any:
        if k.find("__") < 0:
            return k
        typ, key = k.split("__", 1)
        if typ in dispatch:
            return dispatch[typ](key)
        else:
            raise RuntimeError(f'Unhandled type: {typ}')

    if not os.path.exists(filename):
        kwargs = {pack_key(k): v for k, v in f().items()}
        np.savez(filename, **kwargs)

    r = np.load(filename)
    return cast(Dict[str, np.ndarray], {unpack_key(k): v for k, v in r.items()})
