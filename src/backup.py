from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Iterable, List, Optional


def _is_inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def zip_folder(
    source_folder: Path,
    zip_path: Path,
    skip_dir_names: Optional[List[str]] = None,
    max_file_mb: Optional[int] = None
) -> Path:
    """
    Zips source_folder to zip_path safely.

    - allowZip64=True: supports very large files/archives (fixes force_zip64 error)
    - skip_dir_names: avoid zipping _backups folder (prevents zip growing forever)
    - max_file_mb: optional, skip files bigger than this (keeps backup fast)
    """
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    skip_dir_names = skip_dir_names or ["_backups"]
    skip_dirs = [source_folder / name for name in skip_dir_names]

    max_bytes = None
    if max_file_mb is not None:
        max_bytes = max_file_mb * 1024 * 1024

    # ✅ allowZip64=True fixes "File size too large"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        for p in source_folder.rglob("*"):
            if not p.is_file():
                continue

            # ✅ Skip backup folder itself
            if any(_is_inside(p, d) for d in skip_dirs):
                continue

            # ✅ Skip huge files if you set a limit
            if max_bytes is not None and p.stat().st_size > max_bytes:
                continue

            # ✅ Skip locked/unreadable files
            try:
                zf.write(p, p.relative_to(source_folder))
            except PermissionError:
                continue

    return zip_path


def cleanup_old_backups(backup_dir: Path, keep_last: int) -> List[Path]:
    backups = sorted(
        backup_dir.glob("backup_*.zip"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    to_delete = backups[keep_last:]
    for p in to_delete:
        p.unlink(missing_ok=True)
    return to_delete
