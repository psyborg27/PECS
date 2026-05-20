# PECS-LITE Role Analysis

## Current observed behavior

### A. Runtime execution interface
- Yes. `PECS-LITE` is implemented as a stateless runtime projection layer in `PECSLiteRuntimeV2`.
- It queries PECS-PRO artifacts and returns compact locality guidance.
- It does not own continuity state or perform workspace scans.

### B. Prompt expansion layer
- Only minimally. `issue_query` is used for symbol ranking and safety heuristics.
- `PECS-LITE` does not use prompts to build topology or continuity authority.
- It is not a generic prompt amplification engine.

### C. Continuity bridge
- Yes. `PECS-LITE` bridges `.pecs` artifacts into model-facing runtime projections.
- It produces structured outputs, diagnostics, and execution hints.

### D. Hidden orchestration layer
- Not by design. The layer is transparent about artifact reads and diagnostics.
- It does contain safety heuristics that respond to prompt content, but these are visible in code.

### E. Locality resolver
- Yes. Locality resolution is the primary PECS-LITE responsibility.
- It selects runtime targets, secondary neighbors, and execution adjacency based on continuity and topology artifacts.

## Actual role assessment

- `PECS-LITE` is best categorized as a runtime execution interface and locality resolver.
- It is not a hidden orchestration layer; the code documents and asserts query-driven behavior.

## Current output behavior

- The projection output contains `runtime_targets`, `secondary_neighbors`, `pecs_runtime_report`, and `runtime_context`.
- This is consistent with an execution interface rather than a prompt orchestration layer.

## Caveat

- Prompt-derived safety heuristics remain, especially in `detect_behavioral_failures()`.
- Those heuristics should be monitored to prevent drift into prompt-governed orchestration.
