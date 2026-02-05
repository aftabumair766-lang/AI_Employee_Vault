"""
A2A Interface - Agent-to-Agent Communication (Section 10.7).

Defines the interface for Phase 2 agent communication.
Provides FileBasedTransport as a reference implementation.

Usage:
    transport = FileBasedTransport("/path/to/vault")
    msg = A2AMessage(sender="cloud", recipient="local", payload={"action": "request_approval"})
    transport.send(msg)
    messages = transport.receive("local")
"""

import json
import uuid
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger("platinum.a2a")


@dataclass
class A2AMessage:
    """Agent-to-Agent message."""
    sender: str
    recipient: str
    payload: Dict[str, Any]
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    message_type: str = "request"  # request, response, notification
    correlation_id: Optional[str] = None  # For request/response pairing
    ttl_seconds: int = 3600  # Time-to-live

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "message_type": self.message_type,
            "correlation_id": self.correlation_id,
            "ttl_seconds": self.ttl_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "A2AMessage":
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            sender=data["sender"],
            recipient=data["recipient"],
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            message_type=data.get("message_type", "request"),
            correlation_id=data.get("correlation_id"),
            ttl_seconds=data.get("ttl_seconds", 3600),
        )

    def is_expired(self) -> bool:
        """Check if message has exceeded TTL."""
        try:
            created = datetime.fromisoformat(self.timestamp)
            age = (datetime.utcnow() - created).total_seconds()
            return age > self.ttl_seconds
        except ValueError:
            return False


class A2ATransport(ABC):
    """Abstract base class for A2A message transport.

    Implementations may use:
    - File-based (current: Platinum/Signals/)
    - Redis pub/sub
    - HTTP webhooks
    - Message queue (RabbitMQ, etc.)
    """

    @abstractmethod
    def send(self, message: A2AMessage) -> bool:
        """Send a message to another agent.

        Args:
            message: A2AMessage to send.

        Returns:
            True if sent successfully.
        """
        ...

    @abstractmethod
    def receive(self, agent_name: str, limit: int = 10) -> List[A2AMessage]:
        """Receive messages for an agent.

        Args:
            agent_name: Name of the receiving agent.
            limit: Maximum messages to return.

        Returns:
            List of A2AMessage objects.
        """
        ...

    @abstractmethod
    def acknowledge(self, message_id: str) -> bool:
        """Acknowledge (delete) a processed message.

        Args:
            message_id: ID of message to acknowledge.

        Returns:
            True if acknowledged.
        """
        ...

    @abstractmethod
    def get_pending_count(self, agent_name: str) -> int:
        """Get count of pending messages for an agent."""
        ...


class FileBasedTransport(A2ATransport):
    """File-based A2A transport using Platinum/Signals/ directory.

    Messages are stored as JSON files:
    - Platinum/Signals/{recipient}/MSG-{message_id}.json

    This is a simple, vault-compatible transport that works
    with git sync for cross-machine communication.
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.signals_dir = self.vault_path / "Platinum" / "Signals"
        self.signals_dir.mkdir(parents=True, exist_ok=True)

    def _agent_inbox(self, agent_name: str) -> Path:
        inbox = self.signals_dir / agent_name
        inbox.mkdir(parents=True, exist_ok=True)
        return inbox

    def send(self, message: A2AMessage) -> bool:
        """Send message by writing to recipient's inbox."""
        try:
            inbox = self._agent_inbox(message.recipient)
            msg_file = inbox / f"MSG-{message.message_id}.json"
            msg_file.write_text(
                json.dumps(message.to_dict(), indent=2),
                encoding="utf-8"
            )
            logger.info(
                f"A2A message sent: {message.sender} -> {message.recipient} "
                f"({message.message_type})"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send A2A message: {e}")
            return False

    def receive(self, agent_name: str, limit: int = 10) -> List[A2AMessage]:
        """Receive messages from agent's inbox."""
        inbox = self._agent_inbox(agent_name)
        messages = []

        for msg_file in sorted(inbox.glob("MSG-*.json"))[:limit]:
            try:
                data = json.loads(msg_file.read_text(encoding="utf-8"))
                msg = A2AMessage.from_dict(data)

                # Skip expired messages
                if msg.is_expired():
                    msg_file.unlink()
                    logger.debug(f"Expired message deleted: {msg.message_id}")
                    continue

                messages.append(msg)
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Invalid message file {msg_file}: {e}")

        return messages

    def acknowledge(self, message_id: str) -> bool:
        """Delete a processed message file."""
        # Search all inboxes
        for inbox in self.signals_dir.iterdir():
            if inbox.is_dir():
                msg_file = inbox / f"MSG-{message_id}.json"
                if msg_file.exists():
                    msg_file.unlink()
                    logger.debug(f"Message acknowledged: {message_id}")
                    return True
        return False

    def get_pending_count(self, agent_name: str) -> int:
        """Count pending messages in agent's inbox."""
        inbox = self._agent_inbox(agent_name)
        return len(list(inbox.glob("MSG-*.json")))

    def cleanup_expired(self) -> int:
        """Remove all expired messages. Returns count deleted."""
        deleted = 0
        for inbox in self.signals_dir.iterdir():
            if inbox.is_dir():
                for msg_file in inbox.glob("MSG-*.json"):
                    try:
                        data = json.loads(msg_file.read_text(encoding="utf-8"))
                        msg = A2AMessage.from_dict(data)
                        if msg.is_expired():
                            msg_file.unlink()
                            deleted += 1
                    except Exception:
                        pass
        return deleted

    def send_request(
        self,
        sender: str,
        recipient: str,
        action: str,
        data: Optional[dict] = None,
    ) -> A2AMessage:
        """Helper: Send a request message."""
        msg = A2AMessage(
            sender=sender,
            recipient=recipient,
            message_type="request",
            payload={"action": action, "data": data or {}},
        )
        self.send(msg)
        return msg

    def send_response(
        self,
        sender: str,
        recipient: str,
        correlation_id: str,
        status: str,
        data: Optional[dict] = None,
    ) -> A2AMessage:
        """Helper: Send a response message."""
        msg = A2AMessage(
            sender=sender,
            recipient=recipient,
            message_type="response",
            correlation_id=correlation_id,
            payload={"status": status, "data": data or {}},
        )
        self.send(msg)
        return msg

    def send_notification(
        self,
        sender: str,
        recipient: str,
        event: str,
        data: Optional[dict] = None,
    ) -> A2AMessage:
        """Helper: Send a notification message."""
        msg = A2AMessage(
            sender=sender,
            recipient=recipient,
            message_type="notification",
            payload={"event": event, "data": data or {}},
        )
        self.send(msg)
        return msg
