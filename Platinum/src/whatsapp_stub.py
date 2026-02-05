"""
WhatsApp Integration Stub - ABC interface + stub implementation.

Local agent ONLY. SecretGuard enforced.
Phase 2: Replace stub with real WhatsApp Business API integration.

Usage:
    client = WhatsAppStub(settings)
    client.send_message(to="+1234567890", body="Hello!")
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("platinum.whatsapp")


@dataclass
class WhatsAppMessage:
    """WhatsApp message data."""
    to: str
    body: str
    message_type: str = "text"  # text, image, document
    media_url: Optional[str] = None
    timestamp: str = ""
    status: str = "pending"  # pending, sent, delivered, read, failed


class WhatsAppBase(ABC):
    """Abstract base class for WhatsApp integration.

    Implementors must provide send_message and get_messages.
    """

    @abstractmethod
    def send_message(self, to: str, body: str,
                     message_type: str = "text",
                     media_url: Optional[str] = None) -> WhatsAppMessage:
        """Send a WhatsApp message.

        Args:
            to: Recipient phone number (E.164 format).
            body: Message body text.
            message_type: Type of message (text, image, document).
            media_url: URL to media file (for image/document types).

        Returns:
            WhatsAppMessage with status.
        """
        ...

    @abstractmethod
    def get_messages(self, limit: int = 20) -> List[WhatsAppMessage]:
        """Retrieve recent incoming messages.

        Args:
            limit: Maximum number of messages to return.

        Returns:
            List of WhatsAppMessage objects.
        """
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the WhatsApp connection is active."""
        ...


class WhatsAppStub(WhatsAppBase):
    """Stub implementation of WhatsApp integration.

    Local agent ONLY. Logs actions but does not send real messages.
    Replace with real implementation when WhatsApp Business API is configured.
    """

    def __init__(self, settings):
        self.api_url = settings.WHATSAPP_API_URL
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.agent_role = settings.AGENT_ROLE

        if self.agent_role == "cloud":
            raise PermissionError(
                "Cloud agent is not permitted to access WhatsApp. "
                "Only the Local agent has WhatsApp authority."
            )

        self._sent_messages: List[WhatsAppMessage] = []
        self._connected = False

    def send_message(self, to: str, body: str,
                     message_type: str = "text",
                     media_url: Optional[str] = None) -> WhatsAppMessage:
        """Stub: log message but don't actually send."""
        msg = WhatsAppMessage(
            to=to,
            body=body,
            message_type=message_type,
            media_url=media_url,
            timestamp=datetime.utcnow().isoformat(),
            status="stub_logged",
        )
        self._sent_messages.append(msg)
        logger.info(f"[STUB] WhatsApp message to {to}: {body[:50]}...")
        return msg

    def get_messages(self, limit: int = 20) -> List[WhatsAppMessage]:
        """Stub: return previously sent messages for testing."""
        return self._sent_messages[-limit:]

    def is_connected(self) -> bool:
        """Stub: always returns False until real API is configured."""
        return bool(self.api_url and self.api_token)

    def get_sent_count(self) -> int:
        """Return number of stub-logged messages."""
        return len(self._sent_messages)
