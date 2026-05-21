# REFRESH_TRACE_VALIDATION

## Verification goals

Confirm that the daemon observability logs now make the refresh chain visible end-to-end.

### Primary checks

1. `file_change_detected` is emitted when a monitored file changes.
2. `copilot_activity_detected` or `continue_activity_detected` is emitted when chat history is updated.
3. `runtime_activation_detected` is emitted when runtime activation events change.
4. `topology_rebuild_started` and `topology_rebuild_completed` are emitted when topology rebuild occurs.
5. `projection_refresh_started` and `projection_refresh_completed` are emitted when compact or active context regeneration happens.
6. `continuity_refresh_started` and `continuity_refresh_completed` are emitted when the bridge refresh runs.
7. `projection_skipped` is emitted when refresh is intentionally bypassed.
8. `projection_no_changes` is emitted when a projected artifact was unchanged.
9. `bridge_execution_failed` is emitted on bridge refresh failure.

## Sample log flow

### Topology rebuild flow

`daemon_activity.log`
```json
{"ts":"2026-05-21T12:00:00Z","event":"file_change_detected","details":{"path":"src/app.py"}}
{"ts":"2026-05-21T12:00:01Z","event":"topology_rebuild_started","details":{"changed_files":["src/app.py"]}}
```

`continuity_sync.log`
```json
{"ts":"2026-05-21T12:00:02Z","event":"workspace_filter_applied","details":{"excluded_path_count":2,"example_excluded_paths":[".git/config","venv/lib.py"]}}
{"ts":"2026-05-21T12:00:03Z","event":"projection_refresh_started","details":{"trigger":"runtime_topology","reachable_files":34,"edge_count":18}}
{"ts":"2026-05-21T12:00:04Z","event":"topology_compact_refreshed","details":{"edge_count":18}}
{"ts":"2026-05-21T12:00:04Z","event":"compact_bundle_refreshed","details":{"context_count":22}}
{"ts":"2026-05-21T12:00:04Z","event":"active_context_refreshed","details":{"activated_objects":9}}
{"ts":"2026-05-21T12:00:05Z","event":"projection_refresh_completed","details":{"trigger":"runtime_topology"}}
```

### Chat activity flow

`daemon_activity.log`
```json
{"ts":"2026-05-21T12:01:00Z","event":"copilot_activity_detected","details":{"source":"copilot"}}
```

`continuity_sync.log`
```json
{"ts":"2026-05-21T12:01:01Z","event":"continuity_entries_extracted","details":{"chat_entry_count":7,"latest_source":"copilot"}}
{"ts":"2026-05-21T12:01:02Z","event":"projection_refresh_started","details":{"trigger":"chat_history"}}
{"ts":"2026-05-21T12:01:03Z","event":"compact_bundle_refreshed","details":{"context_count":24}}
{"ts":"2026-05-21T12:01:03Z","event":"active_context_refreshed","details":{"activated_objects":10}}
{"ts":"2026-05-21T12:01:04Z","event":"projection_refresh_completed","details":{"trigger":"chat_history"}}
```

### Failure flow

`daemon_errors.log`
```json
{"ts":"2026-05-21T12:02:00Z","event":"bridge_execution_failed","details":{"trigger":"chat_history","reason":"AI chat history update","error":"Bridge refresh failed with exit code 1"}}
```

## Practical validation commands

1. Make a `.py` edit and inspect `.pecs/logs/daemon_activity.log` for `file_change_detected` and `topology_rebuild_started`.
2. Append an AI chat event to `.pecs/ai_chat_history.json` and inspect `.pecs/logs/daemon_activity.log` and `.pecs/logs/continuity_sync.log` for chat trigger events and projection refresh events.
3. Write a runtime activation event to `.pecs/runtime_activation.jsonl` and inspect `.pecs/logs/daemon_activity.log` for `runtime_activation_detected` and `.pecs/logs/continuity_sync.log` for projection refresh events.
4. Force a bridge or artifact write failure and inspect `.pecs/logs/daemon_errors.log` for structured failure events.

## Expected result

The logs should now make the refresh chain visible enough to answer:
- Did the daemon receive the trigger?
- Did extraction run or skip?
- Did projection regeneration execute, no-op, or fail?
- Did the bridge refresh complete or fail?
