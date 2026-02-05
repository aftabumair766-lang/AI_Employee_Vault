"""
Email Integration - IMAP Reader (Cloud) + SMTP Sender (Local).

EmailReader: Connects to Gmail IMAP, fetches unread messages,
  creates JSON task files in Needs_Action/email/.
  Available to Cloud agent (read-only).

EmailSender: Connects to Gmail SMTP, sends approved email drafts.
  Available ONLY to Local agent (SecretGuard enforced).

Usage:
    from Platinum.src.config import get_settings
    settings = get_settings()

    reader = EmailReader(settings)
    new_tasks = reader.fetch_unread()

    sender = EmailSender(settings)
    sender.send(to="user@example.com", subject="Re: ...", body="...")
"""

import imaplib
import smtplib
import email
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger("platinum.email_client")


@dataclass
class EmailMessage:
    """Parsed email message."""
    message_id: str
    sender: str
    recipient: str
    subject: str
    body: str
    date: str
    uid: str = ""


class EmailReader:
    """IMAP email reader - fetches unread messages from inbox.

    Safe for Cloud agent: read-only, no send capability.
    Creates task files in Needs_Action/email/ for processing.
    """

    def __init__(self, settings):
        self.host = settings.IMAP_HOST
        self.port = settings.IMAP_PORT
        self.user = settings.IMAP_USER
        self.password = settings.IMAP_PASSWORD
        self.vault_path = Path(settings.VAULT_PATH)
        self._conn: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> bool:
        """Connect and authenticate to IMAP server."""
        if not self.user or not self.password:
            logger.warning("IMAP credentials not configured")
            return False
        try:
            self._conn = imaplib.IMAP4_SSL(self.host, self.port)
            self._conn.login(self.user, self.password)
            logger.info(f"Connected to IMAP: {self.host}")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP connection failed: {e}")
            self._conn = None
            return False

    def disconnect(self) -> None:
        """Close IMAP connection."""
        if self._conn:
            try:
                self._conn.close()
                self._conn.logout()
            except Exception:
                pass
            self._conn = None

    def fetch_unread(self, mailbox: str = "INBOX", limit: int = 20) -> List[EmailMessage]:
        """Fetch unread messages from the specified mailbox.

        Args:
            mailbox: IMAP mailbox to read from.
            limit: Maximum number of messages to fetch.

        Returns:
            List of EmailMessage objects.
        """
        if not self._conn:
            if not self.connect():
                return []

        messages = []
        try:
            self._conn.select(mailbox)
            _, msg_nums = self._conn.search(None, "UNSEEN")
            if not msg_nums[0]:
                return []

            uids = msg_nums[0].split()[-limit:]
            for uid in uids:
                _, msg_data = self._conn.fetch(uid, "(RFC822)")
                if msg_data[0] is None:
                    continue
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)
                parsed = self._parse_message(msg, uid.decode() if isinstance(uid, bytes) else str(uid))
                if parsed:
                    messages.append(parsed)

        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP fetch error: {e}")
        return messages

    def _parse_message(self, msg: email.message.Message, uid: str) -> Optional[EmailMessage]:
        """Parse a raw email message into an EmailMessage."""
        try:
            subject = self._decode_header(msg.get("Subject", ""))
            sender = self._decode_header(msg.get("From", ""))
            recipient = self._decode_header(msg.get("To", ""))
            date = msg.get("Date", "")
            message_id = msg.get("Message-ID", f"<{uid}@unknown>")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="replace")
                            break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="replace")

            return EmailMessage(
                message_id=message_id,
                sender=sender,
                recipient=recipient,
                subject=subject,
                body=body[:5000],  # Limit body size
                date=date,
                uid=uid,
            )
        except Exception as e:
            logger.error(f"Failed to parse message {uid}: {e}")
            return None

    @staticmethod
    def _decode_header(value: str) -> str:
        """Decode an email header value."""
        if not value:
            return ""
        decoded_parts = decode_header(value)
        result = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                result.append(part.decode(charset or "utf-8", errors="replace"))
            else:
                result.append(str(part))
        return " ".join(result)

    def create_task_files(self, messages: List[EmailMessage]) -> List[str]:
        """Create JSON task files in Needs_Action/email/ for each message.

        Args:
            messages: List of EmailMessage objects to create tasks from.

        Returns:
            List of created task file paths.
        """
        needs_dir = self.vault_path / "Platinum" / "Needs_Action" / "email"
        needs_dir.mkdir(parents=True, exist_ok=True)
        created = []

        for msg in messages:
            task_id = f"EMAIL-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{msg.uid}"
            task_data = {
                "task_id": task_id,
                "domain": "email",
                "title": msg.subject or "No Subject",
                "body": msg.body,
                "sender": msg.sender,
                "recipient": msg.recipient,
                "message_id": msg.message_id,
                "date": msg.date,
                "status": "NEEDS_ACTION",
                "created_at": datetime.utcnow().isoformat(),
            }
            task_file = needs_dir / f"{task_id}.json"
            task_file.write_text(json.dumps(task_data, indent=2), encoding="utf-8")
            created.append(str(task_file))
            logger.info(f"Created email task: {task_id}")

        return created

    def triage_inbox(self, mailbox: str = "INBOX", limit: int = 20) -> List[str]:
        """Full triage: fetch unread, create task files.

        Returns:
            List of created task file paths.
        """
        messages = self.fetch_unread(mailbox=mailbox, limit=limit)
        if messages:
            return self.create_task_files(messages)
        return []


class EmailSender:
    """SMTP email sender - sends approved email drafts.

    ONLY available to Local agent. SecretGuard enforced.
    Cloud agent must NEVER have SMTP credentials.
    """

    def __init__(self, settings):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.agent_role = settings.AGENT_ROLE

        # Enforce: Cloud agent NEVER sends email
        if self.agent_role == "cloud":
            raise PermissionError(
                "Cloud agent is not permitted to send emails. "
                "Only the Local agent has email send authority."
            )

    def send(self, to: str, subject: str, body: str,
             reply_to: Optional[str] = None,
             cc: Optional[List[str]] = None) -> bool:
        """Send an email via SMTP.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            body: Email body (plain text).
            reply_to: Optional In-Reply-To header for threading.
            cc: Optional CC recipients.

        Returns:
            True if sent successfully, False otherwise.
        """
        if not self.user or not self.password:
            logger.error("SMTP credentials not configured")
            return False

        msg = MIMEMultipart()
        msg["From"] = self.user
        msg["To"] = to
        msg["Subject"] = subject
        if reply_to:
            msg["In-Reply-To"] = reply_to
            msg["References"] = reply_to
        if cc:
            msg["Cc"] = ", ".join(cc)

        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.user, self.password)
                recipients = [to] + (cc or [])
                server.sendmail(self.user, recipients, msg.as_string())
            logger.info(f"Email sent to {to}: {subject}")
            return True
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending to {to}: {e}")
            return False

    def send_draft(self, draft_data: dict) -> bool:
        """Send an email from an approved draft.

        Args:
            draft_data: Dict with keys: to, subject, body, reply_to (optional).

        Returns:
            True if sent successfully.
        """
        return self.send(
            to=draft_data.get("to", ""),
            subject=draft_data.get("subject", ""),
            body=draft_data.get("body", ""),
            reply_to=draft_data.get("reply_to"),
        )
