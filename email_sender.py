"""
email_sender.py — Nazil email module.
Sends PDF reports and documents to clients via Gmail SMTP.
"""

from __future__ import annotations
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional
import streamlit as st


def _creds() -> tuple[str, str]:
    def s(k):
        try:
            return st.secrets[k]
        except Exception:
            import os
            return os.getenv(k, "")
    return s("EMAIL_ADDRESS"), s("EMAIL_PASSWORD")


def send_email(
    to: str,
    subject: str,
    body_html: str,
    attachment_bytes: Optional[bytes] = None,
    attachment_name: Optional[str] = None,
) -> tuple[bool, str]:
    """Send an email. Returns (success, error_message)."""
    sender, password = _creds()
    if not sender or not password:
        return False, "פרטי מייל לא מוגדרים ב-Secrets."
    if not to or "@" not in to:
        return False, "כתובת מייל לקוח לא תקינה."

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Nazil <{sender}>"
    msg["To"]      = to

    msg.attach(MIMEText(body_html, "html", "utf-8"))

    if attachment_bytes and attachment_name:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{attachment_name}"')
        msg.attach(part)

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as srv:
            srv.starttls(context=ctx)
            srv.login(sender, password.replace(" ", ""))
            srv.sendmail(sender, to, msg.as_string())
        return True, ""
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Email templates
# ---------------------------------------------------------------------------

def template_report(client_name: str, agent_name: str = "צוות נאזיל") -> str:
    return f"""
<div dir="rtl" style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
     background:#f9f9f9;border-radius:12px;overflow:hidden">
  <div style="background:#1a237e;padding:24px 32px">
    <h1 style="color:#fff;margin:0;font-size:22px">Nazil 💰</h1>
    <p style="color:#8fa8e8;margin:4px 0 0;font-size:13px">ניתוח קרנות פנסיה אישי</p>
  </div>
  <div style="padding:32px;background:#fff">
    <p style="font-size:16px;color:#222">שלום <strong>{client_name}</strong>,</p>
    <p style="color:#444;line-height:1.7">
      מצורף דוח הניתוח האישי שלך. הדוח מסכם את מצב קרנות הפנסיה שלך
      ומציג את האפשרויות העומדות בפניך.
    </p>
    <p style="color:#444;line-height:1.7">
      לכל שאלה — אנחנו כאן.
    </p>
    <p style="color:#666;font-size:14px;margin-top:32px;border-top:1px solid #eee;padding-top:16px">
      {agent_name} | Nazil<br>
      <span style="color:#999;font-size:12px">
        מידע זה הינו סימולציה בלבד ואינו מהווה ייעוץ פנסיוני.
      </span>
    </p>
  </div>
</div>"""


def template_followup(client_name: str, message: str, agent_name: str = "צוות נאזיל") -> str:
    return f"""
<div dir="rtl" style="font-family:Arial,sans-serif;max-width:600px;margin:auto;
     background:#f9f9f9;border-radius:12px;overflow:hidden">
  <div style="background:#1a237e;padding:24px 32px">
    <h1 style="color:#fff;margin:0;font-size:22px">Nazil 💰</h1>
  </div>
  <div style="padding:32px;background:#fff">
    <p style="font-size:16px;color:#222">שלום <strong>{client_name}</strong>,</p>
    <p style="color:#444;line-height:1.7">{message}</p>
    <p style="color:#666;font-size:14px;margin-top:32px;border-top:1px solid #eee;padding-top:16px">
      {agent_name} | Nazil
    </p>
  </div>
</div>"""
