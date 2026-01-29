from __future__ import annotations

"""
organizer.py
------------
TASK 1: Downloads Cleaner / File Organizer

What this module does:
- Reads files from ONE folder (base_folder)
- Finds each file’s extension (.pdf, .jpg, .zip, etc.)
- Decides a category folder (PDFs, Images, Archives...)
- Moves the file to: base_folder/Organized/<Category>/
- Avoids overwriting if a file with the same name already exists
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any


def build_extension_map(categories: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Converts your config categories into a quick lookup dictionary.

    Example input:
        {"Images": [".jpg", ".png"], "PDFs": [".pdf"]}

    Output:
        {".jpg": "Images", ".png": "Images", ".pdf": "PDFs"}

    Why we do this:
    - Faster to look up category by file extension
    - Cleaner logic in organize_folder()
    """
    ext_map: Dict[str, str] = {}

    for category_name, ext_list in categories.items():
        for ext in ext_list:
            ext_map[ext.lower()] = category_name  # store lowercase for safe matching

    return ext_map


def safe_move(src: Path, dst: Path) -> Path:
    """
    Moves a file from src -> dst safely without overwriting.

    Problem:
        If dst already exists, moving will overwrite or fail.

    Solution:
        If dst exists, rename like:
            file.pdf
            file (1).pdf
            file (2).pdf

    Returns:
        The final destination path used.
    """
    # If destination does not exist, normal move is fine
    if not dst.exists():
        shutil.move(str(src), str(dst))
        return dst

    # If destination exists, we generate a new filename
    stem = dst.stem       # filename without extension
    suffix = dst.suffix   # extension (example: .pdf)
    parent = dst.parent   # folder path

    i = 1
    while True:
        # Create candidate path: "file (1).pdf"
        candidate = parent / f"{stem} ({i}){suffix}"

        if not candidate.exists():
            shutil.move(str(src), str(candidate))
            return candidate

        i += 1


def organize_folder(
    base_folder: Path,
    target_root_folder: str,
    categories: Dict[str, List[str]],
    unknown_category: str,
    ignore_folders: List[str],
    dry_run: bool = False
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Organizes files inside base_folder into category folders.

    Parameters:
        base_folder: The folder containing files to organize
        target_root_folder: The root folder name where we store results (example: "Organized")
        categories: category -> list of file extensions
        unknown_category: where unknown file extensions go
        ignore_folders: folders inside base_folder that we must NOT touch
        dry_run: if True, DO NOT move files, only show what would happen

    Returns:
        moved_files: list of dictionaries, each describing a moved file
        summary: dictionary with summary info (moved_count, paths)
    """
    # Create extension -> category map
    ext_map = build_extension_map(categories)

    # This is the "Organized" folder path
    target_root_path = base_folder / target_root_folder

    moved_files: List[Dict[str, Any]] = []

    # Loop through items in the base folder (top level only)
    for item in base_folder.iterdir():

        # Skip folders
        if item.is_dir():
            # If folder is in ignore list, skip
            if item.name in ignore_folders:
                continue
            # We skip all folders anyway (this tool only organizes files)
            continue

        # Skip anything that's not a file
        if not item.is_file():
            continue

        # Identify file extension (example: ".pdf")
        ext = item.suffix.lower()

        # Decide category based on extension (if not found -> unknown_category)
        category = ext_map.get(ext, unknown_category)

        # Create destination folder: base/Organized/<Category>
        dest_dir = target_root_path / category

        # Destination file path
        dest_path = dest_dir / item.name

        # Record metadata for logging/reporting later
        file_info = {
            "src": str(item),
            "dst": str(dest_path),
            "category": category,
            "size_bytes": item.stat().st_size,
            "moved_at": datetime.now().isoformat(timespec="seconds"),
            "dry_run": dry_run
        }

        # If dry_run, we do NOT move. Just record what WOULD happen.
        if dry_run:
            moved_files.append(file_info)
            continue

        # Create destination folder if it doesn't exist
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Move file safely
        final_path = safe_move(item, dest_path)

        # Update the recorded destination to final path (in case it was renamed)
        file_info["dst"] = str(final_path)

        moved_files.append(file_info)

    summary = {
        "base_folder": str(base_folder),
        "target_root": str(target_root_path),
        "moved_count": len(moved_files)
    }

    return moved_files, summary
