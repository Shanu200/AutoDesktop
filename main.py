from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

from src.organizer import organize_folder
from src.reporter import generate_excel_report
from src.backup import zip_folder, cleanup_old_backups
from src.logger_utils import setup_logger
from src.mailer import send_email_with_attachment



# (config + run log)

def load_rules(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_run(moved_files: list, summary: dict) -> Path:
    """Save moved file list into runs/last_run.json (used for reporting)."""
    Path("runs").mkdir(exist_ok=True)
    payload = {
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "summary": summary,
        "moved_files": moved_files,
    }
    out_path = Path("runs/last_run.json")
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path


def load_last_run(path: str = "runs/last_run.json") -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError("runs/last_run.json not found. Run --organize first.")
    return json.loads(p.read_text(encoding="utf-8"))


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")



# CLI args

def parse_args():
    p = argparse.ArgumentParser(description="AutoDesktop - Organizer + Report + Backup + Email")
    p.add_argument("--config", default="config/rules.json")
    p.add_argument("--dry-run", action="store_true")

    p.add_argument("--organize", action="store_true")
    p.add_argument("--report", action="store_true")
    p.add_argument("--backup", action="store_true")
    p.add_argument("--email", action="store_true")

    p.add_argument("--run-all", action="store_true")

    return p.parse_args()



# Email (report + error alert)

def send_report_email(logger, report_path: Path):
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    mail_to = os.getenv("MAIL_TO", "")

    if not all([smtp_host, smtp_user, smtp_pass, mail_to]):
        logger.warning("Email config missing in .env. Skipping report email.")
        return

    subject = f"Automation Report - {datetime.now().strftime('%Y-%m-%d')}"
    body = (
        "Hi,\n\n"
        "Please find attached the latest automation report.\n\n"
        "Regards,\n"
        "AutoDesk Assistant"
    )

    send_email_with_attachment(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_pass=smtp_pass,
        mail_to=mail_to,
        subject=subject,
        body=body,
        attachment_path=report_path if report_path.exists() else None
    )

    logger.info("Report email sent")


def send_error_alert_email(logger, error_text: str):
    """Send logs/app.log as attachment when something fails."""
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    mail_to = os.getenv("MAIL_TO", "")

    if not all([smtp_host, smtp_user, smtp_pass, mail_to]):
        logger.info("Email config missing in .env. Error alert email not sent.")
        return

    log_path = Path("logs/app.log")
    send_email_with_attachment(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_pass=smtp_pass,
        mail_to=mail_to,
        subject=" AutoDesktop Automation Failed",
        body=f"Automation failed.\n\nError:\n{error_text}\n\nSee attached log file.",
        attachment_path=log_path if log_path.exists() else None
    )
    logger.info("Error alert email sent (log attached)")



# Main

def main():
    load_dotenv()  # load .env for SMTP settings 
    args = parse_args()
    logger = setup_logger()

    cfg = load_rules(args.config)
    base_folder = Path(cfg["base_folder"])
    target_root = cfg["target_root_folder"]

    run_all = args.run_all or not (args.organize or args.report or args.backup or args.email)

    do_organize = run_all or args.organize
    do_report = run_all or args.report
    do_backup = run_all or args.backup
    do_email = run_all or args.email

    moved_files = []
    summary = {}

    # Report path
    report_path = Path("reports") / f"report_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    Path("reports").mkdir(exist_ok=True)

    try:
        # 1) ORGANIZE
        if do_organize:
            logger.info(f"Organizing: {base_folder} (dry_run={args.dry_run})")

            moved_files, summary = organize_folder(
                base_folder=base_folder,
                target_root_folder=target_root,
                categories=cfg["categories"],
                unknown_category=cfg["unknown_category"],
                ignore_folders=cfg["ignore_folders"] + [target_root],
                dry_run=args.dry_run
            )

            logger.info(f"Moved count: {summary['moved_count']}")

            # Save for reporting
            saved = save_run(moved_files, summary)
            logger.info(f"Saved run log: {saved}")

        #  Generate REPORT from last_run.json
        if do_report:
            logger.info("Generating Excel report...")

            run_data = load_last_run()
            moved_for_report = run_data["moved_files"]

            generate_excel_report(moved_for_report, report_path)
            logger.info(f"Report created: {report_path}")

        #  BACKUP
        if do_backup:
            backup_cfg = cfg.get("backup", {"enabled": False})
            if not backup_cfg.get("enabled", False):
                logger.info("Backup disabled in rules.json")
            else:
                organized_folder = base_folder / target_root
                if not organized_folder.exists():
                    raise FileNotFoundError(f"Organized folder not found: {organized_folder}")

                backup_dir = organized_folder / backup_cfg.get("backup_folder_name", "_backups")
                keep_last = int(backup_cfg.get("keep_last", 5))
                zip_path = backup_dir / f"backup_{now_stamp()}.zip"

                logger.info(f"Creating backup zip: {zip_path}")

                zip_folder(
                    organized_folder,
                    zip_path,
                    skip_dir_names=["_backups"],
                    max_file_mb=500
                )

                deleted = cleanup_old_backups(backup_dir, keep_last=keep_last)
                logger.info(f"Backup done. Deleted old backups: {len(deleted)}")

        # send latest report
        if do_email:
            # pick latest report file
            reports = sorted(Path("reports").glob("report_*.xlsx"))
            if not reports:
                raise FileNotFoundError("No report found. Run --report first.")
            latest_report = reports[-1]

            logger.info(f"Emailing report: {latest_report}")
            send_report_email(logger, latest_report)

        logger.info("All selected tasks completed successfully")

    except Exception as e:
        # Log full stack trace
        logger.exception(f" Pipeline failed: {e}")

        # Send error alert email 
        try:
            send_error_alert_email(logger, str(e))
        except Exception as mail_err:
            logger.error(f"Error alert email failed: {mail_err}")

        raise


if __name__ == "__main__":
    main()
