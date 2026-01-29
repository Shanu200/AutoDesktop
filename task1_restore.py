"""
task1_restore.py
----------------
This script REVERSES the file organization.

It moves files from:
    base_folder/Organized/<Category>/<file>

Back to:
    base_folder/<file>

This is a SAFE undo operation.
"""

from pathlib import Path
import shutil
import json


def safe_move_back(src: Path, dst: Path) -> Path:
    """
    Move file back safely.
    If file already exists in base folder, rename it.
    """
    if not dst.exists():
        shutil.move(str(src), str(dst))
        return dst

    stem = dst.stem
    suffix = dst.suffix
    parent = dst.parent

    i = 1
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            shutil.move(str(src), str(candidate))
            return candidate
        i += 1


def load_rules(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    cfg = load_rules("config/rules.json")

    base_folder = Path(cfg["base_folder"])
    organized_folder = base_folder / cfg["target_root_folder"]

    print("Restoring files from:", organized_folder)

    if not organized_folder.exists():
        print("❌ Organized folder not found. Nothing to restore.")
        exit()

    moved_back = 0

    # Loop through category folders
    for category_dir in organized_folder.iterdir():
        if not category_dir.is_dir():
            continue

        # Loop through files inside each category
        for file in category_dir.iterdir():
            if not file.is_file():
                continue

            dest_path = base_folder / file.name
            safe_move_back(file, dest_path)
            moved_back += 1

    print(f"✅ Restore complete. Files moved back: {moved_back}")
