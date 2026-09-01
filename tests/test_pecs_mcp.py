"""Tests for the PECS MCP server.

Tests cover:
- Tool registration (tools/list returns all 4 tools)
- Tool definitions match expected schema
- JSON-RPC error handling (unknown method, parse error)
- Facade method delegation via MCP dispatch
"""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from integrations.pecs_mcp_server import (
    TOOLS,
    _build_response,
    _build_error,
    _dispatch,
    _exec_consult,
    _exec_projection,
    _exec_explain,
    _exec_health,
)
from integrations.pecs_service_facade import PECSServiceFacade


class TestMCPToolRegistration(unittest.TestCase):
    """Verify tools/list returns the expected tools."""

    def test_tool_count(self):
        """Must expose exactly 4 tools."""
        self.assertEqual(len(TOOLS), 4)

    def test_tool_names(self):
        """Tool names must match the spec."""
        names = [t["name"] for t in TOOLS]
        self.assertIn("pecs_consult", names)
        self.assertIn("pecs_projection", names)
        self.assertIn("pecs_explain", names)
        self.assertIn("pecs_health", names)

    def test_all_tools_have_input_schema(self):
        """Every tool must declare inputSchema."""
        for tool in TOOLS:
            self.assertIn("inputSchema", tool, f"Tool {tool['name']} missing inputSchema")
            self.assertIsInstance(tool["inputSchema"], dict)

    def test_consult_requires_query(self):
        """pecs_consult must have query as a required field."""
        consult = next(t for t in TOOLS if t["name"] == "pecs_consult")
        self.assertIn("query", consult["inputSchema"].get("required", []))

    def test_explain_requires_query(self):
        """pecs_explain must have query as a required field."""
        explain = next(t for t in TOOLS if t["name"] == "pecs_explain")
        self.assertIn("query", explain["inputSchema"].get("required", []))

    def test_projection_has_projection_id(self):
        """pecs_projection must accept projection_id."""
        proj = next(t for t in TOOLS if t["name"] == "pecs_projection")
        self.assertIn("projection_id", proj["inputSchema"].get("properties", {}))

    def test_health_accepts_no_args(self):
        """pecs_health must have an empty properties schema."""
        health = next(t for t in TOOLS if t["name"] == "pecs_health")
        self.assertEqual(health["inputSchema"].get("properties", {}), {})


class TestMCPJSONRPCProtocol(unittest.TestCase):
    """Verify JSON-RPC protocol handling."""

    def setUp(self):
        self.facade = MagicMock(spec=PECSServiceFacade)
        self.facade.consult.return_value = {"schema": "pecs.query.v1", "result": "ok"}
        self.facade.projection.return_value = {"schema": "pecs.projection.v1"}
        self.facade.explain.return_value = {"query": "test", "confidence": 0.5}
        self.facade.health.return_value = {"daemon_running": False}

    def test_initialize_returns_capabilities(self):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"},
        }
        response = _dispatch(request, self.facade)
        self.assertIsNotNone(response)
        self.assertIn("result", response)
        self.assertIn("capabilities", response["result"])
        self.assertIn("serverInfo", response["result"])

    def test_tools_list_returns_tools(self):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }
        response = _dispatch(request, self.facade)
        self.assertIsNotNone(response)
        self.assertIn("result", response)
        self.assertIn("tools", response["result"])
        self.assertEqual(len(response["result"]["tools"]), 4)

    def test_tools_call_consult(self):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "pecs_consult",
                "arguments": {"query": "find annotation code"},
            },
        }
        response = _dispatch(request, self.facade)
        self.assertIsNotNone(response)
        self.facade.consult.assert_called_once_with(
            query="find annotation code", profile="medium"
        )

    def test_tools_call_projection(self):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "pecs_projection",
                "arguments": {"projection_id": "proj-123"},
            },
        }
        _dispatch(request, self.facade)
        self.facade.projection.assert_called_once_with(projection_id="proj-123")

    def test_tools_call_explain(self):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "pecs_explain",
                "arguments": {"query": "test query"},
            },
        }
        _dispatch(request, self.facade)
        self.facade.explain.assert_called_once_with(query="test query")

    def test_tools_call_health(self):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "pecs_health", "arguments": {}},
        }
        _dispatch(request, self.facade)
        self.facade.health.assert_called_once()

    def test_unknown_method_returns_error(self):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "unknown_method",
            "params": {},
        }
        response = _dispatch(request, self.facade)
        self.assertIsNotNone(response)
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32601)

    def test_unknown_tool_returns_error(self):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {},
            },
        }
        response = _dispatch(request, self.facade)
        self.assertIsNotNone(response)
        self.assertIn("error", response)

    def test_notification_no_response(self):
        """JSON-RPC notifications (no id) must not produce a response."""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
        }
        response = _dispatch(request, self.facade)
        self.assertIsNone(response)

    def test_dispatch_exception_returns_error(self):
        """Exceptions during dispatch must return JSON-RPC error."""
        broken_facade = MagicMock(spec=PECSServiceFacade)
        broken_facade.consult.side_effect = RuntimeError("internal failure")

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "pecs_consult",
                "arguments": {"query": "test"},
            },
        }
        response = _dispatch(request, broken_facade)
        self.assertIsNotNone(response)
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32603)
        self.assertIn("internal failure", response["error"]["message"])


