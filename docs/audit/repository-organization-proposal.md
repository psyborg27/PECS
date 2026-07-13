# Repository Organization Proposal — PECS Core v1 Alpha 1

## Proposed Documentation Layout

```
docs/
├── index.md                          # Documentation landing page with topic map
├── getting-started.md                # First-time user guide (keep)
├── installation.md                   # Installation guide (keep)
├── architecture.md                   # High-level architecture overview (keep)
├── design-principles.md              # Design principles (keep)
├── glossary.md                       # Terminology (keep)
├── troubleshooting.md                # Operational guide (keep)
├── artifacts.md                      # Generated artifact catalog (keep)
├── roadmap.md                        # Future direction (keep)
│
├── reference/                         # Implementation-level specs
│   ├── workspace-graph.md            # Keep, move from docs/
│   ├── workspace-registry.md         # Keep, move from docs/
│   ├── evidence-correlation.md       # Keep, move from docs/
│   ├── navigation-builder.md         # Keep, move from docs/
│   ├── query-pipeline.md             # Keep, move from docs/
│   └── projection-spec.md            # Canonical projection spec (from root PECS_ARCHITECTURAL_PROJECTION_SPEC.md)
│
├── contracts/                         # Query and projection contracts
│   ├── query-contract.md             # Canonical query response contract
│   └── projection-contract.md        # Canonical projection contract
│
├── integration/                       # Consumer-specific guides
│   ├── copilot.md                    # Keep from docs/integrations/
│   ├── continue.md                   # Keep from docs/integrations/
│   ├── kimi.md                       # Keep from docs/integrations/
│   ├── commandcode.md                # Keep from docs/integrations/
│   └── pecs-lite.md                  # Keep from docs/integrations/
│
├── runtime/                           # Daemon and runtime architecture
│   ├── daemon-architecture.md        # Extract from baseline
│   ├── runtime-trigger-chain.md      # Extract from baseline/troubleshooting
│   └── observability.md              # Extract from troubleshooting + consumer observability contract
│
├── developer/                         # Developer-facing guides
│   ├── developer-guide.md            # RESTORED: PECS developer guide (currently corrupted)
│   ├── agents.md                     # Move AGENTS.md here
│   └── changelog.md                  # Move CHANGELOG.md here
│
├── installer/                         # Installer design and behavior
│   ├── workspace-integration.md      # Keep from workspace_assets/
│   ├── workspace-preparation.md      # Keep from workspace_assets/
│   ├── workspace-bootstrap.md        # Keep from workspace_assets/
│   └── implementation-summary.md     # Keep from workspace_assets/
│
├── workspace-assets/                  # Installed assets catalog
│   └── assets-manifest.md            # Document the manifest
│
├── archive/                           # Historical documents
│   ├── reports/                      # One-off audit/analysis/report documents
│   │   ├── PECS_DESIGN_VALIDATION_REPORT.md
│   │   ├── PECS_INSTALLER_AUDIT.md
│   │   └── ... (28+ report files)
│   ├── obsolete-designs/             # Designs that were never implemented
│   │   ├── PECS_AUTHORITY_ENGINE_ARCHITECTURE.md
│   │   ├── PECS_OBJECT_ID_PRODUCER_DESIGN.md
│   │   ├── PECS_FILE_CLASS_FUNCTION_RESOLUTION_DESIGN.md
│   │   └── ... (15+ design files)
│   ├── traces/                       # Continuity extraction traces
│   │   ├── CONTINUITY_EXTRACTION_EXECUTION_TRACE.md
│   │   ├── CURRENT_CONTINUITY_LIFECYCLE_TRACE.md
│   │   └── ... (8 trace files)
│   ├── obsolete-contracts/           # Superseded contract documents
│   │   ├── PECS_CANONICAL_QUERY_AND_PROJECTION_CONTRACT.md
│   │   ├── PECS_QUERY_CONTRACT.md
│   │   └── PECS_CONSUMER_AUTHORITY_MODEL.md
│   ├── status/                       # Stale status reports (keep as-is)
│   │   └── ... (5 files)
│   └── PECS_LITE_README.md           # From PECS_LITE v2/READ.md (obsolete)
│
└── audit/                             # Audit deliverables (this work package)
    ├── documentation-audit.md
    ├── repository-organization-proposal.md
    ├── canonical-document-map.md
    ├── consistency-audit.md
    └── alpha-1-readiness.md
```

