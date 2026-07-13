# Troubleshooting

This guide covers common PECS operational issues, observability, and recovery procedures.

## Health Check

Verify installation and entrypoints from the PECS repo root:

```bash
pecs doctor
```

Or run the bootstrap health check directly:

```bash
python3 scripts/pecs_health_check.py
```

To validate dependencies only:

```bash
python3 install_workspace_integration.py <workspace-root> --validate-deps
```

## Daemon Observability

The daemon writes structured JSONL logs under `.pecs/logs/`:

- `.pecs/logs/daemon_activity.log` — daemon lifecycle and refresh events
- `.pecs/logs/continuity_sync.log` — continuity extraction and projection refresh
- `.pecs/logs/daemon_errors.log` — failures and retries

Log rotation is lightweight: maximum 256 KB per file with up to three backups (`.log.1`, `.log.2`, `.log.3`).

### Common daemon events

| Log | Event | Meaning |
|-----|-------|---------|
| `daemon_activity.log` | `daemon_initialized` | Daemon started |
| `daemon_activity.log` | `file_change_detected` | File watcher triggered |
| `daemon_activity.log` | `continuity_refresh_started` / `continuity_refresh_completed` | Refresh cycle ran |
| `continuity_sync.log` | `projection_no_changes` | Rebuild produced identical output |
| `continuity_sync.log` | `projection_skipped` | Refresh skipped due to throttling or missing payload |
| `daemon_errors.log` | `bridge_execution_failed` | Bridge refresh failed |
| `daemon_errors.log` | `write_retry` / `write_timeout` | Artifact write needed retry |

Each event includes `ts` (ISO 8601 UTC), `event`, and a minimal `details` payload.

## Common Issues

### PECS installed into an unstable location

**Symptom**: installer or health check warns about transient directory.

**Resolution**: reinstall into a stable location such as `~/Developer/PECS/` or `~/Applications/PECS/`. Avoid `Downloads`, `Desktop`, `/tmp`, and removable drives.

### Artifacts are stale or missing

**Symptom**: `pecs doctor` reports missing artifacts or query-pipeline returns empty results.

**Resolution**:

```bash
pecs refresh "/path/to/workspace"
pecs validate "/path/to/workspace"
```

If the daemon is not running:

```bash
pecs restart-daemon "/path/to/workspace"
```

### Workspace moved or install root changed

**Symptom**: VS Code tasks, daemon launchers, or bridge paths point to an old PECS install root.

**Resolution**: rebind the workspace after reinstalling PECS:

```bash
pecs rebind-workspace "/path/to/workspace" --upgrade
```

### PECS-LITE projection error

**Symptom**: `integrations/pecs_lite_runtime_adapter.py` reports a projection error or fallback is triggered.

**Resolution**:

1. Confirm `.pecs/active_context.json`, `.pecs/locality_index.json`, and `.pecs/topology_compact.json` exist.
2. Run `pecs refresh` to regenerate artifacts.
3. Check `.pecs/logs/daemon_errors.log` for write failures.

Fallback to `TopologyRetriever.build_minimal_context(object_id)` is intentional when the projection layer cannot produce a result; the fallback reason is recorded in the response.

### Determinism drift

**Symptom**: repeated queries produce different hashes or rankings for unchanged files.

**Resolution**:

- Verify that no `.pecs/` artifacts are hand-edited.
- Check that entrypoint files exist and are readable.
- Confirm the daemon is using sorted iteration by reviewing `daemon_errors.log` for warnings.

## Validation Commands

```bash
pecs verify-workspace "/path/to/workspace"
pecs status "/path/to/workspace"
pecs validate "/path/to/workspace"
```

## Support Notes

- `.pecs/` artifacts are infrastructure only. Do not edit them as sourcecode.
- Workspace runtime modules remain authoritative.
- PECS does not replace engineering judgment. Validate outputs manually and use version control.

For installation guidance, see [installation.md](installation.md). For artifact descriptions, see [artifacts.md](artifacts.md).
