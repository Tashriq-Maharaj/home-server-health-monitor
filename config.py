"""
Loads configuration from environment variables (via .env if present).
Keeping this separate means secrets never live in source code.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env in the current directory if it exists


def _require(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


class Config:
    BREVO_SMTP_HOST = _require("BREVO_SMTP_HOST")
    BREVO_SMTP_PORT = int(os.environ.get("BREVO_SMTP_PORT", 587))
    BREVO_USER = _require("BREVO_USER")
    BREVO_PASS = _require("BREVO_PASS")

    SENDER_EMAIL = _require("SENDER_EMAIL")
    RECEIVER_EMAIL = _require("RECEIVER_EMAIL")

    PROM_URL = _require("PROM_URL")

    # Add Telegram credentials here
    TELEGRAM_BOT_TOKEN = _require("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = _require("TELEGRAM_CHAT_ID")

    MSSQL_CONN_STR = (
        "DRIVER={{ODBC Driver 18 for SQL Server}};"
        "SERVER={host};DATABASE={db};UID={uid};PWD={pwd};"
        "TrustServerCertificate=yes;"
    ).format(
        host=_require("MSSQL_HOST"),
        db=os.environ.get("MSSQL_DATABASE", "master"),
        uid=_require("MSSQL_UID"),
        pwd=_require("MSSQL_PWD"),
    )