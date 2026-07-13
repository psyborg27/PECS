# Prompt Heuristic Isolation Report

## Objective

Ensure prompt text remains advisory/task-local and cannot directly alter topology/locality/ownership authority.

## Implemented

### Behavioral prompt analysis downgraded to advisory

In `integrations/pecs_pro_query_adapter.py`:

- `detect_behavioral_failures()` now returns `advisory_only: true`.
- Removed authoritative control flags:
  - `emergency_locality_compression`
  - `force_authority_projection`
  - `reduce_topology_breadth`

### Prompt text no longer drives expansion authority

In `integrations/pecs_lite_projection_hardener.py`:

- Removed prompt-driven expansion control coupling.
- `search_expansion_allowed` now derives from deterministic evidence quality thresholds (`tier_1_runtime`, `tier_2_continuity`, fused score).
- Traversal roots remain artifact-derived (`runtime_confirmed_neighborhood_lookup`).

### Prompt signals preserved as advisory output only

In `PECS_LITE v2/pecs_lite v2/runtime/pecs_lite_runtime_v2.py`:

- prompt behavior is surfaced in `prompt_behavior_advisory`.
- No runtime control mutations are applied from prompt-behavior flags.

## Verification

Runtime check executed with two very different prompts:

- evidence-fusion top-5 files remained identical
- advisory flag remained `true`
- runtime protocol sections remained stable

Result: prompt wording no longer changes locality authority ranking.

## Files changed

- `integrations/pecs_pro_query_adapter.py`
- `integrations/pecs_lite_projection_hardener.py`
- `PECS_LITE v2/pecs_lite v2/runtime/pecs_lite_runtime_v2.py`
