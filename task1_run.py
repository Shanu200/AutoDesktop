"""
task1_run.py
------------
This is a simple test runner for Task 1 only.
It reads config/rules.json and runs organize_folder().
"""

import json
from pathlib import Path
from src.organizer import organize_folder


def load_rules(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    cfg = load_rules("config/rules.json")

    base_folder = Path(cfg["base_folder"])
    moved_files, summary = organize_folder(
        base_folder=base_folder,
        target_root_folder=cfg["target_root_folder"],
        categories=cfg["categories"],
        unknown_category=cfg["unknown_category"],
        ignore_folders=cfg["ignore_folders"] + [cfg["target_root_folder"]],
        dry_run=False  # start with dry run
    )

    print("=== DRY RUN RESULT ===")
    print("Moved count:", summary["moved_count"])
    for f in moved_files:
        print(f["category"], "=>", Path(f["src"]).name, "->", f["dst"])
