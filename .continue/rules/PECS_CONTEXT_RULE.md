# PECS CONTEXT RULE

PECS artifacts are continuity infrastructure only.
They do not contain editable sourcecode.

Before proposing edits, read and respect:
- .pecs/active_context.json
- .pecs/compact_bundle.json
- .pecs/session_context.json
- .pecs/locality_index.json
- .continue/rules/CONTINUITY_MAP.md (if present)

Priority order:
1. Live workspace runtime modules
2. PECS locality projection and continuity artifacts
3. Historical chat memory

Never edit or patch .pecs files.
Use PECS only for locality retrieval and execution neighborhood projection.

Always run workspace commands with environment activation when available:
cd "${workspaceFolder}"
source .venv/bin/activate
