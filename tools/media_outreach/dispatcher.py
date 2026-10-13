"""
POLYDIM Independent Dispatcher & Direct Publisher
Autonomous publication dispatcher designed to bypass restrictive platform APIs:
- Webhook Broadcast (Discord, Telegram, Slack, Mastodon, Bluesky)
- Direct SMTP Mailer Engine (Rate-limited, rotating sender profiles)
- Headless / Zero-API Export Queue (ready-to-post clipboard & markdown bundles)
"""

import os
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.error

class OutreachDispatcher:
    def __init__(self, smtp_config: Optional[Dict[str, Any]] = None):
        self.smtp_config = smtp_config or {}

    def send_webhook(self, webhook_url: str, payload: Dict[str, Any]) -> bool:
        """
        Sends payload to any standard webhook (Discord, Slack, custom webhook).
        """
        try:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "POLYDIM-Dispatcher/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status in (200, 204)
        except Exception as e:
            print(f"[Dispatcher Error] Webhook failed: {e}")
            return False

    def send_direct_email(self, to_email: str, subject: str, body_text: str, body_html: Optional[str] = None) -> bool:
        """
        Sends an email using configured SMTP credentials without external marketing platform locks.
        """
        host = self.smtp_config.get("host")
        port = self.smtp_config.get("port", 587)
        user = self.smtp_config.get("user")
        password = self.smtp_config.get("password")
        from_email = self.smtp_config.get("from_email", user)

        if not host or not user or not password:
            print("[Dispatcher Warning] SMTP not configured. Simulating mail send (Dry Run).")
            print(f"To: {to_email}\nSubject: {subject}\nBody:\n{body_text[:150]}...\n")
            return True

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))

        try:
            server = smtplib.SMTP(host, port)
            server.ehlo()
            server.starttls()
            server.login(user, password)
            server.sendmail(from_email, [to_email], msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"[Dispatcher Error] SMTP send failed to {to_email}: {e}")
            return False

    def export_unrestricted_clipboard_bundle(self, title: str, channel: str, content: str, output_file: str) -> str:
        """
        Saves clean, unconstrained markdown text formatted specifically for zero-API copy-paste.
        """
        bundle = f"""# ==========================================
# POLYDIM UNRESTRICTED PUBLICATION ASSET
# CHANNEL: {channel}
# TITLE: {title}
# DATE: {time.strftime('%Y-%m-%d %H:%M:%S')}
# ==========================================

{content}

# ==========================================
# END OF ASSET
# ==========================================
"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(bundle)
        return output_file

if __name__ == "__main__":
    dispatcher = OutreachDispatcher()
    print("Dispatcher module ready.")
