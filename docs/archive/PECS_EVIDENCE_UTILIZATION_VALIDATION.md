# PECS Evidence Utilization Validation

## Purpose
Validate whether current PECS evidence is actively consumed during retrieval and projection generation in the existing implementation.
This audit is limited to current code and saved live query outputs. No redesign or implementation changes are proposed.

## 1. Current Retrieval Flow

### Consumer Query
- `CopilotAdapter.build_copilot_context(object_id, ...)`
- Query text is derived from `object_id` and passed as `issue_query`.
- Copilot emits a runtime event `copilot_query_received`.

### PECS Query Processing
- `CopilotAdapter` calls `PECSLiteRuntimeAdapter.build_projection_safe(...)`.
- That calls `PECSLiteRuntimeAdapter.build_projection(...)`.
- The `PECSLiteRuntimeV2` runtime is instantiated from `PECS_LITE v2/pecs_lite v2/pecs_lite_runtime/pecs_lite_runtime_v2.py`.
- `PECSLiteRuntimeV2.build_projection(...)` performs:
  - runtime context resolution (`RuntimeContextResolver.resolve()`)
  - adapter refresh (`self.adapter.refresh()`)
  - capability classification via `CapabilityClassifier.classify(...)`

### Evidence Retrieval
- Evidence is loaded by `PECSProQueryAdapter._load_artifacts()`:
  - `.pecs/active_context.json`
  - `.pecs/compact_bundle.json`
  - `.pecs/locality_index.json`
  - `.pecs/topology_compact.json`
  - `.pecs/continuity/locality_state.json`
  - `.pecs/continuity/active_topology.json`
  - `.pecs/continuity/engineering_continuity_state.json`

- The adapter retrieves evidence with these methods:
  - `runtime_target_candidates()`
  - `runtime_zone_lookup()`
  - `ownership_locality_lookup()`
  - `wrapper_warning_lookup()`
  - `active_continuity_lookup()`
  - `engineering_continuity_lookup(issue_query, max_chains=4)`
  - `evidence_fusion_lookup(max_files=128)`

### Authority Formation
- `evidence_fusion_lookup(...)` computes a fused score per file using:
  - `tier_0_static`
  - `tier_1_runtime`
  - `tier_2_continuity`
  - `tier_3_validation`
- It uses:
  - `active_context.activated_objects`
  - `locality_state.active_runtime_touched_files`
  - topology edges and object-file map
  - `engineering_continuity_lookup(...)` scores and chains
  - ownership locality and continuity cluster data

### Projection Generation
- `ProjectionHardener.harden_projection(...)`:
  - scores and sorts raw target candidates
  - selects primary runtime targets and secondary neighbors
  - injects accepted continuity anchors from `accepted_locality_scores`
  - enforces token budgeting and projection limits

- `ProjectionExporter.export_projection(...)` builds final output with:
  - `runtime_targets`
  - `secondary_neighbors`
  - `evidence_fusion`
  - `engineering_continuity_summary`
  - `active_engineering_continuity`
  - `pecs_lite_status`
  - `pecs_runtime_report`
  - advisory cognition / shaping envelopes
  - diagnostics and artifact provenance

### Consumer Response
- `CopilotAdapter.build_copilot_context(...)` returns:
  - `projection`
  - `emitted_advisory_cognition`
  - `discarded_cognition_summary`
  - `shaping_losses`
  - `final_emission_observability`
  - `consumption_boundary`
- If projection generation fails, a fallback minimal topology context may be returned.

## 2. Evidence Category Utilization

| Evidence Category | Collected | Stored | Retrieved | Consumed | Contributes to Final Projection |
|---|---|---|---|---|---|
| AI edit history | yes | yes (`.pecs/ai_chat_history.json` → continuity export) | yes via `engineering_continuity_state.json` | partial | yes, mainly in continuity summary and chain-based continuity scoring |
| User acceptance history | yes | yes (`validation_accept_count`, `accepted_locality_scores`) | yes | yes | yes, as evidence_fusion tier 3 and accepted continuity anchors |
| User rejection history | yes | yes (`validation_reject_count`, `rejected_locality_scores`) | yes | yes | yes, as penalty in candidate scoring and advisory signals |
| Runtime authority evidence | yes | yes (`active_context`, `locality_state`, `topology_compact`) | yes | yes | yes, core to candidate ranking and runtime target selection |
| Ownership authority evidence | yes | yes (`ownership_hotspots`, ownership locality data) | yes | yes | yes, in evidence_fusion tier 2 and target metadata |
| Historical authority evidence | yes | yes (`engineering_continuity_state.json`, cluster metrics) | yes | yes | yes, especially in continuity summary and advisory outputs |
| Locality authority evidence | yes | yes (`topology_compact`, `locality_index`, `active_context`) | yes | yes | yes, primary source for targets and adjacency selection |
| Divergence evidence | yes | yes (continuity chain suspicion fields) | yes | yes | partial; mainly advisory outputs and search-expansion heuristics |
| Continuity evidence | yes | yes (`.pecs/continuity/*`) | yes | yes | yes, broad projection metadata, certainty scoring, advisory outputs |

### Notes
- `AI edit history` is stored and read, but its direct influence is mediated through the continuity export chain logic.
- `Divergence evidence` is present and used mainly in advisory/reconciliation output rather than raw target selection.
- `Locality authority` and `runtime authority` are the strongest active consumers.

