"""
OdooClient - Odoo Community XML-RPC Integration.

Cloud Agent: Can create draft invoices/payments (draft state only).
Local Agent: Can confirm invoices/payments (SecretGuard enforced).

Usage:
    from Platinum.src.config import get_settings
    client = OdooClient(get_settings())
    draft = client.create_draft_invoice(partner_id=1, lines=[...])
    # Local only:
    client.confirm_invoice(draft["id"])
"""

import logging
import xmlrpc.client
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger("platinum.odoo")


@dataclass
class OdooInvoiceLine:
    """Invoice line item."""
    product_id: int
    name: str
    quantity: float
    price_unit: float


class OdooClient:
    """Odoo Community XML-RPC client.

    Cloud agent can create drafts only.
    Local agent can confirm (post) invoices and payments.
    """

    def __init__(self, settings):
        self.url = settings.ODOO_URL
        self.db = settings.ODOO_DB
        self.user = settings.ODOO_USER
        self.password = settings.ODOO_PASSWORD
        self.agent_role = settings.AGENT_ROLE

        self._uid: Optional[int] = None
        self._common = None
        self._models = None

    @property
    def is_configured(self) -> bool:
        return bool(self.url and self.db and self.user and self.password)

    def connect(self) -> bool:
        """Authenticate and get user ID."""
        if not self.is_configured:
            logger.warning("Odoo credentials not configured")
            return False

        try:
            self._common = xmlrpc.client.ServerProxy(
                f"{self.url}/xmlrpc/2/common",
                allow_none=True,
            )
            self._uid = self._common.authenticate(
                self.db, self.user, self.password, {}
            )
            if not self._uid:
                logger.error("Odoo authentication failed")
                return False

            self._models = xmlrpc.client.ServerProxy(
                f"{self.url}/xmlrpc/2/object",
                allow_none=True,
            )
            logger.info(f"Connected to Odoo: {self.url} (uid={self._uid})")
            return True
        except Exception as e:
            logger.error(f"Odoo connection failed: {e}")
            return False

    def _execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute an Odoo model method."""
        if not self._uid or not self._models:
            if not self.connect():
                raise ConnectionError("Not connected to Odoo")

        return self._models.execute_kw(
            self.db, self._uid, self.password,
            model, method, list(args), kwargs
        )

    # ========== Draft Operations (Cloud + Local) ==========

    def create_draft_invoice(
        self,
        partner_id: int,
        lines: List[OdooInvoiceLine],
        move_type: str = "out_invoice",
        ref: str = "",
    ) -> Dict[str, Any]:
        """Create a draft invoice.

        Args:
            partner_id: Customer/vendor partner ID.
            lines: List of invoice line items.
            move_type: Invoice type (out_invoice, in_invoice, etc.).
            ref: Reference/memo.

        Returns:
            Dict with invoice id and name.
        """
        invoice_lines = []
        for line in lines:
            invoice_lines.append((0, 0, {
                "product_id": line.product_id,
                "name": line.name,
                "quantity": line.quantity,
                "price_unit": line.price_unit,
            }))

        vals = {
            "partner_id": partner_id,
            "move_type": move_type,
            "ref": ref,
            "invoice_line_ids": invoice_lines,
            "state": "draft",
        }

        invoice_id = self._execute("account.move", "create", vals)
        logger.info(f"Draft invoice created: id={invoice_id}")

        return {
            "id": invoice_id,
            "state": "draft",
            "partner_id": partner_id,
            "move_type": move_type,
            "created_at": datetime.utcnow().isoformat(),
        }

    def create_draft_payment(
        self,
        partner_id: int,
        amount: float,
        payment_type: str = "outbound",
        journal_id: Optional[int] = None,
        ref: str = "",
    ) -> Dict[str, Any]:
        """Create a draft payment.

        Args:
            partner_id: Customer/vendor partner ID.
            amount: Payment amount.
            payment_type: 'inbound' (receive) or 'outbound' (pay).
            journal_id: Payment journal ID (optional).
            ref: Reference/memo.

        Returns:
            Dict with payment id.
        """
        vals = {
            "partner_id": partner_id,
            "amount": amount,
            "payment_type": payment_type,
            "ref": ref,
        }
        if journal_id:
            vals["journal_id"] = journal_id

        payment_id = self._execute("account.payment", "create", vals)
        logger.info(f"Draft payment created: id={payment_id}")

        return {
            "id": payment_id,
            "state": "draft",
            "partner_id": partner_id,
            "amount": amount,
            "payment_type": payment_type,
            "created_at": datetime.utcnow().isoformat(),
        }

    def get_invoice(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Get invoice details."""
        records = self._execute(
            "account.move", "read", [invoice_id],
            {"fields": ["name", "partner_id", "state", "amount_total", "move_type"]}
        )
        return records[0] if records else None

    def get_payment(self, payment_id: int) -> Optional[Dict[str, Any]]:
        """Get payment details."""
        records = self._execute(
            "account.payment", "read", [payment_id],
            {"fields": ["name", "partner_id", "state", "amount", "payment_type"]}
        )
        return records[0] if records else None

    def search_partners(self, name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for partners by name."""
        ids = self._execute(
            "res.partner", "search",
            [("name", "ilike", name)],
            {"limit": limit}
        )
        if not ids:
            return []
        return self._execute(
            "res.partner", "read", ids,
            {"fields": ["name", "email", "phone"]}
        )

    # ========== Confirm Operations (Local Only) ==========

    def confirm_invoice(self, invoice_id: int) -> bool:
        """Confirm (post) a draft invoice. LOCAL AGENT ONLY.

        Raises:
            PermissionError: If called by Cloud agent.
        """
        if self.agent_role == "cloud":
            raise PermissionError(
                "Cloud agent cannot confirm invoices. "
                "Only Local agent has invoice confirmation authority."
            )

        try:
            self._execute("account.move", "action_post", [invoice_id])
            logger.info(f"Invoice confirmed: id={invoice_id}")
            return True
        except Exception as e:
            logger.error(f"Invoice confirmation failed: {e}")
            return False

    def confirm_payment(self, payment_id: int) -> bool:
        """Confirm (post) a draft payment. LOCAL AGENT ONLY.

        Raises:
            PermissionError: If called by Cloud agent.
        """
        if self.agent_role == "cloud":
            raise PermissionError(
                "Cloud agent cannot confirm payments. "
                "Only Local agent has payment confirmation authority."
            )

        try:
            self._execute("account.payment", "action_post", [payment_id])
            logger.info(f"Payment confirmed: id={payment_id}")
            return True
        except Exception as e:
            logger.error(f"Payment confirmation failed: {e}")
            return False

    def cancel_invoice(self, invoice_id: int) -> bool:
        """Cancel an invoice. LOCAL AGENT ONLY."""
        if self.agent_role == "cloud":
            raise PermissionError("Cloud agent cannot cancel invoices.")

        try:
            self._execute("account.move", "button_cancel", [invoice_id])
            logger.info(f"Invoice cancelled: id={invoice_id}")
            return True
        except Exception as e:
            logger.error(f"Invoice cancellation failed: {e}")
            return False

    def list_draft_invoices(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List draft invoices."""
        ids = self._execute(
            "account.move", "search",
            [("state", "=", "draft"), ("move_type", "in", ["out_invoice", "in_invoice"])],
            {"limit": limit}
        )
        if not ids:
            return []
        return self._execute(
            "account.move", "read", ids,
            {"fields": ["name", "partner_id", "state", "amount_total", "move_type", "create_date"]}
        )

    def list_draft_payments(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List draft payments."""
        ids = self._execute(
            "account.payment", "search",
            [("state", "=", "draft")],
            {"limit": limit}
        )
        if not ids:
            return []
        return self._execute(
            "account.payment", "read", ids,
            {"fields": ["name", "partner_id", "state", "amount", "payment_type", "create_date"]}
        )
