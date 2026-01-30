"""
task4_email_report.py

"""

import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from src.mailer import send_email_with_attachment

load_dotenv()

if __name__ == "__main__":
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    mail_to = os.getenv("MAIL_TO")

    # select latest report
    reports = sorted(Path("reports").glob("report_*.xlsx"))
    if not reports:
        raise FileNotFoundError("No report found. Run Task 2 first.")

    report_path = reports[-1]

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
        attachment_path=report_path
    )

    print(" Report email sent successfully")
