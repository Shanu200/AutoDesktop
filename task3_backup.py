"""
task3_backup.py
---------------
Runs backup for Organized folder and applies retention policy (keep last N).
"""

import json
from pathlib import Path
from datetime import datetime

from src.backup import zip_folder, cleanup_old_backups


def load_rules(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


if __name__ == "__main__":
    cfg = load_rules("config/rules.json")

    base_folder = Path(cfg["base_folder"])
    target_root = cfg["target_root_folder"]
    backup_cfg = cfg.get("backup", {"enabled": False})

    if not backup_cfg.get("enabled", False):
        print("Backup is disabled in rules.json")
        raise SystemExit(0)

    organized_folder = base_folder / target_root
    if not organized_folder.exists():
        print("❌ Organized folder not found:", organized_folder)
        print("Run Task 1 organizer first.")
        raise SystemExit(1)

    backup_dir = organized_folder / backup_cfg.get("backup_folder_name", "_backups")
    keep_last = int(backup_cfg.get("keep_last", 5))

    zip_path = backup_dir / f"backup_{now_stamp()}.zip"

    print("Creating backup:", zip_path)
    zip_folder(organized_folder, zip_path)

    deleted = cleanup_old_backups(backup_dir, keep_last=keep_last)

    print("✅ Backup created.")
    print("Deleted old backups:", len(deleted))
