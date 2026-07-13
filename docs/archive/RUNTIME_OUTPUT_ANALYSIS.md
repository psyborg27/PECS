# Runtime Output Analysis

## Output characteristics

### Deterministic
- `ProjectionExporter` explicitly sets `deterministic: true` in projection output.
- `runtime_context.resolve()` returns deterministic artifact state.
- Validation and bridge outputs are JSON serialized with sorted keys.

### Structured
- The projection includes structured fields:
  - `runtime_targets`
  - `secondary_neighbors`
  - `metrics`
  - `diagnostics`
  - `continuity_supporting_artifacts`
  - `pecs_lite_status`
  - `runtime_context`
  - `pecs_runtime_report`

### Machine-stable
- Outputs are JSON objects with explicit schema names.
- `ProjectionExporter` avoids unstructured chat transcripts.

### Compact
- The `ProjectionProfile` budgets target counts and symbol expansion limits.
- `PECS-LITE` is designed for small/medium/large model context profiles.

### Provenance-aware
- `pecs_runtime_report` records artifact usage, authority source, and search plan.
- The projection includes `continuity_supporting_artifacts` and forbidden edit prefixes.

## Not present

- No raw conversational chat history is included in the final projection.
- There is no large prompt transcript baked into the locality output.

## Prompt influence

- `issue_query` still influences symbol selection and behavioral safety signals.
- This makes the runtime output prompt-aware in a scoped way, but not prompt-governed.

## Remaining verbose elements

- Some runtime target fields include narrative strings such as `why_this_location`.
- These are advisory, not core authority artifacts.

## Conclusion

The current runtime output is largely deterministic, structured, and provenance-aware.
It remains compact, with only limited prompt influence used for symbol and safety signals.
