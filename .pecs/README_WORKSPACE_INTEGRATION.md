# PECS Workspace Integration

This workspace was configured by PECS workspace installer.

PECS artifacts are generated continuity infrastructure only.
Do NOT edit or patch .pecs files.
PECS does not contain engineering sourcecode.
Runtime workspace modules are the authoritative implementation.

Installed items:
- .vscode/tasks.json (PECS tasks, including folder-open auto-start)
- .vscode/settings.json with pecs.contextPath
- .continue/config.yaml
- .continue/rules/pecs-first-routing.yaml
- .continue/rules/PECS_CONTEXT_RULE.md
- .continue/rules/PECS_APPEND_RULE.md
- .continue/rules/CONTINUITY_MAP.md
- .continue/rules/PECS_CODING_PROTOCOL.md
- .continue/rules/PECS_PROMPT.md
- .continue/rules/live-context.md
- .github/copilot-instructions.md
- .pecs/tools/append_ai_chat_history.py
- .pecs/ai_chat_history.json
- .pecs/bridge/run_bridge.py
- .pecs/bridge/export_workspace_continuity.py
- .pecs/bridge/validate_workspace_continuity.py
- .pecs/config/install_root.json
- .pecs/config/continuity_bridge.json
- .pecs/run_pecs.sh
- .pecs/run_pecs.cmd
- .pecs/run_pecs_daemon.sh
- .pecs/run_pecs_daemon.cmd
- .pecs/continuity/engineering_continuity_state.json
- .pecs/continuity/continuity_hydration_report.json
- .pecs/README_MANUAL_SETUP.md

PECS v2 Process Flow:
1. Install workspace assets to configure VS Code, Continue, Copilot, and .pecs infrastructure.
2. Start or auto-start the workspace daemon to generate `.pecs/` continuity artifacts from runtime workspace modules.
3. PECS-PRO writes deterministic continuity outputs such as active context and locality index.
4. PECS-LITE reads those outputs and returns runtime target projections to the AI model.
5. The model uses runtime workspace modules for edits; `.pecs` files remain infrastructure only.
6. Accepted engineering continuity chains preserve high-signal issue-locality-outcome guidance.

Key rules:
- Workspace runtime modules are authoritative.
- `.pecs` files are not sourcecode.
- Use `.pecs` only to identify locality and execution neighborhood.
- Do not edit or patch `.pecs` artifacts.
- Do not use raw chat narratives as locality authority.
- Use structured accepted/rejected locality continuity with confidence.

Run manually:
- Task: PECS: Start Daemon
- Task: PECS: Stop Daemon
- Task: PECS: Refresh Continuity State
- Task: PECS: Validate Continuity State
- Task: PECS: Observation Snapshot (Opt-In)
- Task: PECS: Observation Daemon (Opt-In)
- Task: PECS: Show Emitted Envelope Log (Opt-In)
- Task: PECS: Show Projection Snapshot Log (Opt-In)

Refresh behavior:
- Existing `.pecs` continuity artifacts, chat history, and runtime evidence are preserved.
- Continue and Copilot assets are merged/appended when possible.
- Managed launcher/bridge/tool updates are backup-aware before replacement.
- Runtime workspace modules and topology are not modified by installer flows.

Notes:
- Auto-start task may require VS Code confirmation for automatic tasks.
- Continue/Copilot integration is configured to use PECS locality projection and runtime targets.
- PECS-LITE is stateless and query-driven. It does not scan the workspace.
