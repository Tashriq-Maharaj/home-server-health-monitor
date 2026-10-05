#!/usr/bin/env python3
"""
Entry point: run all checks, render the HTML template, email it via Brevo.

Run manually with: python3 send_report.py
Or on a schedule via cron / systemd timer.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

from config import Config
from report import run_all_checks

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("server_report")


def render_html(sections):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html.j2")
    return template.render(sections=sections)


def send_email(html_content: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📊 Daily Home Server Health Report"
    msg["From"] = Config.SENDER_EMAIL
    msg["To"] = Config.RECEIVER_EMAIL
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(Config.BREVO_SMTP_HOST, Config.BREVO_SMTP_PORT, timeout=15) as server:
        server.starttls()
        server.login(Config.BREVO_USER, Config.BREVO_PASS)
        server.sendmail(Config.SENDER_EMAIL, Config.RECEIVER_EMAIL, msg.as_string())


def main():
    log.info("Running checks...")
    sections = run_all_checks()

    log.info("Rendering report...")
    html_content = render_html(sections)

    log.info("Sending email...")
    try:
        send_email(html_content)
        log.info("Report sent successfully.")
    except Exception:
        log.exception("Failed to send email")
        raise


if __name__ == "__main__":
    main()
