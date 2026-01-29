from __future__ import annotations

"""
backup.py
---------
TASK 3: Backup as ZIP + keep last N backups

What it does:
- Zips your Organized folder into a .zip file (timestamped)
- Stores backups inside: Organized/_backups/
- Keeps only the latest N backups (deletes older ones)

Why it matters:
- Undo / rollback support
- Safety for automation in real-world apps
"""

import zipfile
from pathlib import Path
from typing import List


def zip_folder(source_folder: Path, zip_path: Path) -> Path:
    """
    Create a zip file from source_folder.

    Example:
      source_folder = Downloads/Organized
      zip_path = Downloads/Organized/_backups/backup_2026-01-29_19-05-00.zip
    """
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # rglob("*") means scan all subfolders recursively
        for p in source_folder.rglob("*"):
            if p.is_file():
                # save file path relative to the source folder
                zf.write(p, p.relative_to(source_folder))

    return zip_path


def cleanup_old_backups(backup_dir: Path, keep_last: int) -> List[Path]:
    """
    Keep only newest `keep_last` zip files, delete the rest.
    Returns list of deleted backup files.
    """
    backups = sorted(
        backup_dir.glob("backup_*.zip"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    to_delete = backups[keep_last:]
    for p in to_delete:
        p.unlink(missing_ok=True)

    return to_delete
