"""
Tests for OdooClient with mocked XML-RPC.
"""

import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from Platinum.src.odoo_client import OdooClient, OdooInvoiceLine


@pytest.fixture
def local_settings():
    return SimpleNamespace(
        AGENT_ROLE="local",
        ODOO_URL="http://localhost:8069",
        ODOO_DB="odoo",
        ODOO_USER="admin",
        ODOO_PASSWORD="admin",
    )


@pytest.fixture
def cloud_settings():
    return SimpleNamespace(
        AGENT_ROLE="cloud",
        ODOO_URL="http://localhost:8069",
        ODOO_DB="odoo",
        ODOO_USER="admin",
        ODOO_PASSWORD="admin",
    )


@pytest.fixture
def no_creds_settings():
    return SimpleNamespace(
        AGENT_ROLE="local",
        ODOO_URL="",
        ODOO_DB="",
        ODOO_USER="",
        ODOO_PASSWORD="",
    )


@pytest.fixture
def mock_xmlrpc():
    with patch("Platinum.src.odoo_client.xmlrpc.client.ServerProxy") as mock:
        yield mock


class TestOdooClient:

    def test_is_configured(self, local_settings, no_creds_settings):
        client = OdooClient(local_settings)
        assert client.is_configured is True

        client2 = OdooClient(no_creds_settings)
        assert client2.is_configured is False

    def test_connect_success(self, local_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(local_settings)
        assert client.connect() is True
        assert client._uid == 1

    def test_connect_failure(self, local_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = False
        mock_xmlrpc.return_value = mock_common

        client = OdooClient(local_settings)
        assert client.connect() is False

    def test_connect_no_creds(self, no_creds_settings):
        client = OdooClient(no_creds_settings)
        assert client.connect() is False

    def test_create_draft_invoice(self, local_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = 42
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(local_settings)
        client.connect()

        lines = [
            OdooInvoiceLine(product_id=1, name="Widget", quantity=2, price_unit=10.0),
        ]
        result = client.create_draft_invoice(partner_id=1, lines=lines)

        assert result["id"] == 42
        assert result["state"] == "draft"
        mock_models.execute_kw.assert_called()

    def test_create_draft_payment(self, local_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = 99
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(local_settings)
        client.connect()

        result = client.create_draft_payment(
            partner_id=1, amount=100.0, payment_type="outbound"
        )
        assert result["id"] == 99
        assert result["amount"] == 100.0

    def test_get_invoice(self, local_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = [
            {"id": 1, "name": "INV/001", "state": "draft", "amount_total": 100.0}
        ]
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(local_settings)
        client.connect()

        invoice = client.get_invoice(1)
        assert invoice["name"] == "INV/001"

    def test_get_invoice_not_found(self, local_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = []
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(local_settings)
        client.connect()

        invoice = client.get_invoice(999)
        assert invoice is None

    def test_search_partners(self, local_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_models.execute_kw.side_effect = [
            [1, 2],  # search
            [{"id": 1, "name": "Acme"}, {"id": 2, "name": "Acme Corp"}],  # read
        ]
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(local_settings)
        client.connect()

        partners = client.search_partners("Acme")
        assert len(partners) == 2

    def test_confirm_invoice_local_allowed(self, local_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = True
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(local_settings)
        client.connect()

        result = client.confirm_invoice(42)
        assert result is True

    def test_confirm_invoice_cloud_blocked(self, cloud_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(cloud_settings)
        client.connect()

        with pytest.raises(PermissionError, match="Cloud agent cannot confirm"):
            client.confirm_invoice(42)

    def test_confirm_payment_local_allowed(self, local_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = True
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(local_settings)
        client.connect()

        result = client.confirm_payment(99)
        assert result is True

    def test_confirm_payment_cloud_blocked(self, cloud_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(cloud_settings)
        client.connect()

        with pytest.raises(PermissionError, match="Cloud agent cannot confirm"):
            client.confirm_payment(99)

    def test_cancel_invoice_cloud_blocked(self, cloud_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(cloud_settings)
        client.connect()

        with pytest.raises(PermissionError, match="Cloud agent cannot cancel"):
            client.cancel_invoice(42)

    def test_list_draft_invoices(self, local_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_models.execute_kw.side_effect = [
            [1, 2],  # search
            [{"id": 1, "name": "INV/001"}, {"id": 2, "name": "INV/002"}],  # read
        ]
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(local_settings)
        client.connect()

        invoices = client.list_draft_invoices()
        assert len(invoices) == 2

    def test_list_draft_payments(self, local_settings, mock_xmlrpc):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_models.execute_kw.side_effect = [
            [1],  # search
            [{"id": 1, "name": "PAY/001", "amount": 50.0}],  # read
        ]
        mock_xmlrpc.side_effect = [mock_common, mock_models]

        client = OdooClient(local_settings)
        client.connect()

        payments = client.list_draft_payments()
        assert len(payments) == 1


class TestOdooInvoiceLine:

    def test_invoice_line_dataclass(self):
        line = OdooInvoiceLine(
            product_id=1,
            name="Test Product",
            quantity=5,
            price_unit=25.0,
        )
        assert line.product_id == 1
        assert line.quantity == 5
        assert line.price_unit == 25.0
