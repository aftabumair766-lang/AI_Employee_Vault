"""
Odoo MCP Wrapper - MCP-compatible tool interface for OdooClient.

Satisfies CONSTITUTION.md Section 10.5.2:
  "Cloud Agent integrates with Odoo via MCP"

This module wraps the existing OdooClient XML-RPC methods as MCP-compatible
tool definitions. Each tool has a name, description, input schema, and
an execute method that delegates to OdooClient.

Usage:
    from Platinum.src.odoo_mcp import OdooMCPServer
    server = OdooMCPServer(settings)
    tools = server.list_tools()
    result = server.call_tool("create_draft_invoice", {...})
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from Platinum.src.odoo_client import OdooClient, OdooInvoiceLine

logger = logging.getLogger("platinum.odoo_mcp")


@dataclass
class MCPToolDefinition:
    """MCP-compatible tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class MCPToolResult:
    """MCP-compatible tool result."""
    content: List[Dict[str, Any]] = field(default_factory=list)
    is_error: bool = False

    def add_text(self, text: str):
        self.content.append({"type": "text", "text": text})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "isError": self.is_error,
        }


class OdooMCPServer:
    """MCP server wrapper for Odoo operations.

    Exposes OdooClient methods as MCP-compatible tools that can be
    invoked by AI agents using the standard MCP tool-call protocol.
    """

    def __init__(self, settings=None):
        self._client: Optional[OdooClient] = None
        self._settings = settings
        self._tools = self._register_tools()

    def _get_client(self) -> OdooClient:
        if self._client is None:
            if self._settings is None:
                from Platinum.src.config import get_settings
                self._settings = get_settings()
            self._client = OdooClient(self._settings)
        return self._client

    def _register_tools(self) -> Dict[str, MCPToolDefinition]:
        """Register all available MCP tools."""
        tools = {}

        tools["create_draft_invoice"] = MCPToolDefinition(
            name="create_draft_invoice",
            description="Create a draft invoice in Odoo. Cloud Agent: draft-only. "
                        "Local approval REQUIRED before posting.",
            input_schema={
                "type": "object",
                "properties": {
                    "partner_id": {
                        "type": "integer",
                        "description": "Customer/vendor partner ID in Odoo",
                    },
                    "lines": {
                        "type": "array",
                        "description": "Invoice line items",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "integer"},
                                "name": {"type": "string"},
                                "quantity": {"type": "number"},
                                "price_unit": {"type": "number"},
                            },
                            "required": ["product_id", "name", "quantity", "price_unit"],
                        },
                    },
                    "move_type": {
                        "type": "string",
                        "description": "Invoice type (out_invoice or in_invoice)",
                        "default": "out_invoice",
                    },
                    "ref": {
                        "type": "string",
                        "description": "Reference/memo for the invoice",
                        "default": "",
                    },
                },
                "required": ["partner_id", "lines"],
            },
        )

        tools["create_draft_payment"] = MCPToolDefinition(
            name="create_draft_payment",
            description="Create a draft payment in Odoo. Cloud Agent: draft-only. "
                        "Local approval REQUIRED before posting.",
            input_schema={
                "type": "object",
                "properties": {
                    "partner_id": {
                        "type": "integer",
                        "description": "Customer/vendor partner ID in Odoo",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Payment amount",
                    },
                    "payment_type": {
                        "type": "string",
                        "description": "'inbound' (receive) or 'outbound' (pay)",
                        "default": "outbound",
                    },
                    "journal_id": {
                        "type": "integer",
                        "description": "Payment journal ID (optional)",
                    },
                    "ref": {
                        "type": "string",
                        "description": "Reference/memo",
                        "default": "",
                    },
                },
                "required": ["partner_id", "amount"],
            },
        )

        tools["get_invoice"] = MCPToolDefinition(
            name="get_invoice",
            description="Get invoice details from Odoo by ID.",
            input_schema={
                "type": "object",
                "properties": {
                    "invoice_id": {
                        "type": "integer",
                        "description": "Invoice ID to look up",
                    },
                },
                "required": ["invoice_id"],
            },
        )

        tools["get_payment"] = MCPToolDefinition(
            name="get_payment",
            description="Get payment details from Odoo by ID.",
            input_schema={
                "type": "object",
                "properties": {
                    "payment_id": {
                        "type": "integer",
                        "description": "Payment ID to look up",
                    },
                },
                "required": ["payment_id"],
            },
        )

        tools["search_partners"] = MCPToolDefinition(
            name="search_partners",
            description="Search for partners (customers/vendors) in Odoo by name.",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Partner name to search for",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results to return",
                        "default": 10,
                    },
                },
                "required": ["name"],
            },
        )

        tools["confirm_invoice"] = MCPToolDefinition(
            name="confirm_invoice",
            description="Confirm (post) a draft invoice. LOCAL AGENT ONLY. "
                        "Cloud Agent will receive PermissionError.",
            input_schema={
                "type": "object",
                "properties": {
                    "invoice_id": {
                        "type": "integer",
                        "description": "Invoice ID to confirm",
                    },
                },
                "required": ["invoice_id"],
            },
        )

        tools["confirm_payment"] = MCPToolDefinition(
            name="confirm_payment",
            description="Confirm (post) a draft payment. LOCAL AGENT ONLY. "
                        "Cloud Agent will receive PermissionError.",
            input_schema={
                "type": "object",
                "properties": {
                    "payment_id": {
                        "type": "integer",
                        "description": "Payment ID to confirm",
                    },
                },
                "required": ["payment_id"],
            },
        )

        tools["list_draft_invoices"] = MCPToolDefinition(
            name="list_draft_invoices",
            description="List all draft invoices in Odoo.",
            input_schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max results to return",
                        "default": 20,
                    },
                },
            },
        )

        tools["list_draft_payments"] = MCPToolDefinition(
            name="list_draft_payments",
            description="List all draft payments in Odoo.",
            input_schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max results to return",
                        "default": 20,
                    },
                },
            },
        )

        return tools

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return MCP-compatible tool listing."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema,
            }
            for tool in self._tools.values()
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Execute an MCP tool call.

        Args:
            name: Tool name (must match a registered tool).
            arguments: Tool arguments matching the input schema.

        Returns:
            MCPToolResult with content and error status.
        """
        result = MCPToolResult()

        if name not in self._tools:
            result.is_error = True
            result.add_text(f"Unknown tool: {name}. Available: {list(self._tools.keys())}")
            return result

        client = self._get_client()

        try:
            if name == "create_draft_invoice":
                lines = [
                    OdooInvoiceLine(
                        product_id=line["product_id"],
                        name=line["name"],
                        quantity=line["quantity"],
                        price_unit=line["price_unit"],
                    )
                    for line in arguments.get("lines", [])
                ]
                invoice = client.create_draft_invoice(
                    partner_id=arguments["partner_id"],
                    lines=lines,
                    move_type=arguments.get("move_type", "out_invoice"),
                    ref=arguments.get("ref", ""),
                )
                result.add_text(json.dumps(invoice, indent=2))

            elif name == "create_draft_payment":
                payment = client.create_draft_payment(
                    partner_id=arguments["partner_id"],
                    amount=arguments["amount"],
                    payment_type=arguments.get("payment_type", "outbound"),
                    journal_id=arguments.get("journal_id"),
                    ref=arguments.get("ref", ""),
                )
                result.add_text(json.dumps(payment, indent=2))

            elif name == "get_invoice":
                invoice = client.get_invoice(arguments["invoice_id"])
                result.add_text(json.dumps(invoice, indent=2) if invoice else "Invoice not found")

            elif name == "get_payment":
                payment = client.get_payment(arguments["payment_id"])
                result.add_text(json.dumps(payment, indent=2) if payment else "Payment not found")

            elif name == "search_partners":
                partners = client.search_partners(
                    name=arguments["name"],
                    limit=arguments.get("limit", 10),
                )
                result.add_text(json.dumps(partners, indent=2))

            elif name == "confirm_invoice":
                success = client.confirm_invoice(arguments["invoice_id"])
                result.add_text(f"Invoice confirmed: {success}")

            elif name == "confirm_payment":
                success = client.confirm_payment(arguments["payment_id"])
                result.add_text(f"Payment confirmed: {success}")

            elif name == "list_draft_invoices":
                invoices = client.list_draft_invoices(
                    limit=arguments.get("limit", 20),
                )
                result.add_text(json.dumps(invoices, indent=2))

            elif name == "list_draft_payments":
                payments = client.list_draft_payments(
                    limit=arguments.get("limit", 20),
                )
                result.add_text(json.dumps(payments, indent=2))

            logger.info(f"MCP tool '{name}' executed successfully")

        except PermissionError as e:
            result.is_error = True
            result.add_text(f"Permission denied: {e}")
            logger.warning(f"MCP tool '{name}' permission denied: {e}")

        except ConnectionError as e:
            result.is_error = True
            result.add_text(f"Connection error: {e}")
            logger.error(f"MCP tool '{name}' connection error: {e}")

        except Exception as e:
            result.is_error = True
            result.add_text(f"Error executing {name}: {e}")
            logger.error(f"MCP tool '{name}' failed: {e}")

        return result
