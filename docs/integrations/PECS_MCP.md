# PECS MCP Integration (Experimental)

> Version: 1.0.0-alpha1 | Status: Experimental

## Architecture

The MCP server is a thin transport adapter that exposes existing PECS functionality through the [Model Context Protocol](https://modelcontextprotocol.io/).

```
MCP Client (Claude, Cursor, etc.)
        │ JSON-RPC 2.0 over stdio
        ▼
pecs-mcp (integrations/pecs_mcp_server.py)
        │ calls only
        ▼
PECSServiceFacade (integrations/pecs_service_facade.py)
        │ delegates to existing modules
        ▼
Existing PECS codebase (CLI, daemon, adapters, etc.)
```

**Key architectural constraints:**

- The MCP server contains **zero** engineering logic, projection logic, query interpretation, ranking, topology, or continuity logic.
- All business logic remains in the existing PECS core modules.
- `PECSServiceFacade` is the single internal gateway that all future adapters (MCP, SDK, VS Code, Cursor, etc.) must consume.
- The facade delegates to existing PECS modules (`PECSLiteRuntimeAdapter`, `QueryParser`, artifact loading) without duplicating their code.

## Available Tools

### `pecs_consult`

Primary engineering consultation. Takes a free-text query and returns PECS evidence.

**Input:**

```json
{
  "query": "find annotation rendering code",
  "profile": "medium"
}
```

**Output:** Current PECS consult response (locality, projected files, authority, confidence, workspace info). Semantics are identical to `pecs consult`.

### `pecs_projection`

Retrieve the detailed projection associated with a consult result.

**Input:**

```json
{
  "projection_id": "optional-id-from-previous-consult"
}
```

**Output:** Current projection information from PECS.

### `pecs_explain`

Diagnose why PECS returns specific results for a query. Same semantics as `pecs explain-query`.

**Input:**

```json
{
  "query": "string"
}
```

**Output:** Parsed terms, locality matches, topology matches, confidence score.

### `pecs_health`

Diagnostic information about the PECS daemon and workspace.

**Input:** None.

**Output:** Daemon status, workspace indexed state, version, continuity and graph availability.

## Installation

The MCP server ships as an entry point in the `pecs_pro` package:

```bash
pip install -e .
# or activate the existing venv
source .venv/bin/activate
pip install -e .
```

Verify installation:

```bash
pecs-mcp --help
# or check the entrypoint:
which pecs-mcp
```

## Running Locally

```bash
# With default workspace (current directory)
pecs-mcp

# With explicit workspace path
pecs-mcp /path/to/your/workspace
```

The server listens on stdin and writes to stdout. It does not start a TCP socket.

## Connecting to an MCP Client

### Claude Desktop / Claude Code

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pecs": {
      "command": "pecs-mcp",
      "args": ["/path/to/your/workspace"]
    }
  }
}
```

### VS Code (with MCP extension)

Configure the MCP server in VS Code settings:

```json
{
  "mcpServers": {
    "pecs": {
      "command": "pecs-mcp",
      "args": ["${workspaceFolder}"]
    }
  }
}
```

### Manual Testing with stdio

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | pecs-mcp
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | pecs-mcp
```

## Tool Invocation Examples

To test a tool directly via stdin:

```bash
cat <<'EOF' | pecs-mcp /path/to/workspace
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"pecs_health","arguments":{}}}
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"pecs_explain","arguments":{"query":"find annotation code"}}}
{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"pecs_consult","arguments":{"query":"where is annotation rendering","profile":"small"}}}
EOF
```

## Troubleshooting

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| `Method not found` | Client sent an unsupported method | Only `initialize`, `tools/list`, `tools/call` are supported |
| `Unknown tool` | Tool name doesn't match | Use `pecs_consult`, `pecs_projection`, `pecs_explain`, `pecs_health` |
| Empty `daemon_running: false` | Daemon not started for the workspace | Run `pecs daemon start <workspace>` |
| No locality matches | PECS artifacts missing | Run `pecs refresh <workspace>` first |
| Import errors | Package not installed | Run `pip install -e .` from the PECS repo root |

## Backward Compatibility

- Existing CLI commands (`pecs consult`, `pecs explain-query`, `pecs health`, etc.) continue to function unchanged.
- The daemon is unaffected.
- Existing tests must continue to pass.
- The facade and MCP server are additive — no existing code was modified (except `pyproject.toml` for the entry point).

## Non-Goals

This is an experimental integration. It does **not**:

- Redesign PECS
- Redesign projections
- Redesign the query pipeline
- Redesign the daemon
- Redesign the CLI
- Introduce new engineering algorithms
- Introduce AI or semantic reasoning
- Move business logic into the adapter layer
