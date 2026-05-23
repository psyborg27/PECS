
# ⚠ Active Runtime Validation Branch

Current live PECS runtime testing and observability validation are occurring on:

`pecs-runtime-observability-stable`

The `main` branch is currently not the primary branch for active runtime continuity validation, daemon observability testing, or AI workflow propagation experiments.

For current PECS runtime behavior, continuity propagation testing, and observability instrumentation, use the active validation branch instead.

## Current Validation Scope

The active validation branch currently contains:
- daemon observability instrumentation
- runtime trigger-chain tracing
- continuity projection diagnostics
- AI continuity extraction validation
- bridge refresh tracing
- structured JSONL runtime logs

Operational validation is still ongoing.
Semantic continuity effectiveness and downstream AI behavioral influence are still under evaluation.

---

# PECS-PRO

## Branch Guidance

- Recommended stable branch: `main`
- Development branch: not present in this repository; use `main`
- Current `main` status: stable and canonical for this checkout

**Branch selection is critical before installation.** Always verify you are on the intended branch before onboarding a workspace:

```bash
git fetch origin
git checkout main
git pull origin main
```

If you are using a fork or a custom branch, install only from the branch you trust.

## IMPORTANT DISCLAIMER

THIS DIRECTORY IS GENERATED CONTINUITY INFRASTRUCTURE.
DO NOT EDIT.
DO NOT PATCH.
DO NOT TREAT AS ENGINEERING SOURCECODE.

THIS FILE DOES NOT CONTAIN SOURCECODE.
IT ONLY CONTAINS:
- ENGINEERING TARGET LOCATIONS
- EXECUTION LOCALITY
- CONTINUITY RELATIONSHIPS
- RUNTIME TOPOLOGY

ENGINEERING TRUTH EXISTS ONLY IN:
WORKSPACE RUNTIME MODULES.

PECS artifacts are queryable continuity infrastructure only.
PECS is NOT editable engineering sourcecode.
Use `.pecs` for locality retrieval, then edit runtime workspace modules.

## Installation Entry Point

Use the canonical install path in **Installation and Runtime Workflow (Current)**.
That section is the single source for clone/setup/bootstrap/daemon/refresh workflow.

Supported platforms:

- macOS
- Linux
- Windows 10 / 11

Prerequisites:

- Git
- Python 3.9 or newer
- VS Code (recommended for task integration)
- PowerShell or CMD on Windows

## Installation Location Guidance

**IMPORTANT:**
PECS is persistent developer infrastructure. Do **NOT** install or run PECS from transient or unstable directories such as:
- Downloads
- Desktop
- /tmp or other temporary folders
- Removable/external drives

