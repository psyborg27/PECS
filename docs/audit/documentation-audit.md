# Documentation Audit — PECS Core v1 Alpha 1

## Method

Every markdown file in the repository was catalogued (129 files total). Each was examined for:
- Content scope and purpose
- Overlap with other documents
- Accuracy relative to current implementation
- Whether it is still relevant or should be archived
- Whether it is the canonical source for its topic

## Classification Legend

| Classification | Meaning |
|---|---|
| **Canonical** | The authoritative source for its topic; should remain at its current location |
| **Partially Superseded** | Some content remains valid but is partially covered by a newer document |
| **Superseded** | Fully replaced by a newer document; should be archived |
| **Duplicate** | Content overlaps substantially with another document |
| **Obsolete** | Describes removed features, old architecture, or deprecated workflows |
| **Workspace-specific** | Document refers to a specific workspace (Auto-TOC, etc.) and should not be in the PECS repo |

---

## Root Documents

| File | Size | Classification | Notes |
|---|---|---|---|
| `README.md` | 27.1 KB | **Canonical (needs rewrite)** | Was heavily duplicated (branch warnings, disclaimer duplications, scattered install instructions). Rewritten for Alpha 1. |
| `AGENTS.md` | 19.2 KB | **Canonical** | Agent-facing repo guide. Accurate, well-structured, covers repo layout, build/test workflow, code conventions. |
| `CHANGELOG.md` | 4.0 KB | **Canonical** | Release notes. Accurately describes what Alpha 1 delivers. |
| `PECS_ARCHITECTURE_BASELINE.md` | 14.3 KB | **Canonical** | Most detailed implementation-level architecture spec. Provides exact file paths and class names for every component. |
| `PECS_ARCHITECTURAL_PROJECTION_SPEC.md` | 15.9 KB | **Partially Superseded** | Defines CLI-to-consumer wire format. Some content overlaps with PECS_QUERY_CONTRACT.md and PECS_CANONICAL_QUERY.md. Should be canonical for projection profiles only. |
| `PECS_AUTHORITY_ENGINE_ARCHITECTURE.md` | 13.5 KB | **Obsolete** | Describes an authority engine architecture that was never implemented or was superseded by the current PECS-PRO authority model. |
| `PECS_CANONICAL_QUERY_AND_PROJECTION_CONTRACT.md` | 13.8 KB | **Partially Superseded** | Abstract, consumer-agnostic contract. Overlaps significantly with PECS_QUERY_CONTRACT.md and PECS_ARCHITECTURAL_PROJECTION_SPEC.md. |
| `PECS_CONSULTATION_POLICY.md` | 2.7 KB | **Partially Superseded** | Policy document about mandatory query / optional reliance. Relevant but not referenced by any implementation. |
| `PECS_CONSUMER_AUTHORITY_MODEL.md` | 4.7 KB | **Partially Superseded** | Describes consumer authority boundaries. Largely covered by PECS_ARCHITECTURE_BASELINE.md and the README. |
| `PECS_CONSUMER_OBSERVABILITY_CONTRACT.md` | 10.5 KB | **Partially Superseded** | Describes observability contracts for consumers. Contains valuable details but overlaps with troubleshooting docs. |
| `PECS_FILE_CLASS_FUNCTION_RESOLUTION_DESIGN.md` | 10.9 KB | **Obsolete** | Design document for file/class/function resolution. The actual implementation (LineRangeResolver in navigation_builder/) differs. |
| `PECS_OBJECT_ID_PRODUCER_DESIGN.md` | 9.8 KB | **Obsolete** | Design document for PECS_ID generation. The object_id scheme is now embedded in the runtime/workspace scanner. |
| `PECS_QUERY_CONTRACT.md` | 13.2 KB | **Partially Superseded** | More concrete consumer-facing contract. Overlaps with PECS_CANONICAL_QUERY.md and the projection spec. Defines actual JSON payload shapes. |
| `README_MANUAL_SETUP.md` | 12.1 KB | **Partially Superseded** | Manual setup procedures. Much of this is now covered by `docs/installation.md` and the README. |

---

## `docs/` Directory

| File | Size | Classification | Notes |
|---|---|---|---|
| `architecture.md` | 5.8 KB | **Canonical** | Concise, accurate architecture overview with data flow diagram. References component-specific docs. Good entry point. |
| `artifacts.md` | 3.3 KB | **Canonical** | Complete catalog of generated artifacts. Accurate. |
| `design-principles.md` | 2.9 KB | **Canonical** | Standalone principles document. Accurate, no overlap. Referenced by multiple other docs. |
| `developer-guide.md` | 4.5 KB | **Corrupted / Workspace-specific** | Contains Auto-TOC workspace paths (`/Users/raj/Downloads/auto OCR app`), Auto-TOC-specific rules about Qt, signals, and wiring. This is NOT the PECS developer guide — it was overwritten with workspace-specific coding instructions for Auto-TOC. **Must be restored.** |
| `evidence-correlation.md` | 2.9 KB | **Canonical** | Accurate description of Evidence Correlation Engine with evidence source table. Matches implementation. |
| `getting-started.md` | 2.5 KB | **Canonical** | Good first-time user guide. Accurate workflows. |
| `glossary.md` | 3.5 KB | **Canonical** | Accurate definitions. No stale entries. |
| `installation.md` | 2.1 KB | **Canonical** | Accurate installation guide. |
| `navigation-builder.md` | 1.6 KB | **Canonical** | Accurate. Matches implementation. |
| `query-pipeline.md` | 3.7 KB | **Canonical** | Accurate CLI and contract description. |
| `roadmap.md` | 5.3 KB | **Partially Superseded** | Contains the recommendation to standardize around runtime projection. The roadmap content is strategic analysis more than a release plan. Some content overlaps with CHANGELOG.md. |
| `troubleshooting.md` | 3.8 KB | **Canonical** | Accurate troubleshooting guide. |
| `workspace-graph.md` | 2.6 KB | **Canonical** | Accurate. Lists all node types, edge types, authority levels, edge directions. Matches `execution_graph/graph/workspace_graph.py`. |
| `workspace-registry.md` | 2.3 KB | **Canonical** | Accurate. Matches `workspace_registry/models.py`. |

