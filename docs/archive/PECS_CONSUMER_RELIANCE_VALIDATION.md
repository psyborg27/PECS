# PECS Consumer Reliance Validation

## Purpose
Validate whether the installed Copilot integration currently relies on PECS projections for issue-specific engineering audit queries, using the current code and available runtime telemetry.

## Scope
- Analysis limited to current implementation in `integrations/copilot_adapter.py` and `integrations/pecs_lite_runtime_adapter.py`
- Uses available live telemetry from `telemetry/runtime_jsonl/*.jsonl`
- Does not redesign or modify runtime behavior

## 1. Current Copilot-PECS Integration Path

### Code path
- `CopilotAdapter.build_copilot_context(object_id, ...)` is the main Copilot entrypoint.
- It emits `copilot_query_received` before calling `PECSLiteRuntimeAdapter.build_projection_safe(...)`.
- The Adaptor calls `PECSLiteRuntimeAdapter.build_projection(...)` and returns the final projection payload.
- After projection generation, it emits `copilot_projection_finalized` and returns:
  - `projection`
  - `emitted_advisory_cognition`
  - `discarded_cognition_summary`
  - `shaping_losses`
  - `final_emission_observability`
  - `consumption_boundary`
- If `PECS-LITE` fails, Copilot may fall back to `TopologyRetriever.build_minimal_context(object_id)`.

### Runtime behavior
- Current telemetry confirms `copilot_query_received` and `copilot_projection_finalized` are emitted.
- The reported `consumption_mode` is `advisory_evidence`.
- `hard_enforcement` is explicitly `false` in telemetry.
- This means Copilot uses PECS as an advisory projection interface, not as an enforced search-only authority.

## 2. Evidence Sources Loaded by Copilot

PECS-LITE loads evidence from PECS-PRO artifacts, not by scanning the workspace directly.
Evidence sources include:
- `.pecs/active_context.json`
- `.pecs/compact_bundle.json`
- `.pecs/locality_index.json`
- `.pecs/topology_compact.json`
- `.pecs/continuity/locality_state.json`
- `.pecs/continuity/active_topology.json`
- `.pecs/continuity/engineering_continuity_state.json`

These artifacts are read by `PECSProQueryAdapter` and then fused by `ProjectionHardener`.

## 3. Evidence Consumption Observed

### Active consumption
- Runtime authority evidence is actively consumed.
- Locality authority evidence is actively consumed.
- Ownership and historical continuity evidence are consumed in ranking.
- User acceptance/rejection history is read and used.
- Continuity evidence appears in advisory outputs and projection metadata.

### Evidence oversupply
- The implementation loads broad continuity and chat-derived evidence.
- Final projections often suppress or compress many continuity details.
- This supports the finding that current PECS collects more evidence than it fully exposes or uses in final output.

## 4. Available Live Audit Evidence

### Exact issue-name audits requested
The following issue names were searched across the workspace and telemetry logs:
- `Send Annotation To Note`
- `OCR Tabs`
- `Notes Drawing`

Result: **No exact match found** in the available telemetry or saved query outputs.

### Nearby evidence examples
Existing runtime telemetry does contain PECS query activity for similar operational flows:
- `Clipboard paste not working in Notes Module.`
- `CAMLT/OpenCV reconciliation test`

Those logs show the same Copilot-PECS path and consumption pattern.

## 5. Specific Issue Audit Assessment

### A. Send Annotation To Note failure
- Current workspace telemetry does not contain this exact issue label.
- Based on implementation, such a query would follow the same advisory PECS flow.
- No direct runtime evidence is available to confirm exact issue-specific reliance.

### B. OCR Tabs malfunction
- Current telemetry does not contain this exact issue label.
- The current code path would still use `PECSLiteRuntimeAdapter` and advisory evidence.
- No exact runtime projection data exists for this issue in the available artifacts.

### C. Notes Drawing issue
- Current telemetry does not contain this exact issue label.
- The integration path remains the same, but no exact runtime evidence is available.

## 6. Conclusion

### Current reliance summary
- Copilot currently relies on PECS projections in the sense that it queries `PECSLiteRuntimeAdapter` and uses the returned projection payload.
- The reliance is advisory, not hard enforcement.
- Telemetry confirms the execution path and advisory consumption mode.

### Limitation
- For the three requested issue names, the current workspace does not include exact runtime evidence.
- Therefore, we cannot confirm issue-specific reliance beyond the general integration behavior.

## 7. Recommendation

To validate exact issue-specific reliance for `Send Annotation To Note`, `OCR Tabs`, or `Notes Drawing`:
1. Capture or generate runtime telemetry for the exact query label.
2. Confirm `copilot_query_received` and `copilot_projection_finalized` events for that exact issue.
3. Inspect the corresponding projection payload for evidence categories, runtime targets, and advisory outputs.

## 8. Summary

- `CopilotAdapter.build_copilot_context(...)` is active and using PECS-LITE.
- Evidence is loaded from existing `.pecs` artifacts.
- The current mode is advisory and not enforcement.
- Exact issue-specific telemetry for the requested audit names is absent in the current workspace.
- The available data supports a general Copilot-PECS reliance conclusion, but not a definitive issue-name-specific proof.
