# AGENTS.md — PECS-PRO v2

This file is intended for AI coding agents. It describes the project architecture, build/test workflow, code conventions, and operational boundaries of the PECS-PRO v2 repository.

---

## Project Overview

PECS-PRO v2 (Project Execution Continuity System — PRO) is a deterministic, topology-first continuity infrastructure layer for AI-assisted engineering workspaces. It is written in Python and is designed to run as persistent developer infrastructure alongside a target workspace.

The system has two conceptual layers:

- **PECS-PRO** — the continuity authority. It reconstructs runtime topology, execution locality, ownership relationships, and workspace structure. It owns all continuity state and writes deterministic artifacts under `.pecs/` in the target workspace.
- **PECS-LITE** — a stateless projection adapter. It queries PECS-PRO and returns compact, model-shaped locality guidance. It never scans the workspace, never owns continuity state, and never runs as a daemon.

The repository ships as an editable Python package (`pecs_pro`) with console entry points, a file-watching daemon, workspace bootstrap/install scripts, and AI-tooling integration assets for VS Code, GitHub Copilot, and Continue.

Key design principles from the project documentation:

- Continuity is execution-topological, not file-hierarchical.
- PECS-PRO is the single source of truth for runtime topology and continuity.
- `.pecs/` artifacts are generated infrastructure only; they must never be edited as sourcecode.
- Models should use PECS-LITE projections to locate live workspace modules, then edit those modules, not `.pecs/` files.

---

## Technology Stack

- **Language:** Python 3.9+
- **Build / packaging:** `setuptools`, `wheel`, editable install (`pip install -e .`)
- **Primary runtime dependency:** `watchdog` (file-system watching for the daemon)
- **Virtual environment:** `.venv/` managed locally in the repository root
- **Supported platforms:** macOS, Linux, Windows 10/11
- **Recommended editor:** VS Code (task integration is provided)
- **AI tooling targets:** GitHub Copilot Chat, Continue

No web framework, database, or external service is required. All continuity artifacts are local JSON/JSONL files.

---

## Key Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | PEP 517/518 build config, project metadata, console scripts, package discovery |
| `setup.py` | Legacy `setuptools` config mirroring `pyproject.toml` |
| `requirements.txt` | Runtime dependency pin (`watchdog==3.0.0`) |
| `MANIFEST.in` | Specifies extra files to include in the package distribution |
| `workspace_assets/workspace_assets_manifest.json` | Manifest-driven deployment of workspace-local PECS assets |
| `.vscode/tasks.json` | VS Code tasks installed into target workspaces |
| `.continue/config.yaml` | Continue integration config installed into target workspaces |
| `.github/copilot-instructions.md` | Copilot instructions installed into target workspaces |
| `.gitignore` | Excludes `.venv/`, build artifacts, `.pecs/` generated files, and IDE configs |

---

## Repository Structure