## 3. Evidence Influence by Projection Output

| Projection Component | Evidence Influencing It |
|---|---|
| candidate ranking | runtime authority, locality authority, ownership authority, historical authority, user acceptance/rejection, continuity evidence |
| runtime targets | raw runtime target candidates, evidence fusion scores, accepted continuity anchors, locality proximity |
| secondary targets | runtime neighborhood adjacency, evidence_fusion ranked files, proximity constraints, profile budget |
| advisory outputs | divergence evidence, continuity survivability, authority concentration, wrapper_warning, historical authority, continuity chains |
| engineering continuity | continuity export chains, accepted/rejected locality scores, continuity confidence metrics, chain suspicion fields |
| final projection | combined runtime targets, secondary neighbors, evidence_fusion, engineering_continuity_summary, active_engineering_continuity, pecs_lite_status, advisory cognition |

## 4. Statement Assessment

> “PECS currently collects substantially more evidence than it actually uses during authority formation and retrieval.”

- Assessment: **TRUE**
- Justification:
  - The current implementation loads broad continuity and chat-derived evidence from `.pecs/continuity/engineering_continuity_state.json` and related artifacts.
  - In practice, many continuity chain details are filtered by `issue_query` and do not surface in `active_engineering_continuity`.
  - The live query outputs show top-ranked candidates with many files scored mostly by `tier_0_static` and a small number with continuity/validation contributions.
  - Stored history is richer than the final projection uses, especially for chat-derived chains and conversation metadata.

## 5. Simulation Reports

### A. Notes Module Clipboard Issue

- **Current saved query**: `Clipboard paste not working in Notes Module.`
- **Evidence Retrieved**:
  - runtime targets from `runtime_target_candidates()`
  - runtime adjacency from `topology_compact` and active runtime neighborhood
  - evidence fusion from `evidence_fusion_lookup()` using runtime activation, touched files, topology edges, continuity lookup, and validation scores
  - ownership locality from `ownership_locality_lookup()`
  - continuity metrics from `active_continuity_lookup()` and `engineering_continuity_lookup()`
- **Evidence Used**:
  - candidate ranking uses `tier_2_continuity` and `tier_3_validation` for top files
  - raw runtime targets were drawn from runtime interaction and evidence fusion
  - continuity summary and `active_engineering_continuity` are built from retrieved continuity state
  - advisory logic uses divergence and continuity scores
- **Evidence Ignored**:
  - raw chat transcript details from `ai_chat_history.json` are not exposed directly
  - several continuity chain fields are not included because `active_engineering_continuity` showed no matching high-confidence chain for this query
  - `runtime_neighbors` are empty, indicating no additional adjacency beyond the primary target set
- **Final Projection**:
  - `runtime_targets_small` contains `install_workspace_integration.py`, `workspace_bridge_cli.py`, `Qt/auto_toc_dialog_rewrite.py`, `EnhancedPDFViewer.py`, `Qt/__init__.py`, `Qt/auto_toc_dialog_rewrite_next.py`
  - `runtime_neighbors` is empty
  - `evidence_fusion` top file is `install_workspace_integration.py` with tier scores from continuity and validation
  - `engineering_continuity` is empty for the active chain view, but `active_continuity` is present
  - projection includes `continuity_supporting_artifacts` and `pecs_lite_status`

### B. Send Annotation To Note failure

- **Exact current saved query not found** in the available live outputs.
- The current implementation would process this issue via the same flow:
  - query text enters `PECSLiteRuntimeV2.build_projection(...)`
  - evidence is loaded from the same `.pecs` artifacts
  - `evidence_fusion_lookup()` and `engineering_continuity_lookup()` are executed
  - projection is hardened and exported in the same way
- **Closest current saved query**: `Cmd+A selects all notes instead of all text in active frame.`
- For that saved query, evidence retrieved and consumed matched the same pattern as case A.
- Since the implementation is query-driven and stateless, a `Send Annotation To Note` style query would use the same evidence categories.

### C. OCR Tabs malfunction

- **Exact current saved query not found** in the available live outputs.
- The current implementation would still use the exact same retrieval and projection path.
- **Closest current saved query**: `Notes Module modularization and ownership extraction.`
- That query likewise returned the same evidence categories:
  - runtime candidate list,
  - evidence fusion tier scores,
  - active continuity metadata,
  - projection diagnostics.
- The exact issue label is not present, but the current code path is identical.

## 6. Projection Sufficiency for Copilot

- Answer: **PARTIAL**
- Justification:
  - Current projections contain structured evidence, tiered scores, continuity artifact provenance, and advisory guidance.
  - However, the saved projections show that issue-specific continuity chain anchors are sparse and many top-ranked targets rely on static/topology evidence.
  - That means the projection is useful for guiding PECS-aware locality, but not yet decisively strong enough to completely replace broad grep/search in all cases.

## 7. Key Findings

- PECS evidence is actively consumed in the current retrieval path.
- Runtime authority and locality authority are the dominant active contributors.
- Continuity evidence is present and used, but much of the stored continuity/chat-derived detail is not fully exposed in final projection payloads.
- User acceptance/rejection history is read and used, but it is a secondary influence compared to runtime/locality evidence.
- Stored evidence exceeds what is directly used during scoring and projection, supporting the assessment that the system currently collects more evidence than it fully consumes.
