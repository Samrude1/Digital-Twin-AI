import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests


def _send_via_resend(api_key: str, recipient: str, subject: str, body: str) -> bool:
    """Send an email using Resend API."""
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "from": "Portfolio AI <onboarding@resend.dev>",
                "to": [recipient],
                "subject": subject,
                "text": body,
            },
            timeout=10,
        )
        response.raise_for_status()
        print(f"Email sent via Resend! ID: {response.json().get('id')}")
        return True
    except Exception as e:
        print(f"Resend API failed: {e}")
        return False


def _send_via_sendgrid(api_key: str, recipient: str, from_email: str, subject: str, body: str) -> bool:
    """Send an email using SendGrid API."""
    try:
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "personalizations": [{"to": [{"email": recipient}]}],
                "from": {"email": from_email},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body}],
            },
            timeout=10,
        )
        if response.status_code in [200, 201, 202]:
            print(f"Email sent via SendGrid! Status: {response.status_code}")
            return True
        print(f"SendGrid failed: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        print(f"SendGrid API failed: {e}")
        return False


def _send_via_smtp(smtp_email: str, smtp_password: str, recipient: str, subject: str, body: str) -> bool:
    """Send an email using SMTP (Gmail fallback)."""
    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_email
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(smtp_email, smtp_password)
            server.send_message(msg)

        print(f"Email sent via SMTP successfully: {subject}")
        return True
    except Exception as e:
        print(f"Failed to send email via SMTP: {e}")
        return False


def send_email(subject: str, body: str) -> bool:
    """Dispatch email via Resend, SendGrid, or SMTP fallback based on configuration."""
    recipient_email = os.getenv("RECIPIENT_EMAIL", "").strip()
    smtp_email = os.getenv("SMTP_EMAIL", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
    from_email = os.getenv("SENDGRID_VERIFIED_SENDER", "").strip() or smtp_email or "no-reply@portfolio.com"

    resend_key = os.getenv("RESEND_API_KEY", "").strip()
    if resend_key and _send_via_resend(resend_key, recipient_email, subject, body):
        return True

    sendgrid_key = os.getenv("SENDGRID_API_KEY", "").strip()
    if sendgrid_key and _send_via_sendgrid(sendgrid_key, recipient_email, from_email, subject, body):
        return True

    if smtp_email and smtp_password and recipient_email:
        return _send_via_smtp(smtp_email, smtp_password, recipient_email, subject, body)

    print("Email not configured (No Resend/SendGrid Key, No SMTP details).")
    return False