class TestMCPToolExecutors(unittest.TestCase):
    """Verify tool executors work end-to-end with a real facade."""

    def test_exec_consult_delegates(self):
        """_exec_consult must call facade.consult and return its result."""
        facade = MagicMock(spec=PECSServiceFacade)
        facade.consult.return_value = {"result": "consult_response"}

        result = _exec_consult(facade, {"query": "test", "profile": "large"})
        facade.consult.assert_called_once_with(query="test", profile="large")
        self.assertEqual(result, {"result": "consult_response"})

    def test_exec_projection_delegates(self):
        facade = MagicMock(spec=PECSServiceFacade)
        facade.projection.return_value = {"proj": "data"}

        result = _exec_projection(facade, {"projection_id": "abc"})
        facade.projection.assert_called_once_with(projection_id="abc")
        self.assertEqual(result, {"proj": "data"})

    def test_exec_explain_delegates(self):
        facade = MagicMock(spec=PECSServiceFacade)
        facade.explain.return_value = {"explanation": "done"}

        result = _exec_explain(facade, {"query": "why"})
        facade.explain.assert_called_once_with(query="why")
        self.assertEqual(result, {"explanation": "done"})

    def test_exec_health_delegates(self):
        facade = MagicMock(spec=PECSServiceFacade)
        facade.health.return_value = {"healthy": True}

        result = _exec_health(facade, {})
        facade.health.assert_called_once()
        self.assertEqual(result, {"healthy": True})


class TestMCPResponseBuilding(unittest.TestCase):
    """Verify JSON-RPC response builders."""

    def test_success_response(self):
        response = _build_response(1, result={"key": "value"})
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], 1)
        self.assertEqual(response["result"], {"key": "value"})
        self.assertNotIn("error", response)

    def test_error_response(self):
        error = _build_error(-32601, "Method not found")
        response = _build_response(1, error=error)
        self.assertEqual(response["id"], 1)
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32601)

    def test_error_with_data(self):
        error = _build_error(-32603, "Error", data={"detail": "traceback"})
        self.assertEqual(error["data"], {"detail": "traceback"})


class TestMCPToolDefinitions(unittest.TestCase):
    """Verify tool definitions match the NM-35 spec."""

    def test_consult_description_contains_primary(self):
        consult = next(t for t in TOOLS if t["name"] == "pecs_consult")
        self.assertIn("Primary", consult["description"])

    def test_explain_description_contains_diagnose(self):
        explain = next(t for t in TOOLS if t["name"] == "pecs_explain")
        self.assertIn("Diagnose", explain["description"])

    def test_health_description_contains_diagnostic(self):
        health = next(t for t in TOOLS if t["name"] == "pecs_health")
        self.assertIn("diagnostic", health["description"].lower())


if __name__ == "__main__":
    unittest.main()
