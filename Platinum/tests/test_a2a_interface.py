"""
Tests for A2A Interface.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta

from Platinum.src.a2a_interface import (
    A2AMessage, A2ATransport, FileBasedTransport
)


@pytest.fixture
def transport(tmp_path):
    return FileBasedTransport(str(tmp_path))


class TestA2AMessage:

    def test_create_message(self):
        msg = A2AMessage(
            sender="cloud",
            recipient="local",
            payload={"action": "approve"},
        )
        assert msg.sender == "cloud"
        assert msg.recipient == "local"
        assert msg.message_type == "request"
        assert "action" in msg.payload

    def test_to_dict(self):
        msg = A2AMessage(
            sender="cloud",
            recipient="local",
            payload={"data": 123},
        )
        d = msg.to_dict()
        assert d["sender"] == "cloud"
        assert d["recipient"] == "local"
        assert d["payload"]["data"] == 123

    def test_from_dict(self):
        data = {
            "message_id": "abc123",
            "sender": "local",
            "recipient": "cloud",
            "payload": {"status": "ok"},
            "message_type": "response",
        }
        msg = A2AMessage.from_dict(data)
        assert msg.message_id == "abc123"
        assert msg.sender == "local"
        assert msg.message_type == "response"

    def test_is_expired_not_expired(self):
        msg = A2AMessage(
            sender="a", recipient="b", payload={},
            ttl_seconds=3600,
        )
        assert msg.is_expired() is False

    def test_is_expired_true(self):
        old_time = (datetime.utcnow() - timedelta(hours=2)).isoformat()
        msg = A2AMessage(
            sender="a", recipient="b", payload={},
            timestamp=old_time,
            ttl_seconds=3600,
        )
        assert msg.is_expired() is True

    def test_correlation_id(self):
        msg = A2AMessage(
            sender="a", recipient="b", payload={},
            correlation_id="req-001",
        )
        assert msg.correlation_id == "req-001"


class TestFileBasedTransport:

    def test_send_creates_file(self, transport, tmp_path):
        msg = A2AMessage(
            sender="cloud",
            recipient="local",
            payload={"test": True},
        )
        result = transport.send(msg)
        assert result is True

        inbox = tmp_path / "Platinum" / "Signals" / "local"
        files = list(inbox.glob("MSG-*.json"))
        assert len(files) == 1

    def test_receive_returns_messages(self, transport):
        msg = A2AMessage(
            sender="cloud",
            recipient="local",
            payload={"data": "hello"},
        )
        transport.send(msg)

        messages = transport.receive("local")
        assert len(messages) == 1
        assert messages[0].payload["data"] == "hello"

    def test_receive_empty_inbox(self, transport):
        messages = transport.receive("nonexistent")
        assert messages == []

    def test_acknowledge_removes_file(self, transport, tmp_path):
        msg = A2AMessage(
            sender="a", recipient="b", payload={},
        )
        transport.send(msg)

        inbox = tmp_path / "Platinum" / "Signals" / "b"
        assert len(list(inbox.glob("MSG-*.json"))) == 1

        result = transport.acknowledge(msg.message_id)
        assert result is True
        assert len(list(inbox.glob("MSG-*.json"))) == 0

    def test_acknowledge_nonexistent(self, transport):
        result = transport.acknowledge("fake-id")
        assert result is False

    def test_get_pending_count(self, transport):
        assert transport.get_pending_count("agent1") == 0

        transport.send(A2AMessage(sender="x", recipient="agent1", payload={}))
        transport.send(A2AMessage(sender="y", recipient="agent1", payload={}))

        assert transport.get_pending_count("agent1") == 2

    def test_cleanup_expired(self, transport, tmp_path):
        # Send an expired message
        old_msg = A2AMessage(
            sender="a", recipient="b", payload={},
            timestamp=(datetime.utcnow() - timedelta(hours=10)).isoformat(),
            ttl_seconds=3600,
        )
        transport.send(old_msg)

        # Send a fresh message
        fresh_msg = A2AMessage(
            sender="a", recipient="b", payload={},
        )
        transport.send(fresh_msg)

        deleted = transport.cleanup_expired()
        assert deleted == 1
        assert transport.get_pending_count("b") == 1

    def test_send_request_helper(self, transport):
        msg = transport.send_request(
            sender="cloud",
            recipient="local",
            action="approve_draft",
            data={"draft_id": "DRAFT-001"},
        )
        assert msg.message_type == "request"
        assert msg.payload["action"] == "approve_draft"

    def test_send_response_helper(self, transport):
        msg = transport.send_response(
            sender="local",
            recipient="cloud",
            correlation_id="req-001",
            status="approved",
            data={"result": True},
        )
        assert msg.message_type == "response"
        assert msg.correlation_id == "req-001"
        assert msg.payload["status"] == "approved"

    def test_send_notification_helper(self, transport):
        msg = transport.send_notification(
            sender="monitor",
            recipient="local",
            event="health_alert",
            data={"service": "api"},
        )
        assert msg.message_type == "notification"
        assert msg.payload["event"] == "health_alert"

    def test_receive_skips_expired(self, transport):
        # Send an expired message
        old_msg = A2AMessage(
            sender="a", recipient="test",
            payload={"old": True},
            timestamp=(datetime.utcnow() - timedelta(hours=5)).isoformat(),
            ttl_seconds=3600,
        )
        transport.send(old_msg)

        messages = transport.receive("test")
        assert len(messages) == 0
