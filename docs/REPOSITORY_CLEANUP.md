# PECS Repository Cleanup Report

This report identifies documentation candidates for cleanup, archival, and canonical consolidation. It does not modify any files.

## Obsolete Documents

The following documents appear to be legacy, duplicate, or purposefully archival and should not be used as current Alpha 1 references:

- `MANUAL.md` — broad manual guidance that overlaps `README.md` and `getting-started.md`.
- `README_ALPHA1.md` — duplicate Alpha 1 overview content now captured in `README.md` and `docs/index.md`.
- `WORKFLOW_ALPHA1.md` — duplicate workflow guidance now captured in `docs/WORKFLOW.md`.
- `README_COMPAT.md` — compatibility notes are useful but should be referenced from `docs/index.md` rather than treated as a primary doc.

## Duplicate Documents

- `docs/INSTALLATION.md` and `installation.md` cover similar installation material; one should be canonical.
- `docs/UPGRADE.md` and `UPGRADE.md` are duplicates in separate locations.
- `docs/WORKFLOW.md` and `WORKFLOW.md` are duplicates in separate locations.
- `docs/ARCHITECTURE.md` and `architecture.md` are duplicates in separate locations.

## Candidate Archive Files

The following files are candidates for archive or flagging if they are not part of the current Alpha 1 documentation set:

- `docs/archive/` — archival reports and design traces.
- `docs/audit/` — audit and documentation analysis reports.
- `docs/contracts/` — contract drafts and canonical maps.
- `workspace_assets/README_WORKSPACE_INTEGRATION.md` — workspace asset install guide that may be duplicated by current `docs/INSTALLATION.md`.

## Deprecated Documents

- `README_ALPHA1.md` — duplicate of the primary README.
- `WORKFLOW_ALPHA1.md` — duplicate of the workflow documentation.

## Documents That Should Become Canonical

- `docs/index.md` — new documentation landing page.
- `README.md` — primary repository entry point.
- `docs/ARCHITECTURE.md` — primary architecture reference.
- `docs/INSTALLATION.md` — canonical installation procedure.
- `docs/UPGRADE.md` — canonical upgrade guidance.
- `docs/WORKFLOW.md` — canonical workflow reference.
- `docs/LEGAL.md` — canonical legal notice.
- `docs/CONFIGURATION.md` — canonical configuration reference.
- `docs/OUTPUTS.md` — canonical artifact reference.
- `docs/FINALIZATION.md` — canonical release checklist.
- `docs/FAQ.md` — canonical FAQ.
- `docs/MAN_PAGES.md` — canonical CLI reference.

## Recommended Future Documentation Organization

- Keep top-level `README.md` concise and linked to detailed docs in `docs/`.
- Prefer `docs/` as the canonical documentation root.
- Retain `docs/archive/` and `docs/audit/` as archival history, but clearly label them as non-current.
- Use `docs/index.md` to keep the documentation structure discoverable.
- Avoid duplicate docs in both the repository root and `docs/` unless one is an archive.

## Notes

This cleanup assessment is informational only. No files were deleted or moved.
