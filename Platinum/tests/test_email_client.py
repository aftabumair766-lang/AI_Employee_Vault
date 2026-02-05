"""
Tests for EmailReader and EmailSender.
Uses mocked IMAP/SMTP to avoid real network calls.
"""

import json
import pytest
import imaplib
import smtplib
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
from types import SimpleNamespace

from Platinum.src.email_client import EmailReader, EmailSender, EmailMessage


# ========== Fixtures ==========

@pytest.fixture
def mock_settings_local(tmp_path):
    """Settings for Local agent with full credentials."""
    return SimpleNamespace(
        AGENT_ROLE="local",
        VAULT_PATH=str(tmp_path),
        IMAP_HOST="imap.gmail.com",
        IMAP_PORT=993,
        IMAP_USER="test@gmail.com",
        IMAP_PASSWORD="app-password-123",
        SMTP_HOST="smtp.gmail.com",
        SMTP_PORT=587,
        SMTP_USER="test@gmail.com",
        SMTP_PASSWORD="app-password-123",
    )


@pytest.fixture
def mock_settings_cloud(tmp_path):
    """Settings for Cloud agent with IMAP only."""
    return SimpleNamespace(
        AGENT_ROLE="cloud",
        VAULT_PATH=str(tmp_path),
        IMAP_HOST="imap.gmail.com",
        IMAP_PORT=993,
        IMAP_USER="test@gmail.com",
        IMAP_PASSWORD="app-password-123",
        SMTP_HOST="",
        SMTP_PORT=587,
        SMTP_USER="",
        SMTP_PASSWORD="",
    )


@pytest.fixture
def mock_settings_no_creds(tmp_path):
    """Settings with no credentials configured."""
    return SimpleNamespace(
        AGENT_ROLE="local",
        VAULT_PATH=str(tmp_path),
        IMAP_HOST="imap.gmail.com",
        IMAP_PORT=993,
        IMAP_USER="",
        IMAP_PASSWORD="",
        SMTP_HOST="smtp.gmail.com",
        SMTP_PORT=587,
        SMTP_USER="",
        SMTP_PASSWORD="",
    )


def _make_raw_email(subject="Test Subject", sender="alice@example.com",
                     to="test@gmail.com", body="Hello, this is a test."):
    """Create a raw RFC822 email bytes."""
    return (
        f"From: {sender}\r\n"
        f"To: {to}\r\n"
        f"Subject: {subject}\r\n"
        f"Message-ID: <msg-001@example.com>\r\n"
        f"Date: Mon, 1 Jan 2024 12:00:00 +0000\r\n"
        f"\r\n"
        f"{body}\r\n"
    ).encode("utf-8")


# ========== EmailReader Tests ==========