---

## `docs/integrations/` Directory

| File | Size | Classification | Notes |
|---|---|---|---|
| `commandcode.md` | 1.6 KB | **Canonical** | Accurate. |
| `continue.md` | 5.6 KB | **Canonical** | Accurate. |
| `copilot.md` | 5.2 KB | **Canonical** | Accurate. |
| `kimi.md` | 5.5 KB | **Canonical** | Accurate. |
| `pecs-lite.md` | 2.5 KB | **Canonical** | Accurate. |

---

## `docs/archive/` Directory — 70 Files

All 70 files in `docs/archive/` are **historical reports, audit findings, analysis documents, and design traces** from the development process. They are classified into:

### Group A: Project-Specific Reports (28 files)
One-off reports about specific implementation audits, gap analysis, or validation results.
**Examples:** `PECS_DESIGN_VALIDATION_REPORT.md`, `PECS_EVIDENCE_FLOW_AUDIT.md`, `PECS_INSTALLER_AUDIT.md`, `VALIDATION_HARDENING_REPORT.md`

### Group B: Obsolete Architecture/Design (15 files)
Documents describing architectures, contracts, or designs that were never implemented or were superseded.
**Examples:** `PECS_AUTHORITY_CONTRIBUTION_ANALYSIS.md`, `PECS_OBJECT_GROUP_AUTHORITY_VALIDATION.md`, `PECS_LITE_ROLE_ANALYSIS.md`

### Group C: Continuity Extraction Traces (8 files)
Step-by-step traces of continuity extraction experiments.
**Examples:** `CONTINUITY_EXTRACTION_EXECUTION_TRACE.md`, `CURRENT_CONTINUITY_LIFECYCLE_TRACE.md`, `DOWNSTREAM_PROPAGATION_TRACE.md`

### Group D: Auto-TOC Specific (2 files)
Documents specifically about Auto-TOC migration.
**Examples:** `AUTO_TOC_INCREMENTAL_UPGRADE_PLAN.md`, `AUTO_TOC_UPGRADE_IMPACT_REPORT.md`

### Group E: Duplicate/Redundant (5 files)
Multiple versions of similar reports.
**Examples:** `DETERMINISM_AUDIT_REPORT.md`, `DETERMINISM_ENFORCEMENT_REPORT.md`, `DETERMINISM_HARDENING_REPORT.md`

### Group F: Stale Operation Docs (12 files)
Outdated operational guidance superseded by current implementation.
**Examples:** `DAEMON_AUTOMATION_ANALYSIS.md`, `DAEMON_LOGGING_REPORT.md`, `LOGGING_IMPLEMENTATION_REPORT.md`

**Verdict on archive/:** These files serve as development history. They do NOT need to be deleted — they are already in `docs/archive/`. However, they should be conceptually organized into subdirectories to make navigation manageable.

---

## `docs/archive/status/` Directory — 5 Files

Status reports from specific points in development. **All are stale/obsolete** — they describe states that no longer match the current implementation:

| File | Classification |
|---|---|
| `ARCHITECTURAL_DRIFT_REPORT.md` | **Obsolete** |
| `DAEMON_REPAIR_REPORT.md` | **Obsolete** |
| `FINAL_DEPLOYMENT_ACCOUNTABILITY_REPORT_2026-05-19.md` | **Obsolete** |
| `RESTORED_CONTINUITY_REPORT.md` | **Obsolete** |
| `TOPOLOGY_INTEGRITY_REPORT.md` | **Obsolete** |

---

## `workspace_assets/` Directory

| File | Classification | Notes |
|---|---|---|
| `IMPLEMENTATION_SUMMARY.md` | **Canonical** | Ingress implementation overview. |
| `README_WORKSPACE_INTEGRATION.md` | **Canonical** | Installed asset list and rules. |
| `README_WORKSPACE_PREPARATION.md` | **Canonical** | Workspace preparation guide. |
| `WORKSPACE_BOOTSTRAP.md` | **Canonical** | Bootstrap checkpoint. |

---

## `PECS_LITE v2/` Directory

| File | Classification | Notes |
|---|---|---|
| `COMPRESSED CONTEXT SNAPSHOT.md` | **Obsolete** | Describes the old PECS-LITE daemon architecture. PECS-LITE is now stateless and query-driven only. |
| `pecs_lite v2/README.md` | **Obsolete** | README for the old PECS-LITE v2 implementation. |

---

## Summary

| Classification | Count |
|---|---|
| **Canonical** | 32 |
| **Partially Superseded** | 9 |
| **Obsolete** | 11 |
| **Corrupted/Workspace-specific** | 1 (docs/developer-guide.md) |
| **Archive (historical, already in archive/)** | 75 |

**Critical issues:**
1. `docs/developer-guide.md` is corrupted with Auto-TOC workspace content
2. Three root-level contract documents overlap significantly
3. `PECS_AUTHORITY_ENGINE_ARCHITECTURE.md` and `PECS_OBJECT_ID_PRODUCER_DESIGN.md` describe architectures that don't match current code
4. `PECS_FILE_CLASS_FUNCTION_RESOLUTION_DESIGN.md` describes a design that differs from the implemented `LineRangeResolver`
