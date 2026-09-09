import json
import logging
from datetime import datetime
from pathlib import Path
from email_service import send_email

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
LEADS_FILE = DATA_DIR / "leads.jsonl"
QUESTIONS_FILE = DATA_DIR / "unknown_questions.jsonl"


def _ensure_data_dir() -> None:
    """Ensures the local data storage directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _append_record(file_path: Path, record: dict) -> bool:
    """Appends a single JSON record to the specified file safely."""
    try:
        _ensure_data_dir()
        with file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        logger.error(f"Failed to persist record to {file_path}: {e}")
        return False


def record_user(email: str, name: str = "-", notes: str = "-") -> dict[str, str]:
    """Records user lead details to local persistence and dispatches a notification email."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"🎯 New Portfolio Lead: {name}"
    body = (
        f"New contact from portfolio AI chatbot:\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Notes: {notes}\n\n"
        f"Time: {timestamp}\n"
    )

    # 1. Dispatch email notification (Resend -> SendGrid -> SMTP fallback)
    email_dispatched = False
    try:
        email_dispatched = bool(send_email(subject, body))
    except Exception as e:
        logger.error(f"Email notification failed for lead {email}: {e}")

    # 2. Persist lead locally so it is never lost
    record = {
        "timestamp": timestamp,
        "type": "lead",
        "name": name,
        "email": email,
        "notes": notes,
        "email_dispatched": email_dispatched,
    }
    _append_record(LEADS_FILE, record)

    return {"status": "ok"}


def record_issue(question: str) -> dict[str, str]:
    """Records unanswered questions to local persistence and notifies via email."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = "❓ Unknown Question from Portfolio AI"
    body = (
        f"AI chatbot received a question it couldn't answer:\n\n"
        f"Question: {question}\n\n"
        f"Time: {timestamp}\n"
    )

    # 1. Dispatch email notification
    email_dispatched = False
    try:
        email_dispatched = bool(send_email(subject, body))
    except Exception as e:
        logger.error(f"Email notification failed for question: {e}")

    # 2. Persist question locally
    record = {
        "timestamp": timestamp,
        "type": "unknown_question",
        "question": question,
        "email_dispatched": email_dispatched,
    }
    _append_record(QUESTIONS_FILE, record)

    return {"status": "ok"}