class TestEmailReader:

    def test_init(self, mock_settings_cloud):
        reader = EmailReader(mock_settings_cloud)
        assert reader.host == "imap.gmail.com"
        assert reader.port == 993
        assert reader.user == "test@gmail.com"

    @patch("Platinum.src.email_client.imaplib.IMAP4_SSL")
    def test_connect_success(self, mock_imap_cls, mock_settings_cloud):
        mock_conn = MagicMock()
        mock_imap_cls.return_value = mock_conn
        reader = EmailReader(mock_settings_cloud)
        assert reader.connect() is True
        mock_imap_cls.assert_called_once_with("imap.gmail.com", 993)
        mock_conn.login.assert_called_once_with("test@gmail.com", "app-password-123")

    @patch("Platinum.src.email_client.imaplib.IMAP4_SSL")
    def test_connect_failure(self, mock_imap_cls, mock_settings_cloud):
        mock_imap_cls.side_effect = imaplib.IMAP4.error("Auth failed")
        reader = EmailReader(mock_settings_cloud)
        assert reader.connect() is False
        assert reader._conn is None

    def test_connect_no_credentials(self, mock_settings_no_creds):
        reader = EmailReader(mock_settings_no_creds)
        assert reader.connect() is False

    @patch("Platinum.src.email_client.imaplib.IMAP4_SSL")
    def test_fetch_unread(self, mock_imap_cls, mock_settings_cloud):
        mock_conn = MagicMock()
        mock_imap_cls.return_value = mock_conn
        mock_conn.select.return_value = ("OK", [b"1"])
        mock_conn.search.return_value = ("OK", [b"1 2"])
        raw_email = _make_raw_email()
        mock_conn.fetch.return_value = ("OK", [(b"1", raw_email)])

        reader = EmailReader(mock_settings_cloud)
        reader.connect()
        messages = reader.fetch_unread()
        assert len(messages) == 2  # Two UIDs fetched

    @patch("Platinum.src.email_client.imaplib.IMAP4_SSL")
    def test_fetch_unread_empty(self, mock_imap_cls, mock_settings_cloud):
        mock_conn = MagicMock()
        mock_imap_cls.return_value = mock_conn
        mock_conn.select.return_value = ("OK", [b"0"])
        mock_conn.search.return_value = ("OK", [b""])

        reader = EmailReader(mock_settings_cloud)
        reader.connect()
        messages = reader.fetch_unread()
        assert messages == []

    @patch("Platinum.src.email_client.imaplib.IMAP4_SSL")
    def test_fetch_unread_imap_error(self, mock_imap_cls, mock_settings_cloud):
        mock_conn = MagicMock()
        mock_imap_cls.return_value = mock_conn
        mock_conn.select.return_value = ("OK", [b"1"])
        mock_conn.search.side_effect = imaplib.IMAP4.error("Search failed")

        reader = EmailReader(mock_settings_cloud)
        reader.connect()
        messages = reader.fetch_unread()
        assert messages == []

    def test_parse_message(self, mock_settings_cloud):
        reader = EmailReader(mock_settings_cloud)
        import email as emailmod
        raw = _make_raw_email(subject="Invoice #123", sender="bob@example.com")
        msg = emailmod.message_from_bytes(raw)
        parsed = reader._parse_message(msg, "42")
        assert parsed is not None
        assert parsed.subject == "Invoice #123"
        assert parsed.sender == "bob@example.com"
        assert parsed.uid == "42"

    def test_decode_header_plain(self, mock_settings_cloud):
        reader = EmailReader(mock_settings_cloud)
        assert reader._decode_header("Hello World") == "Hello World"

    def test_decode_header_empty(self, mock_settings_cloud):
        reader = EmailReader(mock_settings_cloud)
        assert reader._decode_header("") == ""

    def test_create_task_files(self, mock_settings_cloud):
        reader = EmailReader(mock_settings_cloud)
        messages = [
            EmailMessage(
                message_id="<msg-001@example.com>",
                sender="alice@example.com",
                recipient="test@gmail.com",
                subject="Meeting Tomorrow",
                body="Let's meet at 10 AM.",
                date="Mon, 1 Jan 2024 12:00:00 +0000",
                uid="1",
            ),
        ]
        created = reader.create_task_files(messages)
        assert len(created) == 1
        task_path = Path(created[0])
        assert task_path.exists()
        data = json.loads(task_path.read_text(encoding="utf-8"))
        assert data["domain"] == "email"
        assert data["title"] == "Meeting Tomorrow"
        assert data["sender"] == "alice@example.com"
        assert data["status"] == "NEEDS_ACTION"

    def test_create_task_files_no_subject(self, mock_settings_cloud):
        reader = EmailReader(mock_settings_cloud)
        messages = [
            EmailMessage(
                message_id="<msg-002@example.com>",
                sender="bob@example.com",
                recipient="test@gmail.com",
                subject="",
                body="No subject here.",
                date="Mon, 1 Jan 2024 12:00:00 +0000",
                uid="2",
            ),
        ]
        created = reader.create_task_files(messages)
        data = json.loads(Path(created[0]).read_text(encoding="utf-8"))
        assert data["title"] == "No Subject"

    @patch("Platinum.src.email_client.imaplib.IMAP4_SSL")
    def test_triage_inbox(self, mock_imap_cls, mock_settings_cloud):
        mock_conn = MagicMock()
        mock_imap_cls.return_value = mock_conn
        mock_conn.select.return_value = ("OK", [b"1"])
        mock_conn.search.return_value = ("OK", [b"1"])
        raw_email = _make_raw_email(subject="Urgent")
        mock_conn.fetch.return_value = ("OK", [(b"1", raw_email)])

        reader = EmailReader(mock_settings_cloud)
        reader.connect()
        tasks = reader.triage_inbox()
        assert len(tasks) == 1

    def test_disconnect(self, mock_settings_cloud):
        reader = EmailReader(mock_settings_cloud)
        reader._conn = MagicMock()
        reader.disconnect()
        assert reader._conn is None

    @patch("Platinum.src.email_client.imaplib.IMAP4_SSL")
    def test_fetch_auto_connects(self, mock_imap_cls, mock_settings_cloud):
        """fetch_unread auto-connects if not already connected."""
        mock_conn = MagicMock()
        mock_imap_cls.return_value = mock_conn
        mock_conn.select.return_value = ("OK", [b"0"])
        mock_conn.search.return_value = ("OK", [b""])

        reader = EmailReader(mock_settings_cloud)
        assert reader._conn is None
        reader.fetch_unread()
        mock_imap_cls.assert_called_once()


