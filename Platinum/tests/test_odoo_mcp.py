"""Tests for OdooMCPServer - MCP wrapper around OdooClient."""

import json
import pytest
from unittest.mock import MagicMock, patch

from Platinum.src.odoo_mcp import OdooMCPServer, MCPToolDefinition, MCPToolResult


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.ODOO_URL = "http://localhost:8069"
    settings.ODOO_DB = "odoo"
    settings.ODOO_USER = "admin"
    settings.ODOO_PASSWORD = "admin"
    settings.AGENT_ROLE = "local"
    return settings


@pytest.fixture
def server(mock_settings):
    return OdooMCPServer(settings=mock_settings)


class TestMCPToolDefinition:
    def test_tool_definition_fields(self):
        tool = MCPToolDefinition(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object", "properties": {}},
        )
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.input_schema["type"] == "object"


class TestMCPToolResult:
    def test_empty_result(self):
        result = MCPToolResult()
        assert result.content == []
        assert result.is_error is False

    def test_add_text(self):
        result = MCPToolResult()
        result.add_text("Hello, world!")
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"
        assert result.content[0]["text"] == "Hello, world!"

    def test_to_dict(self):
        result = MCPToolResult()
        result.add_text("test")
        d = result.to_dict()
        assert "content" in d
        assert "isError" in d
        assert d["isError"] is False

    def test_error_result(self):
        result = MCPToolResult(is_error=True)
        result.add_text("Something went wrong")
        d = result.to_dict()
        assert d["isError"] is True


