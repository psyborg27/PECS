# Prompt Dependency Analysis

## Current prompt dependence

### Direct prompt-driven behavior
- `PECSLiteRuntimeV2.build_projection()` accepts `issue_query`, `model_name`, `model_source`, and `context_window`.
- `PECSProQueryAdapter.resolve_symbol_authority()` tokenizes `issue_query` to choose probable classes/methods.
- `PECSProQueryAdapter.detect_behavioral_failures()` analyzes `issue_query` for grep/recursive terms and triggers safety compression.
- `ProjectionExporter` uses `issue_query` to populate `issue_subject` and expected outcome information.

### Indirect prompt governance
- `.github/copilot-instructions.md` and `.continue/rules/pecs-first-routing.yaml` define artifact-first guidance.
- These files instruct Copilot/Continue to use PECS artifacts and not treat `.pecs` as source.
- They are documentation-style governance, not runtime code logic.

## What is prompt-governed

Prompt influence exists primarily in:
- symbol selection for probable edit targets
- safety and breadth heuristics
- execution profile selection by model metadata

This is not the same as prompt-driven topology or locality authority.

## What is runtime-governed

Core locality and continuity resolution uses:
- `.pecs` runtime artifacts
- topology compact graphs
- locality index and active context
- continuity state in `.pecs/continuity`

Prompt wording does not control these artifact reads.

## Hidden prompt assumptions

The system still contains prompt assumptions in `detect_behavioral_failures()`:
- query text containing "grep" or "recursive" alters projection aggressiveness
- namespace-synthesis patterns are inferred from issue text

These are heuristic and should be treated as safety signals, not core authority.

## Exact systems relying on prompt orchestration

- `PECSProQueryAdapter.resolve_symbol_authority`
- `PECSProQueryAdapter.detect_behavioral_failures`
- `ProjectionExporter._build_structured_runtime_targets`

## Conclusion

Current PECS has minimal prompt dependency for safety and symbol guidance.
Core locality/search behavior remains artifact-driven, but prompt-based heuristics are present in safety and target-ranking subsystems.
