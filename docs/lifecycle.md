# PECS Workspace Lifecycle

This document describes the canonical workspace lifecycle: creation, rebuild,
cleanup, validation, auditing, diagnostics, and recovery.

## Workspace Creation

```bash
pecs workspace-init <workspace>          # Initialize a new workspace
pecs install-workspace-assets <workspace> # Install PECS assets
pecs daemon start <workspace>            # Start the daemon
pecs workspace-ready --workspace <workspace>  # Verify readiness
```

For workspaces with existing PECS state:

```bash
pecs status <workspace>                  # Check current state
pecs upgrade-workspace <workspace>       # Upgrade to latest version
```

## Workspace Status

```bash
pecs status <workspace>                  # Show daemon + workspace state
pecs daemon status <workspace>           # Daemon-specific status
pecs health <workspace>                  # Authoritative health check
pecs workspace-ready --workspace <workspace>  # Full readiness assessment
```

## Clean Rebuild

The deterministic clean rebuild restores a workspace to a known good state:

```bash
pecs rebuild <workspace>                 # Full clean rebuild (default)
```

This performs:

1. **Stop daemon** — kills the running daemon if present
2. **Clean artifacts** — removes all generated `.pecs/` artifacts except
   configuration files (config/, bridge/, tools/) and user data
3. **Install assets** — reinstalls all manifest assets
4. **Rebuild runtime data** — runs `pecs refresh` via the bridge
5. **Start daemon** — restarts the daemon
6. **Validate** — runs canonical validation

For incremental rebuilds (skip the destructive clean):

```bash
pecs rebuild <workspace> --incremental
```

## Workspace Cleanup

```bash
pecs clean <workspace> --artifacts       # Remove generated artifacts only
pecs clean <workspace> --runtime         # Remove runtime data only
pecs clean <workspace> --all             # Remove everything (both)
```

`--artifacts` removes: workspace_graph(_validation), registry(_validation),
active_context, compact_bundle, session_context, daemon_state, daemon_health,
daemon_cycle_validation, daemon.pid, runtime_activation.jsonl, etc.

`--runtime` removes: locality_index.json, topology_compact.json, and runtime/
logs/ subdirectories.

Configuration, bridge scripts, tools, the consumer protocol, chat history,
launcher scripts, and backups are preserved.

## Artifact Validation

```bash
pecs validate-artifacts <workspace>      # Validate individual artifacts
pecs validate-artifacts <workspace> --json   # JSON output
pecs validate <workspace>                # Full continuity validation
```

`validate-artifacts` checks each expected artifact for: file existence, valid
JSON parse, and required top-level keys. Reports PASS/FAIL per artifact and
overall status.

## Artifact Audit

```bash
pecs audit-artifacts <workspace>             # Full audit with default concepts
pecs audit-artifacts <workspace> --json      # JSON output
pecs audit-artifacts <workspace> --concepts OCR TOC Bookmark  # Custom concepts
```

Reports:
- Schema version, generator version, creation timestamp
- Artifact inventory (exists/size/stale)
- Dependency graph between artifacts
- Counts: graph nodes, edges, locality entries, registry mismatches, etc.
- Semantic coverage for engineering concepts (Annotation, Toolbar, OCR, TOC,
  Bookmark, Notes, Workspace, Selection, Rendering, Export, Import)
- Warnings for missing dependent artifacts

## Projection Diagnostics

```bash
pecs explain-query <workspace> --query "annotation toolbar interaction focus"
```

Explains why PECS returns specific runtime targets:
1. Parsed query terms
2. Locality matches (matched terms per PECS ID)
3. Topology matches (matched edges)
4. Excluded targets (weak partial matches with reasons)
5. Confidence estimate

## Query Comparison

```bash
pecs compare-query <workspace> --query "annotation toolbar"
```

Compares retrieval across:
- **grep** — text search across all .py files
- **locality index** — PECS locality payload matches
- **topology** — PECS edge matches

Reports differences: entities found by grep but missed by PECS methods.

## Daemon Management

```bash
pecs daemon status <workspace>           # Is it running? PID? Health flags?
pecs daemon start <workspace>            # Start the daemon
pecs daemon stop <workspace>             # Stop the daemon
pecs daemon restart <workspace>          # Restart the daemon
```

Also available at the top level for backward compatibility:

```bash
pecs stop-daemon <workspace>
pecs restart-daemon <workspace>
```

## Recovery from Corrupted Artifacts

### Recover with rebuild (recommended)

```bash
pecs rebuild <workspace>
```

This is the canonical recovery procedure — it stops the daemon, removes all
generated artifacts, reinstalls assets, rebuilds from scratch, and validates.

### Manual steps if rebuild fails

```bash
# 1. Stop daemon
pecs daemon stop <workspace>

# 2. Clean everything
pecs clean <workspace> --all

# 3. Reinstall assets
pecs install-workspace-assets <workspace>

# 4. Rebuild
pecs rebuild <workspace>

# 5. Verify readiness
pecs workspace-ready --workspace <workspace>
```

### If daemon lock is stuck

```bash
rm -f <workspace>/.pecs/daemon.lock
pecs daemon start <workspace>
```

### If artifacts are stale (daemon stopped)

```bash
pecs daemon start <workspace>
pecs workspace-ready --workspace <workspace>
```

## Verbose Logging

All commands support `--verbose` for detailed output:

```bash
pecs --verbose rebuild <workspace>
pecs --verbose validate-artifacts <workspace>
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `pecs status <w>` | Show workspace and daemon state |
| `pecs daemon status <w>` | Show daemon health |
| `pecs health <w>` | Authoritative health check |
| `pecs workspace-ready --workspace <w>` | Full readiness |
| `pecs rebuild <w>` | Clean rebuild all artifacts |
| `pecs rebuild <w> --incremental` | Incremental rebuild |
| `pecs clean <w> --all` | Remove all generated artifacts |
| `pecs clean <w> --artifacts` | Remove generated artifacts only |
| `pecs clean <w> --runtime` | Remove runtime data only |
| `pecs validate-artifacts <w>` | Validate individual artifacts |
| `pecs audit-artifacts <w>` | Full audit with semantic coverage |
| `pecs explain-query <w> --query "..."` | Diagnose projection |
| `pecs compare-query <w> --query "..."` | Compare PECS vs grep |
| `pecs consult <w> --query "..." --source <c>` | Consumer query |
| `pecs doctor` | Health diagnostic |
| `pecs upgrade-workspace <w>` | Upgrade workspace |
