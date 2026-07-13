# AUTO TOC INCREMENTAL UPGRADE PLAN

## Objective

This plan describes an incremental approach for upgrading the auto-TOC / continuity export pipeline in the PECS workspace while minimizing risk to existing continuity artifacts and Kimi integration.

## Scope

- Update generated markdown heading and TOC generation logic
- Preserve existing `.pecs/ai_chat_history.json` and `.pecs/continuity/*`
- Keep Kimi continuity ingestion separate from TOC upgrades
- Ensure bridge refresh remains the authoritative regeneration step

## Incremental Steps

### Step 1: Baseline assessment

- Confirm current `.pecs/continuity/` output contents and file formats
- Run `run_bridge.py validate` to capture baseline validation state
- Document current markdown section names and anchor patterns

### Step 2: Isolate TOC changes

- Identify the exact code or script responsible for markdown generation in the continuity bridge
- If a dedicated TOC generator exists, isolate it from the rest of the export pipeline
- Otherwise, treat export formatting changes as a separate refactor in `export_workspace_continuity.py`

### Step 3: Implement safe TOC upgrade

- Make the TOC upgrade backwards-compatible by preserving existing section names where possible
- Add explicit output flags or version metadata to generated markdown headers
- Avoid changing the overall structure of continuity summaries in the same pass as TOC formatting

### Step 4: Add validation and regression coverage

- Extend `run_bridge.py validate` to include markdown heading and TOC checks if not already present
- Add regression tests for generated `.pecs/continuity/*` artifacts using baseline snapshots
- Ensure that `validate` fails if required sections or anchors are missing

### Step 5: Deploy incrementally

- First deploy the TOC upgrade in a feature branch or experimental mode
- Run a bridge refresh in a test workspace
- Review generated markdown artifacts and compare with baseline outputs

### Step 6: Monitor continuity preservation

- After the upgrade, verify that `.pecs/ai_chat_history.json` remains untouched
- Confirm that `.pecs/continuity/continuity_hydration_report.json` and markdown artifacts are regenerated cleanly
- Inspect `continuity_refresh_state.json` for successful refresh events

### Step 7: Roll out to Kimi integration

- Once the TOC upgrade is stable, finalize Kimi continuity ingestion docs
- Confirm Kimi ingestion events continue to trigger refreshes
- Ensure Kimi does not depend on TOC-specific markdown structure

## Risk mitigation

- Keep TOC changes isolated from event ingestion and runtime topology logic
- Preserve generated continuity artifacts during install and upgrade
- Add clear migration notes if heading names or section anchors change

## Deliverables

- Updated TOC generation code in the bridge/export pipeline
- `run_bridge.py validate` extended for markdown output structure
- Regression tests or snapshot comparisons for `.pecs/continuity/*`
- Documentation in `.pecs/README.md` describing any TOC format changes

## Conclusion

This incremental plan keeps the TOC upgrade low-risk by separating formatting changes from core continuity ingestion and retrieval flows. Kimi integration should remain unaffected as long as it continues to use `.pecs/ai_chat_history.json` and the daemon-triggered bridge refresh model.
