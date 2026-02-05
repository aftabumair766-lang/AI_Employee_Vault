"""
Banking Integration Stub - ABC interface + stub implementation.

Local agent ONLY. SecretGuard enforced.
Phase 2: Replace stub with real banking API integration.

Usage:
    client = BankingStub(settings)
    result = client.initiate_payment(amount=100.00, currency="USD", to="vendor")
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("platinum.banking")


@dataclass
class PaymentRecord:
    """Payment transaction record."""
    payment_id: str
    amount: float
    currency: str
    recipient: str
    description: str = ""
    status: str = "pending"  # pending, approved, completed, failed, stub_logged
    timestamp: str = ""
    reference: Optional[str] = None


@dataclass
class AccountBalance:
    """Account balance snapshot."""
    account_id: str
    balance: float
    currency: str
    as_of: str = ""


class BankingBase(ABC):
    """Abstract base class for banking integration.

    Implementors must provide payment initiation, status check, and balance query.
    """

    @abstractmethod
    def initiate_payment(self, amount: float, currency: str,
                         recipient: str, description: str = "") -> PaymentRecord:
        """Initiate a payment transaction.

        Args:
            amount: Payment amount.
            currency: Currency code (e.g., USD, EUR).
            recipient: Recipient identifier.
            description: Payment description/memo.

        Returns:
            PaymentRecord with transaction details.
        """
        ...

    @abstractmethod
    def get_payment_status(self, payment_id: str) -> Optional[PaymentRecord]:
        """Get the status of a payment transaction.

        Args:
            payment_id: Payment transaction ID.

        Returns:
            PaymentRecord if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_balance(self, account_id: str = "default") -> Optional[AccountBalance]:
        """Get account balance.

        Args:
            account_id: Account identifier.

        Returns:
            AccountBalance if available.
        """
        ...

    @abstractmethod
    def list_recent_transactions(self, limit: int = 20) -> List[PaymentRecord]:
        """List recent payment transactions."""
        ...


class BankingStub(BankingBase):
    """Stub implementation of banking integration.

    Local agent ONLY. Logs actions but does not execute real payments.
    Replace with real implementation when banking API is configured.
    """

    def __init__(self, settings):
        self.api_url = settings.BANKING_API_URL
        self.api_key = settings.BANKING_API_KEY
        self.agent_role = settings.AGENT_ROLE

        if self.agent_role == "cloud":
            raise PermissionError(
                "Cloud agent is not permitted to access banking. "
                "Only the Local agent has banking authority."
            )

        self._payments: List[PaymentRecord] = []
        self._payment_counter = 0

    def initiate_payment(self, amount: float, currency: str,
                         recipient: str, description: str = "") -> PaymentRecord:
        """Stub: log payment but don't actually transfer funds."""
        self._payment_counter += 1
        payment = PaymentRecord(
            payment_id=f"STUB-PAY-{self._payment_counter:04d}",
            amount=amount,
            currency=currency,
            recipient=recipient,
            description=description,
            status="stub_logged",
            timestamp=datetime.utcnow().isoformat(),
        )
        self._payments.append(payment)
        logger.info(
            f"[STUB] Payment initiated: {amount} {currency} to {recipient}"
        )
        return payment

    def get_payment_status(self, payment_id: str) -> Optional[PaymentRecord]:
        """Stub: look up payment in local records."""
        for p in self._payments:
            if p.payment_id == payment_id:
                return p
        return None

    def get_balance(self, account_id: str = "default") -> Optional[AccountBalance]:
        """Stub: return a placeholder balance."""
        return AccountBalance(
            account_id=account_id,
            balance=0.0,
            currency="USD",
            as_of=datetime.utcnow().isoformat(),
        )

    def list_recent_transactions(self, limit: int = 20) -> List[PaymentRecord]:
        """Stub: return previously logged payments."""
        return self._payments[-limit:]

    def is_connected(self) -> bool:
        """Stub: check if API credentials are configured."""
        return bool(self.api_url and self.api_key)

    def get_payment_count(self) -> int:
        """Return number of stub-logged payments."""
        return len(self._payments)