class TestOdooMCPServer:
    def test_list_tools(self, server):
        tools = server.list_tools()
        assert isinstance(tools, list)
        assert len(tools) == 9
        tool_names = [t["name"] for t in tools]
        assert "create_draft_invoice" in tool_names
        assert "create_draft_payment" in tool_names
        assert "get_invoice" in tool_names
        assert "get_payment" in tool_names
        assert "search_partners" in tool_names
        assert "confirm_invoice" in tool_names
        assert "confirm_payment" in tool_names
        assert "list_draft_invoices" in tool_names
        assert "list_draft_payments" in tool_names

    def test_tool_has_required_fields(self, server):
        tools = server.list_tools()
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool

    def test_unknown_tool(self, server):
        result = server.call_tool("nonexistent_tool", {})
        assert result.is_error is True
        assert "Unknown tool" in result.content[0]["text"]

    @patch("Platinum.src.odoo_mcp.OdooClient")
    def test_create_draft_invoice(self, mock_odoo_cls, mock_settings):
        mock_client = MagicMock()
        mock_client.create_draft_invoice.return_value = {
            "id": 42,
            "state": "draft",
            "partner_id": 1,
            "move_type": "out_invoice",
            "created_at": "2026-02-07T00:00:00",
        }
        mock_odoo_cls.return_value = mock_client

        server = OdooMCPServer(settings=mock_settings)
        server._client = mock_client

        result = server.call_tool("create_draft_invoice", {
            "partner_id": 1,
            "lines": [
                {"product_id": 1, "name": "Widget", "quantity": 5, "price_unit": 100.0},
            ],
        })
        assert result.is_error is False
        data = json.loads(result.content[0]["text"])
        assert data["id"] == 42
        assert data["state"] == "draft"

    @patch("Platinum.src.odoo_mcp.OdooClient")
    def test_create_draft_payment(self, mock_odoo_cls, mock_settings):
        mock_client = MagicMock()
        mock_client.create_draft_payment.return_value = {
            "id": 10,
            "state": "draft",
            "partner_id": 1,
            "amount": 500.0,
            "payment_type": "outbound",
            "created_at": "2026-02-07T00:00:00",
        }
        mock_odoo_cls.return_value = mock_client

        server = OdooMCPServer(settings=mock_settings)
        server._client = mock_client

        result = server.call_tool("create_draft_payment", {
            "partner_id": 1,
            "amount": 500.0,
        })
        assert result.is_error is False
        data = json.loads(result.content[0]["text"])
        assert data["id"] == 10
        assert data["amount"] == 500.0

    @patch("Platinum.src.odoo_mcp.OdooClient")
    def test_get_invoice(self, mock_odoo_cls, mock_settings):
        mock_client = MagicMock()
        mock_client.get_invoice.return_value = {
            "id": 42, "name": "INV/2026/001", "state": "draft",
        }
        mock_odoo_cls.return_value = mock_client

        server = OdooMCPServer(settings=mock_settings)
        server._client = mock_client

        result = server.call_tool("get_invoice", {"invoice_id": 42})
        assert result.is_error is False
        assert "INV/2026/001" in result.content[0]["text"]

    @patch("Platinum.src.odoo_mcp.OdooClient")
    def test_get_invoice_not_found(self, mock_odoo_cls, mock_settings):
        mock_client = MagicMock()
        mock_client.get_invoice.return_value = None
        mock_odoo_cls.return_value = mock_client

        server = OdooMCPServer(settings=mock_settings)
        server._client = mock_client

        result = server.call_tool("get_invoice", {"invoice_id": 999})
        assert result.is_error is False
        assert "not found" in result.content[0]["text"]

    @patch("Platinum.src.odoo_mcp.OdooClient")
    def test_search_partners(self, mock_odoo_cls, mock_settings):
        mock_client = MagicMock()
        mock_client.search_partners.return_value = [
            {"id": 1, "name": "Acme Corp", "email": "info@acme.com"},
        ]
        mock_odoo_cls.return_value = mock_client

        server = OdooMCPServer(settings=mock_settings)
        server._client = mock_client

        result = server.call_tool("search_partners", {"name": "Acme"})
        assert result.is_error is False
        data = json.loads(result.content[0]["text"])
        assert len(data) == 1
        assert data[0]["name"] == "Acme Corp"

    @patch("Platinum.src.odoo_mcp.OdooClient")
    def test_confirm_invoice_permission_denied(self, mock_odoo_cls, mock_settings):
        mock_client = MagicMock()
        mock_client.confirm_invoice.side_effect = PermissionError(
            "Cloud agent cannot confirm invoices."
        )
        mock_odoo_cls.return_value = mock_client

        server = OdooMCPServer(settings=mock_settings)
        server._client = mock_client

        result = server.call_tool("confirm_invoice", {"invoice_id": 42})
        assert result.is_error is True
        assert "Permission denied" in result.content[0]["text"]

    @patch("Platinum.src.odoo_mcp.OdooClient")
    def test_confirm_invoice_success(self, mock_odoo_cls, mock_settings):
        mock_client = MagicMock()
        mock_client.confirm_invoice.return_value = True
        mock_odoo_cls.return_value = mock_client

        server = OdooMCPServer(settings=mock_settings)
        server._client = mock_client

        result = server.call_tool("confirm_invoice", {"invoice_id": 42})
        assert result.is_error is False
        assert "confirmed: True" in result.content[0]["text"]

    @patch("Platinum.src.odoo_mcp.OdooClient")
    def test_connection_error(self, mock_odoo_cls, mock_settings):
        mock_client = MagicMock()
        mock_client.create_draft_invoice.side_effect = ConnectionError("Not connected")
        mock_odoo_cls.return_value = mock_client

        server = OdooMCPServer(settings=mock_settings)
        server._client = mock_client

        result = server.call_tool("create_draft_invoice", {
            "partner_id": 1, "lines": [],
        })
        assert result.is_error is True
        assert "Connection error" in result.content[0]["text"]

    @patch("Platinum.src.odoo_mcp.OdooClient")
    def test_list_draft_invoices(self, mock_odoo_cls, mock_settings):
        mock_client = MagicMock()
        mock_client.list_draft_invoices.return_value = [
            {"id": 1, "name": "INV/001", "state": "draft"},
        ]
        mock_odoo_cls.return_value = mock_client

        server = OdooMCPServer(settings=mock_settings)
        server._client = mock_client

        result = server.call_tool("list_draft_invoices", {})
        assert result.is_error is False
        data = json.loads(result.content[0]["text"])
        assert len(data) == 1

    @patch("Platinum.src.odoo_mcp.OdooClient")
    def test_list_draft_payments(self, mock_odoo_cls, mock_settings):
        mock_client = MagicMock()
        mock_client.list_draft_payments.return_value = []
        mock_odoo_cls.return_value = mock_client

        server = OdooMCPServer(settings=mock_settings)
        server._client = mock_client

        result = server.call_tool("list_draft_payments", {"limit": 5})
        assert result.is_error is False
        data = json.loads(result.content[0]["text"])
        assert data == []
