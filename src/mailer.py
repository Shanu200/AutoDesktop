"""
mailer.py
---------
TASK 5.1: Send email with attachment using SMTP
"""

import smtplib
from pathlib import Path
from typing import Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def send_email_with_attachment(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_pass: str,
    mail_to: str,
    subject: str,
    body: str,
    attachment_path: Optional[Path] = None
) -> None:
    """
    Sends an email with optional attachment.
    """

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = mail_to
    msg["Subject"] = subject

    # Email body
    msg.attach(MIMEText(body, "plain"))

    # Attachment (Excel report)
    if attachment_path and attachment_path.exists():
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment_path.read_bytes())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{attachment_path.name}"'
        )
        msg.attach(part)

    # SMTP connection
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