# ========== EmailSender Tests ==========

class TestEmailSender:

    def test_cloud_agent_blocked(self, mock_settings_cloud):
        """Cloud agent cannot instantiate EmailSender."""
        with pytest.raises(PermissionError, match="Cloud agent is not permitted"):
            EmailSender(mock_settings_cloud)

    def test_local_agent_allowed(self, mock_settings_local):
        sender = EmailSender(mock_settings_local)
        assert sender.user == "test@gmail.com"

    @patch("Platinum.src.email_client.smtplib.SMTP")
    def test_send_success(self, mock_smtp_cls, mock_settings_local):
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        sender = EmailSender(mock_settings_local)
        result = sender.send(
            to="alice@example.com",
            subject="Re: Meeting",
            body="See you at 10 AM.",
        )
        assert result is True

    @patch("Platinum.src.email_client.smtplib.SMTP")
    def test_send_with_reply_to(self, mock_smtp_cls, mock_settings_local):
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        sender = EmailSender(mock_settings_local)
        result = sender.send(
            to="alice@example.com",
            subject="Re: Invoice",
            body="Confirmed.",
            reply_to="<msg-001@example.com>",
        )
        assert result is True

    @patch("Platinum.src.email_client.smtplib.SMTP")
    def test_send_failure(self, mock_smtp_cls, mock_settings_local):
        mock_smtp_cls.side_effect = smtplib.SMTPException("Auth failed")

        sender = EmailSender(mock_settings_local)
        result = sender.send(
            to="alice@example.com",
            subject="Test",
            body="Hello",
        )
        assert result is False

    def test_send_no_credentials(self, mock_settings_no_creds):
        sender = EmailSender(mock_settings_no_creds)
        result = sender.send(
            to="alice@example.com",
            subject="Test",
            body="Hello",
        )
        assert result is False

    @patch("Platinum.src.email_client.smtplib.SMTP")
    def test_send_draft(self, mock_smtp_cls, mock_settings_local):
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        sender = EmailSender(mock_settings_local)
        draft_data = {
            "to": "bob@example.com",
            "subject": "Re: Urgent",
            "body": "Done.",
        }
        result = sender.send_draft(draft_data)
        assert result is True

    @patch("Platinum.src.email_client.smtplib.SMTP")
    def test_send_with_cc(self, mock_smtp_cls, mock_settings_local):
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        sender = EmailSender(mock_settings_local)
        result = sender.send(
            to="alice@example.com",
            subject="FYI",
            body="Looping in team.",
            cc=["bob@example.com", "carol@example.com"],
        )
        assert result is True
