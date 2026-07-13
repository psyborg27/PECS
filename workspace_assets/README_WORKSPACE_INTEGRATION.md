# PECS Workspace Integration

This workspace was configured by PECS workspace installer.

PECS artifacts are generated continuity infrastructure only.
Do NOT edit or patch .pecs files.
PECS does not contain engineering sourcecode.
Runtime workspace modules are the authoritative implementation.

Installed items:
- .vscode/tasks.json (PECS tasks, including folder-open auto-start)
- .vscode/settings.json with pecs.contextPath
- .continue/rules/PECS_CONTEXT_RULE.md
- .continue/rules/PECS_APPEND_RULE.md
- .github/copilot-instructions.md
- .pecs/tools/append_ai_chat_history.py
- .pecs/ai_chat_history.json
- .pecs/bridge/run_bridge.py
- .pecs/bridge/export_workspace_continuity.py
- .pecs/bridge/validate_workspace_continuity.py
- .pecs/config/continuity_bridge.json
- .pecs/README_MANUAL_SETUP.md

Run manually:
- Task: PECS: Start Daemon
- Task: PECS: Stop Daemon
- Task: PECS: Refresh Continuity State
- Task: PECS: Validate Continuity State
- Task: PECS: Observation Snapshot (Opt-In)
- Task: PECS: Observation Daemon (Opt-In)
- Task: PECS: Stop Observation Daemon (Opt-In)
- Task: PECS: Show Emitted Envelope Log (Opt-In)
- Task: PECS: Show Projection Snapshot Log (Opt-In)

Refresh behavior:
- Existing `.pecs` continuity artifacts and runtime evidence are preserved.
- Existing `.pecs/ai_chat_history.json` is never reset.
- Continue and Copilot assets are merged or appended where possible.
- Managed launcher/bridge/tool updates are backup-aware before changes.
- Existing workspace topology/runtime modules are not modified by installer flows.

Required workflow:
- Query PECS first with canonical `observe-projection-snapshot` or `observe-projection-daemon` commands.
- Perform engineering reasoning and bounded edits on runtime workspace modules.
- Refresh PECS using canonical `refresh`, `rebuild-continuity`, or `rebuild-topology` commands after edits.
- Use preserve-first flows like `install-workspace-assets --preserve`, `refresh-managed-assets --preserve`, `rebind-workspace --preserve`, and `safe-migration --preserve`.

Example commands:

```bash
pecs observe-projection-snapshot "/path/to/workspace" \
  --query "stabilization, ownership lookup, continuity locality" \
  --query-source "copilot" \
  --model-name "unknown" \
  --profile-class frontier \
  --local-vs-frontier frontier

pecs observe-projection-daemon "/path/to/workspace" \
  --query "stabilization, ownership lookup, continuity locality" \
  --query-source "continue" \
  --model-name "unknown" \
  --profile-class local \
  --local-vs-frontier local \
  --iterations 20 \
  --interval-seconds 2.0

pecs refresh "/path/to/workspace"
pecs rebuild-continuity "/path/to/workspace"
pecs rebuild-topology "/path/to/workspace"
pecs restart-daemon "/path/to/workspace"
```
Preserve-first lifecycle:
- `install-workspace-assets --preserve` updates managed workspace assets without wiping continuity.
- `refresh-workspace-bindings` / `rebind-workspace` handles install root changes while preserving history.
- `rebuild-continuity` regenerates derived continuity artifacts safely.
- `rebuild-topology` refreshes runtime/topology outputs without destroying continuity.
- `restart-daemon` cleanly restarts the PECS daemon after managed asset or continuity refresh.

Optional observation mode:
- Observation tasks are opt-in and bounded.
- Snapshots are written to `.pecs/logs/observation/`.
- Logged fields include query/model/profile, emitted advisory cognition, discarded cognition, shaping losses, runtime targets, payload sizing/compression, and session lineage.
- Observation mode is visibility-only and does not force edit destinations.

Notes:
- Auto-start task may require VS Code confirmation for automatic tasks.
- Continue/Copilot integration is configured to use PECS locality projection and runtime targets.
- PECS artifacts are infrastructure only; do not treat them as source.
