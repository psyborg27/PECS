# Prompt Minimization Report

## Summary

- PECS-LITE no longer relies on large governance or locality prompts for runtime arbitration.
- The only prompt-derived input in the projection path is `issue_query`, which is used for symbol authority resolution.
- Runtime output is now deterministic and structured, reducing the need for conversational prompt scaffolding.

## Implementation details

- `ProjectionExporter` now emits `pecs_runtime_report` with fixed keys and explicit runtime state.
- `RuntimeContextResolver` provides the runtime context without prompt or artifact mutation.
- `reasoning_basis` labels were simplified to deterministic evidence categories.

## Desired compact workflow

Example compact prompts now map cleanly onto the runtime interface:

- `Use PECS runtime context and implement clipboard stabilization.`
- `Use PECS runtime context and audit hyperlink serialization.`

These prompts can be satisfied using the deterministic `PECS-LITE` runtime output without large prompt amplification.
