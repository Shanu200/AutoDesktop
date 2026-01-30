"""
task1_run.py

"""

import json
from pathlib import Path
from datetime import datetime
from src.organizer import organize_folder


def load_rules(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def save_run(moved_files: list, summary: dict) -> Path:
    """
    Save moved file records + summary to JSON.
    This creates an audit log we can use for reporting.
    """
    Path("runs").mkdir(exist_ok=True)

    payload = {
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "summary": summary,
        "moved_files": moved_files
    }

    out_path = Path("runs/last_run.json")
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path

if __name__ == "__main__":
    cfg = load_rules("config/rules.json")
    base_folder = Path(cfg["base_folder"])
    
    DRY_RUN = False
    
    moved_files, summary = organize_folder(
        base_folder=base_folder,
        target_root_folder=cfg["target_root_folder"],
        categories=cfg["categories"],
        unknown_category=cfg["unknown_category"],
        ignore_folders=cfg["ignore_folders"] + [cfg["target_root_folder"]],
        dry_run=DRY_RUN  # start dry run
    )

    print("=== ORGANIZER RESULT ===")
    print("Dry run:", DRY_RUN)
    print("Moved count:", summary["moved_count"])
    for f in moved_files:
        print(f["category"], "=>", Path(f["src"]).name, "->", f["dst"])
        
    saved = save_run(moved_files, summary)
    print("\nSaved run log to:", saved)
