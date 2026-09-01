"""PECS MCP Server — Model Context Protocol adapter for PECS.

This is a minimal, experimental MCP server that exposes existing PECS
functionality through four tools. It is ONLY a transport adapter — no
engineering logic, projection logic, or query interpretation lives here.

Protocol: JSON-RPC 2.0 over stdio (MCP).
"""

from __future__ import annotations

import json
import logging
import sys
import traceback
from typing import Any, Dict

from integrations.pecs_service_facade import PECSServiceFacade

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# MCP Protocol constants
# ---------------------------------------------------------------------------

JSONRPC_VERSION = "2.0"
SERVER_INFO = {
    "name": "pecs-mcp",
    "version": "1.0.0-alpha1",
}
CAPABILITIES = {
    "tools": {},
}

# ---------------------------------------------------------------------------
# Tool definitions (MCP tool descriptor list)
# ---------------------------------------------------------------------------

TOOLS: list[Dict[str, Any]] = [
    {
        "name": "pecs_consult",
        "description": (
            "Primary PECS engineering consultation. Returns deterministic "
            "engineering evidence for a free-text query: locality, projected "
            "files, authority, confidence, and related workspace information."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Free-text engineering query (e.g. 'find the annotation rendering code')",
                },
                "profile": {
                    "type": "string",
                    "enum": ["small", "medium", "large"],
                    "description": "Projection profile (default: medium)",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "pecs_projection",
        "description": (
            "Retrieve the detailed projection associated with the current or "
            "previous consult result."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "projection_id": {
                    "type": "string",
                    "description": "Optional projection id from a previous consult result",
                },
            },
        },
    },
    {
        "name": "pecs_explain",
        "description": (
            "Diagnose why PECS returns specific results for a query. Returns "
            "parsing, locality, and topology match analysis."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query to explain",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "pecs_health",
        "description": (
            "PECS diagnostic information: daemon status, workspace "
            "indexed state, version, continuity and graph availability."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]

# ---------------------------------------------------------------------------
# Request handlers
# ---------------------------------------------------------------------------


def _handle_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    protocol_version = params.get("protocolVersion", "2024-11-05")
    return {
        "protocolVersion": protocol_version,
        "capabilities": CAPABILITIES,
        "serverInfo": SERVER_INFO,
    }


def _handle_tools_list(params: Dict[str, Any]) -> Dict[str, Any]:
    return {"tools": TOOLS}


def _handle_tools_call(
    params: Dict[str, Any], facade: PECSServiceFacade
) -> Dict[str, Any]:
    name = params.get("name", "")
    arguments = params.get("arguments", {}) or {}
    workspace_root = arguments.pop("workspace_root", None)

    # Allow per-request workspace override, fall back to facade default
    local_facade = (
        PECSServiceFacade(workspace_root=workspace_root)
        if workspace_root
        else facade
    )

    tool_map = {
        "pecs_consult": _exec_consult,
        "pecs_projection": _exec_projection,
        "pecs_explain": _exec_explain,
        "pecs_health": _exec_health,
    }

    executor = tool_map.get(name)
    if executor is None:
        raise ValueError(f"Unknown tool: {name}")

    result = executor(local_facade, arguments)
    return result


def _exec_consult(facade: PECSServiceFacade, args: Dict[str, Any]) -> Dict[str, Any]:
    query = args.get("query", "")
    profile = args.get("profile", "medium")
    return facade.consult(query=query, profile=profile)


def _exec_projection(
    facade: PECSServiceFacade, args: Dict[str, Any]
) -> Dict[str, Any]:
    projection_id = args.get("projection_id", "")
    return facade.projection(projection_id=projection_id)


def _exec_explain(facade: PECSServiceFacade, args: Dict[str, Any]) -> Dict[str, Any]:
    query = args.get("query", "")
    return facade.explain(query=query)


def _exec_health(facade: PECSServiceFacade, args: Dict[str, Any]) -> Dict[str, Any]:
    return facade.health()


# ---------------------------------------------------------------------------
# JSON-RPC dispatcher
# ---------------------------------------------------------------------------


def _build_response(
    request_id: Any, result: Any = None, error: Any = None
) -> Dict[str, Any]:
    response: Dict[str, Any] = {
        "jsonrpc": JSONRPC_VERSION,
        "id": request_id,
    }
    if error is not None:
        response["error"] = error
    else:
        response["result"] = result
    return response


def _build_error(
    code: int, message: str, data: Any = None
) -> Dict[str, Any]:
    err: Dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return err


def _dispatch(
    request: Dict[str, Any], facade: PECSServiceFacade
) -> Dict[str, Any] | None:
    method = request.get("method", "")
    request_id = request.get("id")
    params = request.get("params", {}) or {}

    # Notifications (no id) are not responded to
    if request_id is None:
        return None

    try:
        if method == "initialize":
            result = _handle_initialize(params)
        elif method == "tools/list":
            result = _handle_tools_list(params)
        elif method == "tools/call":
            result = _handle_tools_call(params, facade)
        elif method in ("resources/list", "resources/read", "prompts/list", "prompts/get"):
            # Return empty defaults for un-implemented methods
            result = {}
        else:
            return _build_response(
                request_id,
                error=_build_error(-32601, f"Method not found: {method}"),
            )

        return _build_response(request_id, result=result)

    except Exception as exc:
        logger.error("Error handling %s: %s", method, exc, exc_info=True)
        return _build_response(
            request_id,
            error=_build_error(-32603, str(exc), traceback.format_exc()),
        )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server over stdio."""
    workspace_root = None
    if len(sys.argv) > 1:
        workspace_root = sys.argv[1]

    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    facade = PECSServiceFacade(workspace_root=workspace_root)

    # Send the initial endpoint info (required by some MCP clients)
    initial_info = {
        "jsonrpc": JSONRPC_VERSION,
        "method": "initialized",
        "params": {
            "capabilities": CAPABILITIES,
            "serverInfo": SERVER_INFO,
        },
    }
    sys.stdout.write(json.dumps(initial_info) + "\n")
    sys.stdout.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            response = _build_response(
                None,
                error=_build_error(-32700, f"Parse error: {exc}"),
            )
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            continue

        response = _dispatch(request, facade)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
