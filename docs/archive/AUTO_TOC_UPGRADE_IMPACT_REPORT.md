# AUTO TOC UPGRADE IMPACT REPORT

## Purpose

This report analyzes the potential impact of upgrading the PECS auto-TOC (table of contents) mechanism in relation to the requested Kimi continuity integration work.

## Current State

### Relevant files and components

- `install_workspace_integration.py` — installer and bootstrap management
- `workspace_bridge_cli.py` — bridge CLI and workspace lifecycle commands
- `.pecs/bridge/export_workspace_continuity.py` — continuity export implementation
- `.pecs/bridge/run_bridge.py` — refresh/validate bridge wrapper
- `.pecs/config/continuity_bridge.json` — bridge runtime configuration
- `.pecs/README.md` — documentation for workspace integration and `.pecs` use

### Existing TOC behavior

- The current workspace uses `.pecs` as a continuity infrastructure layer and does not expose a separate auto-TOC subsystem in the main repository structure.
- Continuity exports generate markdown summaries such as `architectural_decisions.md`, `current_workspace_focus.md`, and `unresolved_tensions.md`.
- These artifacts are produced by the bridge and may include structural headings, but no dedicated auto-TOC engine was found in the inspected codebase.

## Upgrade impact analysis

### Direct effects on PECS continuity

- An auto-TOC upgrade would likely affect generated markdown summaries under `.pecs/continuity/`
- If the TOC upgrade changes export formatting or heading generation, the bridge refresh path will regenerate artifacts on next refresh
- The installer preserves existing continuity artifacts, so any TOC formatting changes would appear only after a refresh rather than during install

### Indirect effects on Kimi integration

- Kimi continuity ingestion should be independent of TOC generation
- Kimi-generated events are stored in `.pecs/ai_chat_history.json`, not in generated markdown
- Therefore, Kimi integration is resilient to TOC upgrades as long as the bridge refresh path remains stable

### Risk areas

1. `continuity_bridge.json` mode changes
   - If the bridge switches from `exploratory` to a stricter mode, Kimi events may be handled differently during export
2. Generated markdown schema changes
   - Existing downstream consumers of `.pecs/continuity/*.md` could break if heading anchors or section names change
3. Bridge validation gaps
   - The current `run_bridge.py validate` step verifies schema and size, but may not cover TOC semantics

### Preservation

- Upgrading the TOC mechanism does not require unpreserved changes to `.pecs` continuity artifacts
- The installer already preserves `.pecs/ai_chat_history.json` and `.pecs/continuity/*`
- A TOC upgrade should continue to observe this policy to avoid data loss

## Recommendations

### For Kimi continuity integration

- Keep Kimi event ingestion separate from TOC generation
- Do not add Kimi-specific TOC content to `.pecs/ai_chat_history.json`
- Ensure Kimi event semantics are captured in generated exports without depending on TOC structure

### For upgrade process

- Treat TOC changes as a bridge refresh-time artifact update, not an installer update
- Add regression tests for generated continuity markdown headings and section structure
- Validate `.pecs/continuity/*.md` output after any TOC upgrade using `run_bridge.py validate`

## Conclusion

The auto-TOC upgrade impact on Kimi continuity integration is low if the upgrade is confined to generated markdown exports. The key dependency is the bridge refresh path, not the installer. Kimi should be designed to use `.pecs/ai_chat_history.json` for ingestion and let the bridge regenerate any TOC-related continuity artifacts.