```text
.
├── pyproject.toml / setup.py / requirements.txt   # Package and dependency config
├── workspace_bridge_cli.py                       # Main CLI: pecs / pecs-pro entry point
├── run_pecs_daemon.py                            # Daemon launcher
├── run_pecs_pro.py                               # Canonical PECS-PRO runtime bootstrap
├── run_pecs_lite_v2_daemon.py                    # PECS-LITE v2 daemon helper
├── install_workspace_integration.py              # Workspace installer logic
├── workspace_assets_manager.py                   # Manifest-driven asset deployment
├── append_ai_chat_history.py                     # Chat-history append helper
├── validate_governance_determinism.py            # Determinism validation script
├── setup.sh / setup.ps1 / setup.bat              # Repository setup scripts
├── install_pecs_workspace.sh / .ps1              # Workspace bootstrap wrappers
├── launch_pecs_daemon.sh / .ps1                  # Host-side daemon launch helper
│
├── pecs_pro/                                     # Core package subset
│   ├── install_workspace_integration.py
│   └── workspace_assets_manager.py
│
├── continuity/                                   # Continuity object model and registries
│   ├── object_model/                             # Runtime nodes, edges, snapshots, zones, clusters
│   ├── registry/                                 # Continuity, runtime, ownership, duplicate registries
│   └── confidence/                               # Confidence models for topology, ownership, dispatch, etc.
│
├── execution_graph/                              # Graph construction and query engine
│   ├── builders/                                 # Topology graph builder, graph consolidator
│   ├── graph/                                    # Dispatch, execution, ownership, propagation, runtime graphs
│   ├── indexes/                                  # Graph, execution, ownership, runtime-path indexes
│   └── queries/                                  # Continuity path queries, graph query engine
│
├── runtime/                                      # Runtime topology reconstruction
│   ├── daemon/                                   # WorkspaceContinuityDaemon (file watcher + refresh)
│   ├── session/                                  # WorkspaceRuntimeSession
│   ├── engines/                                  # Runtime topology engine
│   ├── dispatch/                                 # Dispatch chain and execution-path mappers
│   ├── signal_slot/                              # Signal/slot topology reconstruction
│   ├── qaction/                                  # QAction / menu / toolbar topology mappers
│   ├── overlays/                                 # Overlay propagation tracking
│   ├── viewer/                                   |Navigation / viewer ownership mappers
│   ├── subprocess/                               # Subprocess topology mapping
│   ├── workspace/                                # Workspace scanner, import locality, entrypoint mapper
│   ├── locality_activation_engine.py
│   ├── runtime_activation_events.py
│   ├── runtime_activation_logger.py
│   └── runtime_telemetry.py
│
├── topology/                                     # Topology indexing, scoring, retrieval, compaction
│   ├── archaeology/                              # Continuity archaeology
│   ├── compaction/                               # Compact context builder
│   ├── incremental/                              # Incremental topology updater
│   ├── indexing/                                 # Locality and topology indexes
│   ├── retrieval/                                # Topology retriever, trace harness
│   ├── scoring/                                  # Continuity score engine
│   ├── locality_traversal.py
│   └── runtime_edge_reinforcement.py
│
├── integrations/                                 # Adapters for AI tooling and PECS-LITE
│   ├── pecs_pro_query_adapter.py
│   ├── pecs_lite_runtime_adapter.py
│   ├── pecs_lite_projection_hardener.py
│   ├── continue_adapter.py
│   ├── copilot_adapter.py
│   └── context_export_adapter.py
│
├── exports/                                      # Continuity export authority
│   └── continuity_exporter.py
│
├── validation/                                   # Continuity integrity validator
│   └── continuity_validator.py
│
├── scripts/                                      # Operational scripts
│   ├── pecs_health_check.py
│   ├── validate_workspace_continuity.py
│   └── export_workspace_continuity.py
│
├── tests/                                        # Test suite
│   └── test_pecs_lite_runtime_validation.py
│
├── workspace_assets/                             # Template assets installed into target workspaces
│   ├── .continue/
│   ├── .github/
│   ├── .pecs/
│   └── workspace_assets_manifest.json
│
├── PECS_LITE v2/                                 # Stateless projection runtime
│   └── pecs_lite v2/
│       ├── pecs_lite_runtime/
│       ├── continuity/
│       ├── integrations/
│       └── runtime/
│
├── .pecs/                                        # Generated continuity infrastructure for THIS repo
│   ├── active_context.json
│   ├── compact_bundle.json
│   ├── locality_index.json
│   ├── topology_compact.json
│   ├── logs/
│   ├── bridge/
│   ├── runtime/
│   └── tools/
│
└── *.md                                          # Extensive architecture/design/report documentation
```

---

## Build and Test Commands

### Initial repository setup

```bash
git clone <repo-url> ~/Developer/PECS
cd ~/Developer/PECS
git checkout main
git pull origin main

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e .
```

On Windows PowerShell use `.venv\Scripts\Activate.ps1` and the equivalent `python` commands.

### Health check

```bash
pecs doctor
# or
python3 scripts/pecs_health_check.py
```

### Workspace bootstrap

```bash
./install_pecs_workspace.sh "/path/to/workspace"
# or
python3 -m workspace_bridge_cli bootstrap-workspace "/path/to/workspace" --repo-root "$(pwd)"
```

### Runtime operations on a workspace

```bash
pecs verify-workspace "/path/to/workspace"
pecs status "/path/to/workspace"
pecs refresh "/path/to/workspace"
pecs validate "/path/to/workspace"
```

### Running tests

