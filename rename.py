from pathlib import Path

from flowweave import FlowWeaveResult

from .file_system import FileSystem
from .lock_manager import get_path_lock

class RenameCfg():
    def __init__(self):
        self.files = []
        self.folders = []
        self.ext = []

class Rename(FileSystem):
    def operation_init(self):
        self.rename = RenameCfg()

    def operation(self):
        result = FlowWeaveResult.SUCCESS
        self.message(f"source : {self.source_dir}")

        for source_dir in self.source_dir:
            src_root = Path(source_dir).resolve()

            lock = get_path_lock(src_root)
            with lock:
                self.rename_files(src_root)
                self.rename_folders(src_root)
                self.rename_extensions(src_root)
        return result

    def rename_files(self, src_root):
        for rule in self.rename.files:
            for pattern, cfg in rule.items():
                for path in self._iter_targets(src_root, pattern):
                    if not path.is_file():
                        continue

                    from_str, to_str = self._get_from_to(cfg)
                    new_name = path.name.replace(from_str, to_str)
                    if new_name != path.name:
                        path.rename(path.with_name(new_name))

    def rename_folders(self, src_root):
        for rule in self.rename.folders:
            for pattern, cfg in rule.items():
                paths = sorted(
                    self._iter_targets(src_root, pattern),
                    key=lambda p: len(p.parts),
                    reverse=True
                )

                for path in paths:
                    if not path.is_dir():
                        continue

                    from_str, to_str = self._get_from_to(cfg)
                    new_name = path.name.replace(from_str, to_str)
                    if new_name != path.name:
                        path.rename(path.with_name(new_name))

    def rename_extensions(self, src_root):
        for rule in self.rename.ext:
            for pattern, cfg in rule.items():
                for path in self._iter_targets(src_root, pattern):
                    if not path.is_file():
                        continue

                    from_str, to_str = self._get_from_to(cfg)
                    from_ext = from_str.lstrip(".")
                    if path.suffix.lstrip(".") == from_ext:
                        to_ext = to_str if to_str.startswith(".") else f".{to_str}"
                        path.rename(path.with_suffix(to_ext))

    @staticmethod
    def _get_from_to(cfg):
        from_str = cfg.get("from_str", None)
        if None == from_str:
            raise Exception(f"Failed to get from_str of {cfg}")

        to_str = cfg.get("to_str", None)
        if None == to_str:
            raise Exception(f"Failed to get to_str of {cfg}")

        return from_str, to_str

    @staticmethod
    def _iter_targets(root: Path, pattern: str):
        if pattern.startswith("**/"):
            name = pattern[3:]
            yield from root.rglob(name)
        else:
            yield from root.glob(pattern)
