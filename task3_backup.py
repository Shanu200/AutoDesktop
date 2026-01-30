import json
from pathlib import Path
from datetime import datetime

from src.backup import zip_folder, cleanup_old_backups
from src.logger_utils import setup_logger


def load_rules(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


if __name__ == "__main__":
    logger = setup_logger()

    try:
        cfg = load_rules("config/rules.json")

        base_folder = Path(cfg["base_folder"])
        target_root = cfg["target_root_folder"]
        backup_cfg = cfg.get("backup", {"enabled": False})

        if not backup_cfg.get("enabled", False):
            logger.info("Backup is disabled in rules.json")
            raise SystemExit(0)

        organized_folder = base_folder / target_root
        if not organized_folder.exists():
            logger.error(f"Organized folder not found: {organized_folder}")
            logger.error("Run Task 1 organizer first.")
            raise SystemExit(1)

        backup_dir = organized_folder / backup_cfg.get("backup_folder_name", "_backups")
        keep_last = int(backup_cfg.get("keep_last", 5))

        zip_path = backup_dir / f"backup_{now_stamp()}.zip"

        logger.info(f"Creating backup zip: {zip_path}")
        zip_folder(organized_folder,
                   zip_path,skip_dir_names=["_backups"],
                   max_file_mb=500 )

        deleted = cleanup_old_backups(backup_dir, keep_last=keep_last)
        logger.info(f"Backup complete. Deleted old backups: {len(deleted)}")

        logger.info("Task 3 finished successfully ✅")

    except Exception as e:
        # logger.exception prints full stack trace to logs/app.log
        logger.exception(f"Task 3 failed ❌: {e}")
        raise