## Root Documents to Move or Promote

| Current Location | Proposed Location | Reason |
|---|---|---|
| `AGENTS.md` | `docs/developer/agents.md` | Agent-facing docs belong in developer/ |
| `CHANGELOG.md` | `docs/developer/changelog.md` | Release notes belong in developer/ |
| `PECS_ARCHITECTURE_BASELINE.md` | `docs/reference/architecture-baseline.md` | Implementation-level spec belongs in reference/ |
| `PECS_ARCHITECTURAL_PROJECTION_SPEC.md` | `docs/reference/projection-spec.md` | Projection spec belongs in reference/ |
| `PECS_AUTHORITY_ENGINE_ARCHITECTURE.md` | `docs/archive/obsolete-designs/` | Describes unimplemented architecture |
| `PECS_CANONICAL_QUERY_AND_PROJECTION_CONTRACT.md` | Consolidate into `docs/contracts/` | Merge with PECS_QUERY_CONTRACT.md |
| `PECS_CONSULTATION_POLICY.md` | `docs/reference/` | Keep but move |
| `PECS_CONSUMER_AUTHORITY_MODEL.md` | `docs/archive/obsolete-contracts/` | Superseded by query contract |
| `PECS_CONSUMER_OBSERVABILITY_CONTRACT.md` | `docs/runtime/observability.md` | Merge into runtime observability guide |
| `PECS_FILE_CLASS_FUNCTION_RESOLUTION_DESIGN.md` | `docs/archive/obsolete-designs/` | Never implemented as designed |
| `PECS_OBJECT_ID_PRODUCER_DESIGN.md` | `docs/archive/obsolete-designs/` | Never implemented as designed |
| `PECS_QUERY_CONTRACT.md` | Consolidate into `docs/contracts/` | Merge with canonical query contract |
| `README_MANUAL_SETUP.md` | `docs/installer/manual-setup.md` | Installer detail belongs in installer/ |

## Workspace Assets to Move

| Current Location | Proposed Location |
|---|---|
| `workspace_assets/IMPLEMENTATION_SUMMARY.md` | `docs/installer/implementation-summary.md` (or keep in workspace_assets/) |
| `workspace_assets/README_WORKSPACE_INTEGRATION.md` | `docs/installer/workspace-integration.md` |
| `workspace_assets/README_WORKSPACE_PREPARATION.md` | `docs/installer/workspace-preparation.md` |
| `workspace_assets/WORKSPACE_BOOTSTRAP.md` | `docs/installer/workspace-bootstrap.md` |

## Immediate Actions (No Move Required)

| Action | Target |
|---|---|
| **Restore** `docs/developer-guide.md` | Currently contains Auto-TOC workspace content, not PECS developer guide |
| **Consolidate** root contract docs | Merge PECS_CANONICAL_QUERY.md + PECS_QUERY_CONTRACT.md into one canonical contract document |
| **Archive** `PECS_AUTHORITY_ENGINE_ARCHITECTURE.md` | Obsolete — move to docs/archive/obsolete-designs/ |
| **Archive** `PECS_FILE_CLASS_FUNCTION_RESOLUTION_DESIGN.md` | Obsolete — move to docs/archive/obsolete-designs/ |
| **Archive** `PECS_OBJECT_ID_PRODUCER_DESIGN.md` | Obsolete — move to docs/archive/obsolete-designs/ |
| **Archive** `PECS_LITE v2/COMPRESSED CONTEXT SNAPSHOT.md` | Obsolete — move to archive |
| **Archive** `PECS_LITE v2/pecs_lite v2/README.md` | Obsolete — move to archive |

## Structural Principles

1. **`docs/reference/`** holds implementation-level specifications that correspond directly to code packages
2. **`docs/contracts/`** holds query and projection contract definitions (consumers, not implementation)
3. **`docs/integration/`** holds consumer-specific setup guides (already in `docs/integrations/`)
4. **`docs/runtime/`** holds daemon, trigger chain, and observability documentation
5. **`docs/developer/`** holds contributor-facing guides (agents, changelog, developer guide)
6. **`docs/installer/`** holds installer design and workspace preparation guides
7. **Root-level `PECS_*.md` files** should be reduced to only canonical contract/spec documents
8. **Root-level README** is the authoritative entry point — everything else is one click away