**Recommended install locations:**
- `~/Developer/PECS/`
- `~/Applications/PECS/`
- `C:\Users\<USER>\Developer\PECS\`

PECS must reside in a stable, user-owned directory to ensure reliable operation and avoid accidental deletion or corruption. This is critical for continuity and daemon reliability.


## Installation Health Check

After installation, verify PECS runtime and entrypoints:

```bash
# From the PECS repo root
pecs doctor
```

Or run the bootstrap health check directly:

```bash
python3 scripts/pecs_health_check.py
```

To validate dependencies only:

```bash
python3 install_workspace_integration.py <workspace-root> --validate-deps
```

The installer and health check will warn if PECS is installed into an unstable location or if required dependencies are missing.

## Relocation Recovery

If the PECS install root changes, recover the workspace integration with:

```bash
git clone <your-repo-url> ~/Developer/pecs_pro
cd ~/Developer/pecs_pro
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e .
pecs rebind-workspace "/path/to/your/workspace" --upgrade
```

This rewrites workspace VS Code tasks, daemon launch bindings, and bridge paths to the current PECS install root.

## Persistent Infrastructure Notice

PECS is not experimental tooling. It is persistent developer infrastructure. Treat your PECS install root as you would any critical developer toolchain or application. Do not move or delete the install root while in use.

PECS-PRO v2 is the continuity authority for workspace-local AI continuity.
It generates deterministically repeatable `.pecs/` artifacts that capture:
- runtime topology
- execution locality
- continuity relationships
- workspace target projections

PECS-PRO is not a reasoning engine.
It stabilizes the continuity state so an LLM can reason from compact, topology-aware evidence.

## What PECS-LITE Is

PECS-LITE is a stateless projection layer.
It does not scan the workspace, reconstruct topology, or infer authority independently.
Instead, it queries PECS-PRO continuity outputs and returns compact runtime workspace target projections.

PECS-LITE is intentionally:
- stateless
- lean
- query-driven
- projection-only

## E10 Process Flow

1. **Install workspace assets**
   - `pecs install-workspace-assets <workspace>` writes VS Code tasks, Continue rules, Copilot guidance, and `.pecs/` bridge assets.

2. **Start the workspace daemon**
   - The daemon runs in the workspace and populates `.pecs/` continuity artifacts from runtime workspace modules.

3. **Generate continuity infrastructure**
   - PECS-PRO writes `.pecs/active_context.json`, `.pecs/compact_bundle.json`, `.pecs/locality_index.json`, and other continuity artifacts.

4. **Use PECS-LITE as projection**
   - The model queries PECS-LITE, which reads PECS-PRO output and returns recommended runtime targets and execution neighborhood projections.

5. **Target runtime modules, not `.pecs`**
   - Workspace modules are authoritative. `.pecs` files are infrastructure only and must not be edited.

6. **Refresh and validate**
   - The daemon and bridge refresh `.pecs` when runtime state changes, and verification commands confirm installation health.

## Architecture Separation

Current implementation flow:

MODEL → PECS-LITE QUERY ADAPTER → PECS-PRO CONTINUITY AUTHORITY → `.pecs/` ARTIFACTS → MODEL

PECS keeps a strict separation between engine and workspace state:

- **PECS engine**: exporters, validators, normalization logic, topology tooling, bridge installers, and the continuity authority.
- **Workspace continuity state**: `.pecs/` artifacts, runtime evidence, bridge runtime/config, and installed VS Code/Continue guidance.

This separation keeps PECS deterministic, maintainable, and safe for AI-assisted workflows.

## PECS-PRO Authority Model (Final Architectural Realization)

**PECS-PRO is the ONLY continuity authority.**

PECS-PRO exclusively owns and maintains:
- runtime topology reconstruction
- execution graph continuity
- workspace structure scanning
- runtime activation evidence
- continuity state persistence
- topology-aware locality weighting
- ownership and mutation locality tracking
- runtime zone and cluster classification

PECS-PRO generates deterministic `.pecs/` artifacts:
- `.pecs/active_context.json` — runtime execution context
- `.pecs/active_topology.json` — current runtime topology
- `.pecs/locality_index.json` — locality-weighted targets
- `.pecs/compact_bundle.json` — compressed continuity state
- `.pecs/daemon_state.json` — daemon health and state

## PECS-LITE Projection Model (Query-Driven Stateless Layer)

**PECS-LITE is ONLY a stateless query and projection adapter.**

PECS-LITE exclusively does:
- normalize AI model queries
- request locality from PECS-PRO
- project compact runtime target neighborhoods
- compress continuity for model consumption
- adapt output format for specific AI tooling (Copilot, Continue)
- filter and shape authority-safe outputs

**PECS-LITE must NEVER:**
- run as an independent daemon
- maintain continuity state
- own topology artifacts
- reconstruct runtime relationships
- scan workspace
- infer execution state independently
- cache or index continuity data
- perform any form of authority reconstruction

PECS-LITE is invocation-driven only:
- queries PECS-PRO on demand
- returns ephemeral projection outputs
- stateless between invocations
- no persistent daemon responsibility

## Why This Authority Separation Matters

**Single Source of Truth:** Only PECS-PRO interprets runtime topology and continuity. This prevents drift where PECS-LITE makes different continuity inferences than PECS-PRO.

**Small, Predictable Projection:** PECS-LITE is small and stateless. It scales horizontally since it doesn't maintain state and doesn't conflict with other instances.

**Authority-Safe Model Guidance:** Models receive projection outputs labeled explicitly as ephemeral locality guidance, not canonical workspace truth. `.pecs/` artifacts are infrastructure only, never engineering sourcecode.

**Reduced Complexity:** All topology interpretation happens in PECS-PRO. PECS-LITE is a thin adapter layer, making failures easier to diagnose and security easier to audit.

## Context Bridge

The workspace-local context bridge exists only to:
- normalize continuity inputs deterministically
- compare before writing
- suppress no-op rewrites
- persist stable continuity anchors

The bridge does not:
- act as conversational authority
- perform semantic summarization
- orchestrate AI decisions
- replace LLM reasoning

## Supported AI Tooling

PECS is currently designed and tested primarily for:
- GitHub Copilot Chat
- Continue

Compatibility note:
- Other VS Code AI extensions may not preserve compatible continuity/workflow behavior.
- PECS is built around deterministic continuity anchors and sparse runtime projection, not broad semantic indexing.

## What changed in v2 vs v1

### v1
- line-number continuity anchors like `file.py:42`
- file-based locality tokens
- heavier continuity payloads
- no persistent live daemon

### v2
- canonical symbolic anchors like `PECS_ID:viewer.overlay.sync`
- compact anchor-based locality storage
- topology-aware retrieval via query adapters
- incremental live daemon generating `.pecs/` artifacts
- low-token compact context export
- no AST-heavy reconstruction or large continuity payloads

## Why PECS Exists: The Locality Problem

AI-assisted development creates **locality uncertainty** and **continuity drift**:

1. **Execution-Local Fragmentation**
   - Code changes scatter across files, modules, and runtime zones
   - An AI model loses track of which files are execution-adjacent vs. semantic-similar
   - Models treat all "similar" code equally, but runtime locality matters more

2. **Wrapper Penetration ("Gunpowder in Another Barrel")**
   - A bug exists in file A, but the ownership chain passes through wrappers in B and C
   - Fixing in A alone is incomplete; B or C needs changes too
   - An LLM may fix A but miss B/C because it doesn't see the wrapper dependency chain

3. **Mutation Ownership Drift**
   - A change in file A mutates runtime state that file D doesn't export
   - File D's code becomes stale relative to the mutation in A
   - The AI model doesn't know which files are mutation-dependent on which others

4. **Runtime Authenticity Loss**
   - After many edits, the workspace's actual runtime behavior diverges from inferred structure
   - No persistent record of which files currently run, which are dead code, which are active
   - Models reconstruct runtime state from scratch on each session, losing continuity

**PECS stabilizes execution locality continuity.** It does NOT replace reasoning or inference. The LLM still decides what to change. PECS just makes locality reliable.

## Known Limitations

PECS remains probabilistic and incomplete:
- **Runtime certainty:** PECS weights locality evidence but cannot guarantee wrapper penetration is complete
- **Mutation tracking:** Mutation ownership is inferred, not fully traced; some mutation chains may be incomplete
- **Semantic extraction:** Issue extraction from chat history is imperfect; some context gets lost
- **Continuity drift:** After many edits, some stale continuity may accumulate
- **Wrapper penetration:** Not all wrapper chains are detected; some ownership chains remain hidden

PECS reduces execution-locality uncertainty by orders of magnitude, but does not guarantee complete certainty.

## What PECS Does NOT Do

- Solve general LLM reasoning problems
- Eliminate ambiguity in code semantics
- Replace careful code review
- Guarantee correctness of changes
- Eliminate the need for testing
- Solve authentication, security, or permission issues
- Provide global semantic indexing
- Build a "reasoning engine" for the LLM

PECS is **locality stabilization infrastructure only.**

## Installation and Runtime Workflow (Current)

This is the current supported setup path for this repository.
Use this flow for new installs and workspace onboarding.

### 1. Clone and choose branch

```bash
git clone <your-repo-url> ~/Developer/PECS
cd ~/Developer/PECS
git checkout main
git pull origin main
```

### 2. Create venv and install dependencies

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e .
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e .
```

