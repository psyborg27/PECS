# Architectural Drift Report

Date: 2026-05-19
Workspace: /Users/raj/Developer/PECS

## Scope
Audit focused on PECS runtime retrieval, daemon lifecycle, adapters, and chat-history continuity integration.

## Drift Findings

1. Governance-style hard failures in retrieval pipeline
- File: topology/retrieval/topology_retriever.py
- Behavior before repair: strict/enforced retrieval raised exceptions for weak or missing anchors.
- Why drift: this turned continuity telemetry into control/gating behavior.

2. Integration adapters forcing strict retrieval
- Files: integrations/copilot_adapter.py, integrations/continue_adapter.py
- Behavior before repair: both adapters hardcoded enforce=True.
- Why drift: projection layer controlled retrieval policy rather than consuming advisory continuity.

3. Session focus retrieval hard-enforced
- File: runtime/session/workspace_runtime_session.py
- Behavior before repair: focus context used enforce=True.
- Why drift: degraded assistive/observational semantics.

4. Daemon health false-negative startup path
- File: runtime/daemon/workspace_continuity_daemon.py
- Behavior before repair: health written before initial topology/locality build.
- Why drift risk: looked like daemon malfunction, encouraged control-oriented repairs.

5. Entry-point under-discovery causing zero topology in this workspace
- File: runtime/daemon/workspace_continuity_daemon.py
- Behavior before repair: only generic UI-oriented entrypoint candidates; PECS-native workspace had no seed path.
- Outcome before repair: runtime locality payload/topology remained empty.

## Non-drift but relevant
- AI chat history watcher existed and was operational.
- Primary gap was normalization/dedup and missing automatic system-event append.
