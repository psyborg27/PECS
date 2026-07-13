# PECS Current Architecture Report

## Summary

The current PECS implementation is best described as a hybrid of runtime artifact authority and LLM-facing projection support.

Key architecture facts:
- `PECS-PRO` is the authoritative continuity source.
- `PECS-LITE` is implemented as a stateless query-driven projection layer.
- `.pecs` artifacts are treated as generated continuity infrastructure, not editable source.
- The workspace bridge refresh path writes continuity artifacts; validate is now read-only.
- Prompt input is used for scope hints and safety signals, not for core locality authority.

## Current Control Flow

- `PECSLiteRuntimeV2.build_projection()` resolves runtime context with `RuntimeContextResolver`.
- `PECSProQueryAdapter` loads runtime artifacts from `.pecs` and derives locality, topology, and ownership signals.
- `ProjectionHardener` hardens targets and applies model profile constraints.
- `ProjectionExporter` produces structured model-facing output plus `pecs_runtime_report` diagnostics.

## Authority Sources

Primary runtime evidence:
- `.pecs/active_context.json`
- `.pecs/locality_index.json`
- `.pecs/topology_compact.json`
- `.pecs/continuity/locality_state.json`
- `.pecs/continuity/active_topology.json`
- `.pecs/continuity/engineering_continuity_state.json`

Supporting evidence:
- `.pecs/ai_chat_history.json` through engineering continuity extraction
- runtime activation events in `.pecs/runtime_activation.jsonl`
- daemon health via `.pecs/daemon_health.json`

## Prompt Dependency

- `issue_query` influences symbol authority selection in `resolve_symbol_authority()`.
- `issue_query` also drives safety heuristics in `detect_behavioral_failures()`.
- Profile selection is based on model metadata, not governance prompts.
- `.github/copilot-instructions.md` and `.continue/rules` enforce artifact-first behavior.

## Validation and Refresh

- `bash .pecs/bridge/run_bridge.sh <workspace> refresh` regenerates continuity artifacts.
- `bash .pecs/bridge/run_bridge.sh <workspace> validate` checks determinism and read-only stability.
- `scripts/validate_workspace_continuity.py` now treats validation as read-only and reports `artifact_writes: 0`.

## What is working

- Runtime locality resolution is artifact-driven.
- Continuity evidence is preserved through structured chains and validity scores.
- The projection outputs are structured and include provenance metadata.
- The workspace bridge is the canonical refresh/validate mechanism.

## What is risk

- Issue-based prompt parsing remains in symbol resolution and safety heuristics.
- Chat history is normalized, but it still enters the evidence pipeline via correlation fields.
- `PECS-LITE` is still an LLM-facing layer; careful monitoring is needed to prevent it becoming a prompt orchestration layer.