### 3. Bootstrap workspace integration (installer path)

Use the repository installer script (interactive or path argument):

macOS / Linux:

```bash
./install_pecs_workspace.sh "/path/to/workspace"
```

Windows PowerShell:

```powershell
.\install_pecs_workspace.ps1 "C:\path\to\workspace"
```

The installer runs `workspace_bridge_cli bootstrap-workspace` under the hood.
Bootstrap installs assets, writes install-root bindings, starts the daemon, triggers refresh, and verifies workspace integration.

### 4. Verify runtime state

```bash
pecs verify-workspace "/path/to/workspace"
pecs status "/path/to/workspace"
pecs refresh "/path/to/workspace"
pecs validate "/path/to/workspace"
```

### 5. VS Code task workflow

Expected tasks after bootstrap:

- `PECS: Start Daemon`
- `PECS: Stop Daemon`
- `PECS: Refresh Continuity State`
- `PECS: Validate Continuity State`
- `PECS: Append Chat Event`
- `PECS: Manual Update Chat History`
- `PECS: Auto Start Daemon On Folder Open`

Installer-written launchers are workspace local:

- `.pecs/run_pecs_daemon.sh`
- `.pecs/run_pecs_daemon.ps1`
- `.pecs/run_pecs_daemon.cmd`

Daemon startup writes `.pecs/daemon.pid` and runtime output to `.pecs/daemon.log`.

### Multi-workspace runtime expectations

