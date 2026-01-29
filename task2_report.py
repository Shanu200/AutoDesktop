"""
task2_report.py
---------------
Reads runs/last_run.json and generates an Excel report.
"""

import json
from pathlib import Path
from datetime import datetime
from src.reporter import generate_excel_report


def load_last_run(path: str = "runs/last_run.json") -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError("runs/last_run.json not found. Run task1_run.py first.")
    return json.loads(p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    run_data = load_last_run()
    moved_files = run_data["moved_files"]

    report_path = Path("reports") / f"report_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    out = generate_excel_report(moved_files, report_path)

    print("✅ Excel report created:", out)
