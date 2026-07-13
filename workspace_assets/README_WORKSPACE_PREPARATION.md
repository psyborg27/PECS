# PECS Workspace Preparation

## Overview

PECS workspace assets enable AI coding agents (Copilot, Continue, etc.) to use generated continuity infrastructure to identify runtime workspace targets and execution locality.

This document describes:
- What assets are installed
- How ingress routing works
- How to verify the installation
- How to repair a broken installation

## Critical Architecture Principle

**PECS is continuity infrastructure only. Runtime workspace modules are authoritative.**

PECS artifacts must be used to derive runtime target files and locality projection. They must never be treated as editable engineering sourcecode.

Coding agents should:
1. Prefer live workspace runtime modules for edits
2. Use `.pecs/` artifacts only to narrow locality and execution neighborhood
3. Use active execution context (`.pecs/active_context.json`) to identify likely runtime targets
4. Use locality index (`.pecs/locality_index.json`) to refine scope
5. Fall back to repository search only when PECS does not provide sufficient runtime locality

## What Gets Installed

### Workspace Configuration Files

- **.github/copilot-instructions.md** — Forces GitHub Copilot to check PECS artifacts first
- **.continue/config.yaml** — Configure Continue to respect PECS routing rules
- **.continue/rules/pecs-first-routing.yaml** — Explicit PECS-first routing rule

### Stateless PECS-LITE Projection

PECS-LITE does not scan the workspace or reconstruct runtime topology independently. It queries PECS-PRO continuity outputs and returns compact runtime target projections for the model.

### Canonical Query Workflow

Before any broad repository inspection or architectural reasoning, run the canonical PECS-LITE query command:

```bash
pecs observe-projection-snapshot "$(pwd)" \
  --query "stabilization, ownership lookup, continuity locality" \
  --query-source "copilot" \
  --model-name "unknown" \
  --profile-class frontier \
  --local-vs-frontier frontier
```

For repeated observation in longer sessions:

```bash
pecs observe-projection-daemon "$(pwd)" \
  --query "stabilization, ownership lookup, continuity locality" \
  --query-source "copilot" \
  --model-name "unknown" \
  --profile-class frontier \
  --local-vs-frontier frontier \
  --iterations 10 \
  --interval-seconds 2.0
```

Use the returned projection first; only then inspect runtime workspace files for bounded edits.

After task completion, refresh PECS artifacts with canonical lifecycle commands:

```bash
pecs refresh "$(pwd)"
pecs rebuild-continuity "$(pwd)"
pecs rebuild-topology "$(pwd)"
pecs restart-daemon "$(pwd)"
```

### Required PECS Workflow

1. Query PECS first using the canonical observe-projection commands.
2. Perform the engineering task with locality and continuity awareness.
3. Refresh or rebuild PECS artifacts after completion using canonical lifecycle commands.
4. Never hand-edit `.pecs` artifacts or continuity outputs.

### PECS Process Flow

1. Install workspace assets to configure VS Code, Continue, Copilot, and `.pecs` infrastructure.
2. Start the workspace daemon or bridge to generate `.pecs/` continuity artifacts from live runtime workspace modules.
3. PECS-PRO writes deterministic continuity infrastructure such as active context, locality index, and projected runtime neighborhoods.
4. PECS-LITE reads those artifacts and projects compact runtime workspace targets for the AI model.
5. The AI model uses runtime workspace modules for actual edits; `.pecs` files remain infrastructure only.

### PECS Ingress Directory (.pecs/)