PECS supports multi-workspace usage from one install root.
Each workspace keeps its own `.pecs` runtime state, daemon PID/logs, bridge state, and continuity artifacts.
Workspace launchers and bridge scripts resolve runtime paths through `.pecs/config/install_root.json`.

### Expected `.pecs/` structure (current runtime)

```text
.pecs/
   bridge/
   config/
   continuity/
   logs/
   runtime/
   tools/
   active_context.json
   compact_bundle.json
   topology_compact.json
   locality_index.json
   continuity_refresh_state.json
   ai_chat_history.json
   daemon.pid
   daemon.log
```

## Runtime Trigger Flow

Current trigger chain:

workspace activity
-> daemon detection
-> topology rebuild
-> projection refresh
-> continuity refresh
-> bridge export

Runtime events can be generated by file changes, Copilot/Continue chat activity, or runtime activation updates.

## Runtime Observability

PECS daemon observability is workspace-local under `.pecs/logs/`.

Primary log files:

- `.pecs/logs/daemon_activity.log`
- `.pecs/logs/continuity_sync.log`
- `.pecs/logs/daemon_errors.log`

Behavior:

- Structured JSONL (one JSON object per line)
- UTC `ts` field, `event`, and `details`
- Trigger-chain tracing from detection to bridge execution
- Lightweight rotating logs (256 KB max file, backup count 3)

Representative events include:

- activity: `file_change_detected`, `copilot_activity_detected`, `continue_activity_detected`, `continuity_refresh_started`, `bridge_execution_succeeded`
- continuity: `projection_refresh_started`, `projection_refresh_completed`, `projection_skipped`, `projection_no_changes`, `continuity_noop`
- errors: `continuity_extraction_failed`, `projection_refresh_failed`, `bridge_execution_failed`

## Active Continuity Artifacts

Current primary runtime artifacts:

- `active_context.json`
- `compact_bundle.json`
- `topology_compact.json`
- `locality_index.json`
- `continuity_refresh_state.json`

These are refreshed by daemon topology/runtime cycles and bridge refresh execution.

## Bridge Refresh Behavior

Bridge refresh is run by the daemon through workspace-local bridge runners:

- `.pecs/bridge/run_bridge.sh` (preferred when executable)
- `.pecs/bridge/run_bridge.py` (fallback)

Refresh state is persisted in `continuity_refresh_state.json` with `trigger`, `reason`, `status`, and timestamps.
Manual refresh remains available through `pecs refresh` or `PECS: Refresh Continuity State`.

## AI Continuity Extraction Behavior

Daemon continuity extraction reads `.pecs/ai_chat_history.json` and emits extraction diagnostics/events to `continuity_sync.log`.
Chat-history replay remains optional and experimental.
Deterministic `.pecs` continuity artifacts remain the primary handoff for runtime locality context.

## Runtime Notes

- Observability timestamps are UTC ISO 8601.
- Continuity refresh is throttled (`continuity_refresh_throttle_seconds`, current default 60s).
- Throttled refresh attempts are logged as `projection_skipped` with `reason: throttled`.
- No-op refresh/write paths are expected and logged (`continuity_noop`, `projection_no_changes`).
- Experimental continuity ingestion remains active; extraction behavior is instrumented but still being evaluated for downstream influence.

## Current Validation Status

- Runtime observability: validated.
- AI continuity extraction: partially validated.
- Downstream AI behavioral influence: still under evaluation.

---

For manual setup procedures, see `README_MANUAL_SETUP.md`.
For optional chat-history workflows, see `README_AI_CHAT_HISTORY.md`.

## PECS-LITE Design Principle: Projection Discipline

PECS-LITE exists for ONE purpose:

**Reduce execution-locality entropy for constrained coding models.**

PECS-LITE intentionally sacrifices:
- continuity completeness
- topology breadth
- historical context

In favor of:
- small-model execution locality precision
- bounded runtime target neighborhoods
- high-confidence locality narrowing

### Why Projection Discipline Matters

Large continuity dumps fail for small-context models because:

1. **Search entropy explosion** — thousands of candidate files overwhelm model reasoning
2. **Token budget exhaustion** — complete topology metadata consumes model context
3. **Noise amplification** — historical and stale locality distract from current execution
4. **Authority confusion** — models struggle to distinguish infrastructure from sourcecode

PECS-LITE solves this by:

- **Hard-limiting projection breadth** — small models receive 3-6 primary targets + 2-4 neighbors only
- **Confidence-ordering targets** — highest-confidence runtime files first
- **Entropy reduction** — aggressive filtering of distant, inactive, historical locality
- **Authority clarity** — explicit separation of editable modules from `.pecs` infrastructure

