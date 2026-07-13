# DAEMON_OBSERVABILITY_PROTOCOL

## Purpose

This protocol documents the lightweight runtime observability added to the PECS daemon.
It is intentionally operational only: no telemetry infrastructure, no orchestration state machine, no large debug archives.

## Log outputs

The daemon now writes structured event logs under `.pecs/logs/`.

Files:
- `.pecs/logs/daemon_activity.log`
- `.pecs/logs/continuity_sync.log`
- `.pecs/logs/daemon_errors.log`

Each file is written as one JSON object per line.

## Rolling behavior

- Maximum file size: 256 KB
- Backup count: 3
- Rotation is daemon-local and lightweight
- Old log files are retained as `.log.1`, `.log.2`, `.log.3`

## Log semantics

### `daemon_activity.log`
Tracks the runtime trigger lifecycle and high-level refresh events.

Logged events:
- `daemon_initialized`
- `file_change_detected`
- `copilot_activity_detected`
- `continue_activity_detected`
- `runtime_activation_detected`
- `continuity_refresh_started`
- `continuity_refresh_completed`
- `bridge_execution_succeeded`

### `continuity_sync.log`
Tracks continuity extraction and projection refresh behavior.

Logged events:
- `workspace_filter_applied`
- `continuity_entries_extracted`
- `continuity_entries_skipped`
- `continuity_noop`
- `timestamp_gap_detected`
- `projection_refresh_started`
- `projection_refresh_completed`
- `compact_bundle_refreshed`
- `active_context_refreshed`
- `topology_compact_refreshed`
- `locality_index_refreshed`
- `projection_skipped`
- `projection_no_changes`

### `daemon_errors.log`
Tracks failure conditions and retries.

Logged events:
- `continuity_extraction_failed`
- `write_retry`
- `write_timeout`
- `projection_refresh_failed`
- `bridge_execution_failed`
- `incremental_sync_failed`

## Event payloads

Each event includes:
- `ts` — ISO 8601 UTC timestamp
- `event` — event name
- `details` — minimal structured context for the event

Example:
```json
{"ts":"2026-05-21T12:00:00Z","event":"file_change_detected","details":{"path":"src/app.py"}}
```

## Operational philosophy

This observability is:
- lightweight: small JSONL logs, no external service
- daemon-local: stored under workspace `.pecs/logs`
- incrementally useful: each event reflects an actual runtime step
- non-invasive: no architecture redesign, only instrumentation
- deterministic: same event model for the daemon lifecycle

## Use cases

This protocol supports the following operational questions:
- Did a file change actually reach the daemon?
- Did the daemon execute topology rebuild logic?
- Was a chat or continue event detected as `copilot_activity_detected` or `continue_activity_detected`?
- Did projection refresh begin and complete?
- Was a refresh skipped due to throttling or missing payload?
- Did a bridge refresh fail, or did a write retry occur?
- Was the projection write a no-op because content did not change?