The project uses the standard `unittest` module. From the repository root:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
# or run the specific suite
python3 -m unittest tests.test_pecs_lite_runtime_validation -v
```

### Manual daemon launch

```bash
./launch_pecs_daemon.sh "/path/to/workspace"
# or directly
python3 run_pecs_daemon.py "/path/to/workspace"
```

---

## Entry Points and Console Scripts

The package defines the following console scripts (declared in `pyproject.toml` and `setup.py`):

| Command | Module target | Purpose |
|---------|---------------|---------|
| `pecs` | `workspace_bridge_cli:main` | Main workspace bridge CLI |
| `pecs-pro` | `workspace_bridge_cli:main` | Alias for `pecs` |
| `pecs-pro-daemon` | `run_pecs_daemon:main` | Standalone daemon launcher |
| `pecs-pro-install-workspace` | `install_workspace_integration:main` | Workspace installer |

`workspace_bridge_cli.py` is the primary CLI surface and contains subcommands such as `bootstrap-workspace`, `verify-workspace`, `status`, `refresh`, `validate`, `rebind-workspace`, `observe-projection-snapshot`, and `observe-projection-daemon`.

---

## Code Style Guidelines

The codebase follows these observable conventions:

- **Python version target:** 3.9+. Use `from __future__ import annotations` in most modules.
- **Type hints:** Used for public signatures; `typing.Dict`, `List`, `Optional`, `Any` are common.
- **Import style:** Absolute top-level imports are preferred. Relative imports appear inside some subpackages (`runtime.daemon` uses `from ..locality_activation_engine import ...`).
- **Formatting:** 4-space indentation. Module-level `logger = logging.getLogger(__name__)` pattern.
- **Naming:**
  - `PascalCase` for classes and dataclasses.
  - `snake_case` for modules, functions, and variables.
  - `SCREAMING_SNAKE_CASE` for module-level constants (e.g., `HARD_EXCLUDED_DIRS`, `ENTRYPOINT_CANDIDATES`).
- **Dataclasses:** Heavily used for runtime components, daemon state, and object model entities.
- **Path handling:** `pathlib.Path` is used consistently; paths are resolved where possible.
- **JSON persistence:** JSON/JSONL outputs use `sort_keys=True` and `ensure_ascii=True` for determinism.
- **Timestamps:** UTC ISO 8601 with trailing `Z` (e.g., `datetime.utcnow().isoformat() + "Z"`).
- **Error handling:** Graceful degradation is preferred, especially in daemon and telemetry code. Exceptions are often caught, logged, and suppressed rather than crashing the daemon.

### Authority and layering rules reflected in the code

- PECS-PRO owns continuity authority; PECS-LITE does not.
- Keep UI/transport/caller layers thin; business logic belongs in owning core modules.
- Avoid cross-layer leakage of processing logic.
- Do not introduce parallel logic, duplicate authorities, or orchestration forests.
- Preserve public signatures unless explicitly instructed otherwise.

---

## Testing Instructions

- Tests live in `tests/` and use the standard `unittest` framework.
- The only committed test file is `tests/test_pecs_lite_runtime_validation.py`.
- Tests verify PECS-LITE projection profiles, telemetry output, and runtime-target behavior across small/medium/large model identities.
- Telemetry events are written to `telemetry/runtime_jsonl/pecs_runtime_*.jsonl`.
- Run tests from the repository root with `python3 -m unittest discover -s tests`.
- When adding tests, use existing workspace artifacts or user-provided fixtures. Do not fabricate execution results, runtime behavior, or benchmark data.

---

## Security Considerations

- PECS writes generated continuity artifacts under `.pecs/` in the target workspace. These files are infrastructure and must not be treated as editable sourcecode.
- The daemon performs file-system watching and Python AST inspection limited to configured workspace roots. It does not execute arbitrary user code.
- Installer scripts copy guidance files into `.github/`, `.continue/`, and `.vscode/` directories of the target workspace. Backups are created during upgrades.
- The package relies only on `watchdog` and the Python standard library. Keep the dependency surface small.
- PECS is intended to support human-directed workflows; it is not an autonomous engineering agent. Avoid adding autonomous mutation, self-modifying infrastructure, or recursive AI orchestration.
- Do not install PECS from transient directories such as `Downloads`, `Desktop`, `/tmp`, or removable drives. The installer warns when the install root matches known unstable patterns.

---

## Development Conventions

### What to edit

- Edit live workspace runtime modules for feature work.
- Edit PECS engine modules (this repository) when improving continuity, topology, adapters, or installer behavior.
- Do **not** edit `.pecs/` artifacts by hand. They are regenerated by the daemon/bridge refresh cycle.

### Preservation discipline

- Treat existing code as potentially active unless proven otherwise.
- Do not delete code just because it appears unused.
- Prefer localized patches and symbol-level edits over file-wide rewrites.
- Verify imports, call sites, signal wiring, and startup paths after changes.
- If logic must be moved, explicitly state source location, destination, and reason.

### Adding new modules

- Place modules under the owning package (`continuity/`, `execution_graph/`, `runtime/`, `topology/`, `integrations/`, `validation/`, `exports/`).
- Update `pyproject.toml` and `setup.py` package discovery only if a new top-level package is introduced.
- Avoid creating parallel validation, export, or query authorities.

### Logging and telemetry

- Use module-level `logger = logging.getLogger(__name__)`.
- Runtime telemetry is emitted as structured JSONL to `telemetry/runtime_jsonl/` and `.pecs/logs/`.
- Events use `subsystem`, `event`, and `payload` fields with UTC timestamps.

---

## Runtime Architecture

The canonical runtime flow is:

1. `run_pecs_pro.py::PECSProRuntime.initialize()` wires together:
   - `ContinuityRegistry`, `RuntimeRegistry`
   - `GraphIndex`, `ExecutionIndex`, `OwnershipIndex`
   - `LocalityIndex`
   - `ContinuityScoreEngine`
   - `TopologyRetriever`
   - `IncrementalTopologyUpdater`
   - `WorkspaceRuntimeSession`
   - `CompactContextBuilder`

2. `run_pecs_daemon.py` creates a `WorkspaceContinuityDaemon` and starts it.

3. The daemon watches the workspace for file changes, chat events, and runtime activation events.

4. On trigger, it rebuilds runtime-reachable topology and writes deterministic artifacts to `.pecs/`:
   - `active_context.json`
   - `compact_bundle.json`
   - `locality_index.json`
   - `topology_compact.json`
   - `continuity_refresh_state.json`

5. A workspace-local bridge (`run_bridge.sh` / `run_bridge.py`) executes refresh and validation commands.

6. PECS-LITE queries PECS-PRO via `PECSProQueryAdapter` and returns bounded projections through `PECSLiteRuntimeAdapter`.

---

## Deployment and Distribution

- The package is installed in editable mode (`pip install -e .`) during normal setup.
- Distribution uses `setuptools` with `MANIFEST.in` to include shell scripts, PowerShell scripts, bat files, JSON files, and workspace assets.
- `zip_safe=False` is set to ensure launcher scripts and assets behave correctly.
- No containerization, CI/CD pipeline, or cloud deployment is currently present in the repository.

---

## Useful Reference Files

- `README.md` — Repository landing page: overview, purpose, architecture, quick start, and documentation links.
- `README_MANUAL_SETUP.md` — Manual setup procedures (kept at repo root for installer compatibility).
- `PECS_ARCHITECTURE_BASELINE.md` — Canonical architectural baseline.
- `PECS_ARCHITECTURAL_PROJECTION_SPEC.md` — Canonical architectural projection specification.
- `PECS_CANONICAL_QUERY_AND_PROJECTION_CONTRACT.md` and `PECS_QUERY_CONTRACT.md` — Canonical query/response contracts.
- `CHANGELOG.md` — Canonical project changelog.
- `docs/getting-started.md` — First-time install and workspace bootstrap guide.
- `docs/architecture.md` — Implemented architecture overview.
- `docs/design-principles.md` — Core deterministic design principles.
- `docs/glossary.md` — Primary PECS terminology.
- `docs/workspace-graph.md`, `docs/workspace-registry.md`, `docs/evidence-correlation.md`, `docs/navigation-builder.md`, `docs/query-pipeline.md` — Component documentation.
- `docs/integrations/` — Consumer-specific integration contracts.
- `docs/developer-guide.md` — Project coding and patch discipline guidelines.
- `docs/artifacts.md` — Catalog of generated artifacts and installed workspace assets.
- `docs/troubleshooting.md` — Operational troubleshooting and observability.
- `docs/roadmap.md` — Future direction and planned upgrades.
- `docs/archive/` — Genuinely obsolete historical reports and design traces.
- `workspace_assets/workspace_assets_manifest.json` — Asset deployment manifest.

---

## Quick Command Reference

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .

# Health
pecs doctor

# Bootstrap a workspace
./install_pecs_workspace.sh /path/to/workspace

# Workspace operations
pecs status /path/to/workspace
pecs refresh /path/to/workspace
pecs validate /path/to/workspace
pecs verify-workspace /path/to/workspace

# Tests
python3 -m unittest discover -s tests -v
```

---

Last updated: 2026-07-07. This file reflects the actual project content at the time of creation.
