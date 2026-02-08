from pathlib import Path

from flowweave import FlowWeaveResult

from .file_system import FileSystem
from .lock_manager import get_path_lock

class RenameStr():
    def __init__(self):
        self.from_str = ""
        self.to_str = ""

class RenameCfg():
    def __init__(self):
        self.files = list[dict(str, RenameStr)]
        self.folders = list[dict(str, RenameStr)]
        self.ext = list[dict(str, RenameStr)]

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

                    new_name = path.name.replace(cfg.from_str, cfg.to_str)
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

                    new_name = path.name.replace(cfg.from_str, cfg.to_str)
                    if new_name != path.name:
                        path.rename(path.with_name(new_name))

    def rename_extensions(self, src_root):
        for rule in self.rename.ext:
            for pattern, cfg in rule.items():
                for path in self._iter_targets(src_root, pattern):
                    if not path.is_file():
                        continue

                    if path.suffix == cfg.from_str:
                        path.rename(path.with_suffix(cfg.to_str))

    @staticmethod
    def _iter_targets(root: Path, pattern: str):
        if pattern.startswith("**/"):
            name = pattern[3:]
            yield from root.rglob(name)
        else:
            yield from root.glob(pattern)
