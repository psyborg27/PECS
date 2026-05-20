# Architectural Drift Report

## Intended vs current architecture

Intended design:
- runtime-resolved continuity/locality authority
- evidence-weighted workspace intelligence
- deterministic locality resolver
- compact execution interface
- prompt-local task guidance only

Current implementation:
- largely artifact-driven authority
- prompt input used for localized symbol and safety signals
- deterministic projection output and read-only validation
- some drift remains in whitebox prompt heuristics

## Drift observations

### Runtime evidence system → prompt-governed orchestration
- Core continuity authority remains runtime artifact-based.
- The drift is limited to safety heuristics and symbol ranking.
- `detect_behavioral_failures()` interprets `issue_query` text patterns.
- `resolve_symbol_authority()` selects probable symbols based on prompt tokens.

### Where drift appears
- `PECSProQueryAdapter` in `resolve_symbol_authority()` and `detect_behavioral_failures()`.
- `ProjectionExporter` in constructed runtime target fields.
- chat/correlation pipeline in `append_ai_chat_history.py` if raw narrative is supplied without structured correlation.

### Why drift occurred
- to reduce model workload and avoid broad search expansion
- to make `PECS-LITE` safer for small models
- to enable localized symbol selection from compact projections

### When drift is visible
- during `PECS-LITE` projection generation with `issue_query` input.
- when `issue_query` contains grep/recursive keywords.
- when model profile heuristics choose expansion limits.

## Drift severity

- Moderate: prompt heuristics exist but do not change the underlying topology/locality authority.
- Low on core authority: no evidence of prompt-driven topology reconstruction.
- High in user-facing safety behavior: prompt text can alter search expansion.

## Subsystems involved

- `PECSProQueryAdapter`
- `ProjectionExporter`
- `.github/copilot-instructions.md`
- `.continue/rules/pecs-first-routing.yaml`
- `append_ai_chat_history.py`

## Recommendation for future action

- preserve runtime artifact authority in core resolution paths
- isolate prompt-driven safety heuristics from topology and ownership decisions
- keep `issue_query` influence scoped to symbol ranking and warnings
- maintain the read-only validation boundary for deterministic behavior
