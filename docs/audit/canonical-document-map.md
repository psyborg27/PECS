# Canonical Document Map — PECS Core v1 Alpha 1

This map identifies the single authoritative document for each topic. Where multiple documents cover the same topic, one is promoted to canonical and the others are either merged, archived, or deprecated.

---

## Topic-to-Canonical-Source Map

| Topic | Canonical Document | Supersedes / Notes |
|---|---|---|
| **Project overview** | `README.md` (rewritten) | Supersedes the previous 780-line README |
| **Architecture (high-level)** | `docs/architecture.md` | Condensed, navigable overview with data flow |
| **Architecture (implementation-level)** | `PECS_ARCHITECTURE_BASELINE.md` → `docs/reference/architecture-baseline.md` | Most detailed spec with file paths and class names |
| **Design principles** | `docs/design-principles.md` | Standalone — no other doc overlaps |
| **Workspace Graph** | `docs/workspace-graph.md` | → `docs/reference/workspace-graph.md` |
| **Workspace Registry** | `docs/workspace-registry.md` | → `docs/reference/workspace-registry.md` |
| **Evidence Correlation** | `docs/evidence-correlation.md` | → `docs/reference/evidence-correlation.md` |
| **Navigation Builder** | `docs/navigation-builder.md` | → `docs/reference/navigation-builder.md` |
| **Query Pipeline** | `docs/query-pipeline.md` | → `docs/reference/query-pipeline.md` |
| **Projection spec** | `PECS_ARCHITECTURAL_PROJECTION_SPEC.md` → `docs/reference/projection-spec.md` | Canonical for profiles and wire format |
| **Query contract** | Consolidate: `PECS_CANONICAL_QUERY_AND_PROJECTION_CONTRACT.md` + `PECS_QUERY_CONTRACT.md` → `docs/contracts/query-contract.md` | Abstract contract + concrete payload shapes → one merged document |
| **Projection contract** | Extract from `PECS_ARCHITECTURAL_PROJECTION_SPEC.md` → `docs/contracts/projection-contract.md` | Separate from query contract since they address different concerns |
| **Consumer authority model** | `README.md` (Authority Model section) | Supersedes `PECS_CONSUMER_AUTHORITY_MODEL.md` |
| **Consumer observability** | `docs/troubleshooting.md` + extract from `PECS_CONSUMER_OBSERVABILITY_CONTRACT.md` → `docs/runtime/observability.md` | Merge relevant observability contract details into runtime docs |
| **Consultation policy** | `PECS_CONSULTATION_POLICY.md` → `docs/reference/` | Keep as-is, just move |
| **Installation** | `docs/installation.md` | Supersedes duplications in old README |
| **Getting started** | `docs/getting-started.md` | |
| **Troubleshooting** | `docs/troubleshooting.md` | |
| **Artifact catalog** | `docs/artifacts.md` | |
| **Glossary** | `docs/glossary.md` | |
| **Roadmap** | `docs/roadmap.md` | Keep, though some content overlaps with CHANGELOG |
| **Changelog** | `CHANGELOG.md` → `docs/developer/changelog.md` | |
| **Agent instructions** | `AGENTS.md` → `docs/developer/agents.md` | |
| **Developer guide** | `docs/developer-guide.md` | **Must be restored** — currently corrupted with Auto-TOC content |
| **Copilot integration** | `docs/integrations/copilot.md` | |
| **Continue integration** | `docs/integrations/continue.md` | |
| **Kimi integration** | `docs/integrations/kimi.md` | |
| **Command Code integration** | `docs/integrations/commandcode.md` | |
| **PECS-LITE integration** | `docs/integrations/pecs-lite.md` | |
| **Installer implementation** | `workspace_assets/IMPLEMENTATION_SUMMARY.md` → `docs/installer/implementation-summary.md` | |
| **Workspace integration** | `workspace_assets/README_WORKSPACE_INTEGRATION.md` → `docs/installer/workspace-integration.md` | |
| **Workspace preparation** | `workspace_assets/README_WORKSPACE_PREPARATION.md` → `docs/installer/workspace-preparation.md` | |
| **Workspace bootstrap** | `workspace_assets/WORKSPACE_BOOTSTRAP.md` → `docs/installer/workspace-bootstrap.md` | |

---

## Documents to Archive (Superseded or Obsolete)

| Document | Reason | Target |
|---|---|---|
| `PECS_AUTHORITY_ENGINE_ARCHITECTURE.md` | Never implemented; describes architecture that doesn't exist in code | `docs/archive/obsolete-designs/` |
| `PECS_FILE_CLASS_FUNCTION_RESOLUTION_DESIGN.md` | Design differs from implemented `LineRangeResolver` | `docs/archive/obsolete-designs/` |
| `PECS_OBJECT_ID_PRODUCER_DESIGN.md` | PECS_ID scheme now embedded in runtime scanner | `docs/archive/obsolete-designs/` |
| `PECS_CANONICAL_QUERY_AND_PROJECTION_CONTRACT.md` | Content absorbed into consolidated contracts | `docs/archive/obsolete-contracts/` |
| `PECS_QUERY_CONTRACT.md` | Content absorbed into consolidated contracts | `docs/archive/obsolete-contracts/` |
| `PECS_CONSUMER_AUTHORITY_MODEL.md` | Content absorbed into README authority model section | `docs/archive/obsolete-contracts/` |
| `PECS_LITE v2/COMPRESSED CONTEXT SNAPSHOT.md` | PECS-LITE is now stateless and query-driven only | `docs/archive/` |
| `PECS_LITE v2/pecs_lite v2/README.md` | Same reason | `docs/archive/` |

---

## Documents to Keep as Root Documents

After the reorganization, the following should remain at root level:

| Document | Rationale |
|---|---|
| `README.md` | Repository entry point — required by every repository |
| `LICENSE` | Legal requirement (create if missing) |
| `CONTRIBUTING.md` | Standard practice (create if desired) |
| `CHANGELOG.md` | Often expected at root. Can move to `docs/developer/changelog.md` |
| `AGENTS.md` | AI agent instructions are repo-entry-point relevant. Can move to `docs/developer/agents.md` |

All `PECS_*.md` specification documents should move to `docs/reference/` or `docs/archive/`.