- **.pecs/README.md** — Workspace-local PECS documentation
- **.pecs/tools/** — Workspace utilities
  - append_ai_chat_history.py
  - update_ai_chat_history.sh
- **.pecs/bridge/** — Continuity infrastructure
  - run_bridge.py
  - run_bridge.sh
  - export_workspace_continuity.py
  - validate_workspace_continuity.py
- **.pecs/config/** — Continuity configuration
  - continuity_bridge.json
- **.pecs/continuity/** — Continuity state artifacts
  - active_topology.json
  - locality_state.json
  - architectural_decisions.md
  - current_workspace_focus.md
  - unresolved_tensions.md
- **.pecs/runtime/** — Runtime execution state (generated)
- **.pecs/ai_chat_history.json** — Agent interaction history

### VS Code Integration

- **.vscode/tasks.json** — PECS daemon tasks
  - PECS: Start Daemon
  - PECS: Stop Daemon
  - PECS: Refresh Continuity State
  - PECS: Validate Continuity State
  - PECS: Auto Start Daemon On Folder Open
- **.vscode/settings.json** — Workspace settings
  - pecs.contextPath

## Installation Flow

### Fresh Install

```bash
# From within your workspace
pecs install-workspace-assets $(pwd)
```

or

```bash
# From PECS-PRO repository
./install_pecs_workspace.sh /path/to/your/workspace
```

### Upgrade Install

```bash
# Safe upgrade preserves existing configuration
pecs install-workspace-assets $(pwd) --upgrade
```

### Verify Installation

```bash
pecs verify-workspace $(pwd)
```

### Repair Broken Installation

```bash
pecs repair-workspace $(pwd)
```

## Ingress Routing Behavior

### Copilot Instructions

When Copilot suggests edits, it inspects:
1. .pecs/active_context.json (if present)
2. .pecs/compact_bundle.json (if present)
3. .pecs/session_context.json (if present)
4. .pecs/locality_index.json (if present)

Copilot uses this information to narrow search scope before suggesting edits.

### Continue Rules

When Continue suggests code, it first loads:
1. .pecs/active_context.json
2. .pecs/locality_index.json
3. .pecs/topology_compact.json

Continue respects PECS routing rule (`pecs-first-routing.yaml`) which:
- Prevents broad repository crawling initially
- Prioritizes execution topology over filesystem traversal
- Ignores backup/debug/generated folders unless explicitly activated by PECS

## Agent Configuration

### Continue Configuration

The Continue config is installed at `.continue/config.yaml`. Verify:

```yaml
rules:
  - path: rules/pecs-first-routing.yaml
    alwaysApply: true
```

### Copilot Instructions

The Copilot instructions file is at `.github/copilot-instructions.md`. Verify it contains PECS-first guidance.

## Daemon Operations

### Start Daemon

```bash
# VS Code Task
"PECS: Start Daemon"

# Manual command
cd /path/to/workspace
source .venv/bin/activate  # if present
PECS_PRO_REPO=/path/to/pecs-pro ./launch_pecs_daemon.sh
```

### Stop Daemon

```bash
# VS Code Task
"PECS: Stop Daemon"

# Manual command
kill $(cat .pecs/daemon.pid)
```

### Check Daemon Status

```bash
pecs status
```

## Troubleshooting

### Missing .pecs Directory

If .pecs/ is missing:

```bash
pecs repair-workspace $(pwd)
```

### Copilot Instructions Not Applied

1. Close and reopen workspace in VS Code
2. Verify `.github/copilot-instructions.md` exists
3. Check GitHub Copilot extension is enabled

### Continue Rules Not Applied

1. Restart Continue
2. Verify `.continue/config.yaml` has pecs-first-routing.yaml rule
3. Verify `.continue/rules/pecs-first-routing.yaml` exists

### Daemon Not Starting

```bash
# Check environment
pecs doctor

# Manual check
PECS_PRO_REPO=/path/to/pecs-pro bash -x ./launch_pecs_daemon.sh $(pwd)
```

## Workspace Continuity Artifacts

PECS maintains continuity state in `.pecs/continuity/`:

- **active_topology.json** — Current runtime topology
- **locality_state.json** — Workspace locality metrics
- **architectural_decisions.md** — Architecture notes
- **current_workspace_focus.md** — Current work focus
- **unresolved_tensions.md** — Known issues/tensions

These files are authoritative for understanding workspace state. Regular filesystem traversal is supplementary.

## Best Practices

1. **Always commit .pecs artifacts** to version control (except runtime/* and generated/)
2. **Run daemon before coding** to populate continuity artifacts
3. **Use Continue chat append** to maintain ai_chat_history.json
4. **Run verify periodically** to detect missing/broken assets
5. **Run doctor** to diagnose environment issues

## Configuration Changes

If you modify:
- Continue config → restart Continue
- Copilot instructions → reload workspace in VS Code
- PECS daemon config → stop/start daemon

To refresh PECS continuity state:

```bash
pecs refresh-workspace $(pwd)
```

## Next Steps

1. Run `pecs verify-workspace $(pwd)` to confirm installation
2. Run `pecs status` to check daemon status
3. Start daemon: `pecs daemon start $(pwd)`
4. Open Continue/Copilot and verify they respect PECS artifacts
