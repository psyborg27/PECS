# PECS KIMI ADAPTER DESIGN

## Goal

Design a Kimi integration that participates in continuity retrieval and continuity generation in the same manner as Continue and Copilot.

## Design Principles

- Reuse existing PECS-LITE projection infrastructure
- Keep Kimi behavior consistent with Continue/Copilot for retrieval and fallback
- Preserve `.pecs` continuity artifacts during installation and upgrade
- Trigger the same bridge-based continuity refresh path for Kimi-generated events
- Maintain explicit separation between runtime projection and continuity export

## Kimi Retrieval Design

### Core adapter

Create a new adapter module, e.g. `integrations/kimi_adapter.py`, with the following responsibilities:

- Accept a Kimi query request containing:
  - `object_id`
  - `query_text`
  - `model_id`
  - `session_id`
  - `request_metadata`
- Normalize request metadata into a standard projection payload
- Call `PECSLiteRuntimeAdapter.build_projection_safe(...)`
- Tag query source as `kimi`
- Return a unified response shape with:
  - `runtime_targets`
  - `secondary_neighbors`
  - `inferred_focus`
  - `fallback_context`
  - `advisories`
  - `diagnostic_payload`

### Shared retrieval flow

Follow the same pattern used by `continue_adapter.py` and `copilot_adapter.py`:

1. Build request payload and telemetry context
2. Attempt projection via `PECSLiteRuntimeAdapter.build_projection_safe`
3. If successful, return projection data
4. If projection fails, call `TopologyRetriever.build_minimal_context(object_id)`
5. Log fallback and return a safe advisory response

### Model embedding and wrapper behavior

- Kimi should pass `query_source = "kimi"`
- Preserve `user_profile` and `conversation_history` metadata for downstream advisories
- Use the same safe-fallback semantics to avoid overreliance on continuity when runtime projection is unavailable

## Kimi Continuity Generation Design

### Event ingestion

Leverage the existing `.pecs/tools/append_ai_chat_history.py` pipeline for Kimi event ingestion.

- Kimi should append relevant continuity events to `.pecs/ai_chat_history.json`
- Use the same normalization and deduplication rules as other sources
- Add `source = "kimi"` and maintain `event_type` semantics

### Event types

Support the following Kimi-specific event payloads:

- `kimi_query_requested`
- `kimi_query_completed`
- `kimi_continuity_suggestion`
- `kimi_decision_applied`

Each event payload should include:

- `workspace_root`
- `workspace_id`
- `source`
- `event_type`
- `message`
- `component`
- `object_ids`
- `correlation`
- `ts`

### Continuity refresh trigger

- Kimi event ingestion should update `.pecs/ai_chat_history.json`
- The daemon watches this file and will invoke `_on_chat_history_update_unlocked()`
- This will call `_run_continuity_refresh(trigger="chat_history_update", reason="Kimi continuity event")`
- The refresh path executes `.pecs/bridge/run_bridge.py refresh`

## Installer and Workspace Asset Integration

### Asset manifest

Extend `workspace_assets/workspace_assets_manifest.json` to include Kimi integration assets.

New entries should include:

- `.kimi/config.yaml`
- `.kimi/instructions.md`
- `.kimi/rules/PECS_CONTEXT_RULE.md`
- `.kimi/rules/PECS_APPEND_RULE.md`

### Preservation policy

- Preserve existing `.pecs/ai_chat_history.json` and continuity exports during Kimi install/upgrade
- Backup modified workspace assets before replacement
- Append to `copilot-instructions.md` or workspace-level docs only when needed

### Installation path

- Add a `install_kimi_integration` flow to `install_workspace_integration.py`
- Add a `kimi` target to `workspace_bridge_cli.py` if relevant
- Reuse the same manifest-based asset manager for safe merges

## Continuity Retrieval and Generation Parity

### Retrieval parity with Continue/Copilot

- Use the same runtime projection adapter and fallback rules
- Use Kimi-specific query tagging only at metadata layer
- Return the same diagnostic fields for downstream observability

### Generation parity with Continue/Copilot

- Use `.pecs/tools/append_ai_chat_history.py` for all continuity ingestion
- Avoid creating new proprietary continuity sinks
- Use daemon-triggered bridge refresh to update `.pecs/continuity/*`

## Suggested Implementation Sketch

### `integrations/kimi_adapter.py`

- `KimiRuntimeAdapter.build_projection_safe(query_payload)`
- `KimiRuntimeAdapter._build_query_metadata(...)`
- `KimiRuntimeAdapter._build_safe_fallback(object_id)`

### `.pecs/tools/append_ai_chat_history.py`

- Add `source == "kimi"` support in event normalization
- Ensure Kimi payloads are deduplicated by event signature

### `install_workspace_integration.py`

- Add `_install_kimi_rules()` and `_write_kimi_config()` helpers
- Include Kimi assets in `workspace_assets_manifest.json`

### `workspace_bridge_cli.py`

- Add `install-kimi-assets` or `bootstrap-kimi` command aliases
- Ensure continuity refresh commands accept `query_source=kimi`

## Gap analysis

### Current repo gaps

- No existing Kimi-specific code or assets present
- No `kimi/` or `prompt_responses/` directories found
- Current adapters are limited to Continue and Copilot

### Recommended first steps

1. Add `integrations/kimi_adapter.py`
2. Extend `workspace_assets_manifest.json` for Kimi
3. Add Kimi event ingestion docs and examples in `.pecs/README.md`
4. Build end-to-end test coverage for Kimi query and continuity refresh

## Conclusion

This design ensures Kimi will integrate with PECS using the same retrieval/fallback semantics as Continue and Copilot, while preserving the existing `.pecs` continuity artifact model and installer upgrade behavior. The Kimi integration should remain a first-class consumer of the PECS bridge and should not introduce proprietary continuity storage outside `.pecs`.