### Projection Profiles

PECS-LITE supports three projection profiles:

#### SMALL Profile (6k–32k models)
- 3 primary runtime targets
- 2 secondary neighbors
- 2000-token budget
- Highest confidence only
- Used for Qwen, DeepSeek, Claude 3.5 Sonnet with other context

#### MEDIUM Profile (32k–100k models)
- 6 primary targets
- 4 secondary neighbors
- 4000-token budget
- Near-locality adjacency
- Balanced breadth and precision

#### LARGE Profile (100k+ models)
- 10 primary targets
- 6 secondary neighbors
- 8000-token budget
- Broader but still strictly bounded

All profiles enforce:
- Hard target count limits
- Token budgeting
- Safe `.pecs` artifact exclusion
- Small-model safety validation

### PECS-LITE Query Flow Integrity

PECS-LITE maintains authority separation by:

1. **Querying PECS-PRO exclusively** — never scans workspace
2. **Reading .pecs artifacts only** — never owns continuity state
3. **Returning projections, not topology** — ephemeral guidance only
4. **Recording query diagnostics** — proving no reconstruction occurred
5. **Validating small-model safety** — ensuring no .pecs exposure to models

Every projection includes:
- Query flow diagnostics
- Health metrics
- Authority confirmations
- Safety validation results

Negative assertions prove:
- "PECS-LITE did NOT scan workspace"
- "PECS-LITE did NOT reconstruct topology"
- "PECS-LITE did NOT own continuity state"

### Why Projections are NOT Editable

PECS-LITE projections are:
- **Ephemeral** — regenerated on each query
- **Lossy** — intentionally simplified for models
- **Infrastructure** — guidance only, not sourcecode
- **Stateless** — no persistence or authority

Models must:
- Use projected targets to locate **editable runtime files**
- Never edit `.pecs` artifacts
- Never treat projections as authoritative sourcecode
- Query PECS-LITE, never edit its outputs

### Performance Characteristics

Small-model projection hardening achieves:
- **3-10x token reduction** — compared to raw continuity dumps
- **50-70% entropy reduction** — compared to workspace-wide file lists
- **100-200ms query latency** — sub-second projection generation
- **Zero workspace scanning** — file I/O bounded to `.pecs/` directory only

## Engineering Continuity Principle

PECS preserves accepted engineering continuity.

PECS does NOT preserve raw conversational history as projection context.

### Why Raw Chat is Noisy

Raw transcript history often contains:
- failed edits
- rollback pollution
- duplicate exploratory reasoning
- stale locality assumptions
- wrapper confusion

Even large models can degrade when fed noisy conversational continuity.

### What PECS Preserves Instead

PECS continuity is structured and compact:
- issue -> accepted locality -> outcome chains
- rejected locality chains for downranking
- continuity confidence (probabilistic, not deterministic)
- accepted followup continuity and locality stability
- unresolved engineering locality tensions (bounded)

### Why Accepted and Rejected Locality Both Matter

- Accepted locality captures stable engineering ownership and successful followups.
- Rejected locality prevents repeated mutation of failed areas.
- Confidence scoring prevents false certainty when continuity is weak.

### Profile-Aware Engineering Continuity Richness

#### SMALL profile
- tiny accepted continuity anchors only
- accepted locality + continuity confidence
- at most one rejected locality hint
- no narrative continuity

#### MEDIUM profile
- bounded continuity chains
- nearby engineering continuity relationships
- confidence-aware locality ambiguity

#### LARGE profile
- richer but bounded accepted engineering continuity
- accepted locality evolution
- rejected locality chains
- unresolved engineering tensions
- mutation-locality ambiguity

All profiles remain structured, bounded, and execution-local.
PECS never emits raw chat dumps as continuity payload.

### Why This Helps Small and Large Models

- Small models avoid search entropy collapse by inheriting compact accepted continuity anchors.
- Large models gain higher-signal continuity linkage without continuity sludge.
- Both receive probabilistic locality guidance with explicit confidence and ambiguity.

## Disclaimer

PECS-PRO is not an autonomous AI project manager.
It is a continuity infrastructure layer only.
Use it to support human-directed workflows, not to replace them.

PECS-LITE is a stateless projection layer.
It does not reason, infer, or own continuity authority.
It queries PECS-PRO and returns bounded locality guidance.
Never edit PECS-LITE outputs or treat them as sourcecode.
