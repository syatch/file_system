from pathlib import Path
from threading import Lock
from weakref import WeakValueDictionary

_path_locks: WeakValueDictionary[str, Lock] = WeakValueDictionary()
_lock_create_guard = Lock()

def get_path_lock(path):
    key = str(Path(path).resolve())
    with _lock_create_guard:
        if key not in _path_locks:
            store_lock = Lock()
            _path_locks[key] = store_lock
        return _path_locks[key]
