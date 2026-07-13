# PECS Alpha 1

PECS is experimental Alpha 1 software for runtime-aware workspace continuity. It builds deterministic runtime topology and artifact outputs to support AI-assisted workflows.

## Project Purpose

PECS is intended to help AI tools and developers understand which workspace files are runtime-adjacent, which modules own execution behavior, and how continuity evidence should be correlated.

## Problem Statement

Workspace tooling typically lacks persistent runtime continuity. AI assistants can lose track of execution locality, ownership chains, and runtime dependencies. PECS is designed to make those relationships explicit in a deterministic way.

## Why PECS Exists

PECS exists to separate runtime continuity authority from projection delivery. It provides a stable artifact layer for AI consumer adapters without embedding semantic search or AI reasoning in the core infrastructure.

## Expected Outcomes

- deterministic continuity artifacts
- a canonical workspace graph and registry
- structural evidence correlation for queries
- bounded projections for AI consumers
- a workspace bootstrap, refresh, and validation workflow

## Alpha-1 Scope

PECS Alpha 1 currently supports:

- Python runtime discovery
- daemon-based workspace refresh
- `.pecs/` artifact generation
- workspace graph and registry construction
- evidence correlation and navigation projection
- CLI commands for bootstrap, refresh, validate, query, and upgrade
- adapters for Copilot, Continue, Kimi, and Command Code

This Alpha release is experimental and implementation-focused.

## Architecture Overview

PECS has two layers:

- **PECS-PRO** — continuity authority and artifact writer
- **PECS-LITE** — stateless projection adapter

See `docs/ARCHITECTURE.md` for the full architecture reference.

## Repository Structure

- `workspace_bridge_cli.py` — main PECS CLI
- `runtime/` — daemon and runtime topology discovery
- `execution_graph/` — workspace graph builders and indexes
- `workspace_registry/` — feature/infrastructure classification
- `evidence_correlation/` — evidence scoring engine
- `navigation_builder/` — navigation graph projection
- `pecs_query/` — query pipeline
- `integrations/` — consumer adapters and projection wrapper
- `workspace_assets/` — managed workspace assets
- `docs/` — documentation

## Installation Overview

```bash
git clone <repo-url> ~/Developer/PECS
cd ~/Developer/PECS
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e .
pecs doctor
```

## Upgrade Overview

Upgrade a workspace with:

```bash
pecs upgrade-workspace "/path/to/workspace" --repo-root "$(pwd)"
```

## Supported Platforms

- macOS
- Linux
- Windows 10 / 11

## Supported AI Coding Assistants

- GitHub Copilot
- Continue
- Kimi
- Command Code

## Basic Workflow

1. install PECS
2. bootstrap a workspace
3. run the daemon and refresh continuity
4. query `pecs query-pipeline` or a supported adapter
5. edit live workspace source
6. refresh and validate again

## Documentation Index

- [Documentation landing page](docs/index.md)
- [Installation](docs/INSTALLATION.md)
- [Upgrade](docs/UPGRADE.md)
- [Workflow](docs/WORKFLOW.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Outputs](docs/OUTPUTS.md)
- [Configuration](docs/CONFIGURATION.md)
- [FAQ](docs/FAQ.md)
- [Legal](docs/LEGAL.md)
- [CLI Reference](docs/MAN_PAGES.md)

## Development Roadmap

Current Alpha 1 development is focused on deterministic continuity and projection behavior.

## Future Work

Future work may include:

- stronger adapter integrations
- additional language support
- a daemon IPC query path

## Current Limitations

- experimental Alpha 1 only
- Python-only runtime discovery
- no semantic embeddings in the core
- `.pecs/` artifacts are generated infrastructure only

## Known Issues

- dynamic imports may be missed
- line-range resolution is Python-specific
- query projections are intentionally bounded
- upgrade compatibility is not guaranteed across alpha revisions

## Contribution Notes

Contributions should preserve determinism, avoid feature speculation, and document current implementation behavior.

## Copyright

Copyright © 2026

Ashok Rajagopalan, Advocate

All Rights Reserved.

## Contact

pecs_project@gmail.com

## Legal Reference

See `docs/LEGAL.md`.

## Typical Update Flow

```
1. Workspace file changes are detected by the daemon (file watcher)
2. Daemon triggers topology rebuild → runtime locality payload
3. Continuity refresh exports engineering continuity from chat history
4. artifacts are written to .pecs/ (locality_index, topology_compact, active_context, etc.)
5. Bridge export writes continuity state (active_topology, locality_state, etc.)
6. Validation confirms determinism and schema stability
```

---

## Current Alpha-1 Capabilities

- **Workspace Graph** — Unified canonical graph with 18 node types, 17 edge types, deterministic hashing, and stable serialization.
- **Workspace Registry** — Deterministic feature/infrastructure classification with weighted evidence and tanh-normalized confidence.
- **Evidence Correlation** — 14 weighted structural evidence sources, tier-based evidence fusion (static/runtime/continuity/validation), deterministic clustering.
- **Navigation Builder** — Seed collection, bounded boundary expansion, AST line-range resolution with caching, parent/child wiring.
- **Query Pipeline** — Full CLI flow with artifact loading, lifecycle logging, and schema `pecs.query_pipeline.v1` JSON output.
- **Consumer Adapters** — Four adapters covering Copilot, Continue, Kimi, and Command Code with projection profile support (SMALL/MEDIUM/LARGE).
- **Daemon** — File-watching daemon with topology rebuild, artifact generation, JSONL logging, and health reporting.
- **Installer** — Full workspace bootstrap with manifest-driven asset deployment, preserve-first upgrade, and cross-platform launcher scripts.
- **Bridge** — Workspace-local refresh, export, and validation scripts with deterministic write discipline.
- **Continuity Export** — Engineering continuity state from chat history with chain tracking, divergence detection, and hotspot collection.

## Planned Alpha-2 Work

- **Consumer integration hardening** — Full validation of Copilot, Continue, Kimi, and Command Code integrations.
- **Auto-TOC validation** — End-to-end TOC extraction and upgrade impact verification.
- **Projection quality benchmarking** — Quantitative measurement of projection precision and recall.
- **Extension-point inference** — Detect and rank extension points (hooks, plugins, signals).
- **Impact graph construction** — Build a graph of change impact propagation paths.
- **Legacy parallel structures** — Remove RuntimeGraph/ExecutionGraph/OwnershipGraph after all consumers are migrated.
- **IPC query endpoint** — Direct daemon query path without CLI-side rebuilding.
- **Multi-language line ranges** — Extend AST line-range resolution beyond Python.

---

## Build Instructions

```bash
# Clone and set up
git clone <repo-url> ~/Developer/PECS
cd ~/Developer/PECS
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e .

# Verify installation
pecs doctor
```

## Installation

Install PECS once into a stable location, then bootstrap each target workspace:

```bash
# Bootstrap a workspace
./install_pecs_workspace.sh "/path/to/workspace"

# Or via CLI
pecs bootstrap-workspace "/path/to/workspace" --repo-root "$(pwd)"

# Verify workspace
pecs verify-workspace "/path/to/workspace"
pecs status "/path/to/workspace"
```

After installing in a workspace, the daemon generates `.pecs/` continuity artifacts automatically.

---

## Development Workflow

```bash
# Common workspace commands
pecs status "/path/to/workspace"        # Daemon health and readiness
pecs refresh "/path/to/workspace"       # Regenerate continuity artifacts
pecs validate "/path/to/workspace"      # Validate determinism and schema
pecs query-pipeline "/path/to/workspace" --terms "my query"

# After PECS install root relocation
pecs rebind-workspace "/path/to/workspace" --upgrade

# Full diagnostics
pecs doctor "/path/to/workspace"
```

---

## Current Status

- **Architecture**: Complete — Workspace Graph, Registry, Evidence Correlation, Navigation Builder, Query Pipeline all implemented and validated for determinism.
- **Daemon**: Healthy with file-watching, topology rebuild, artifact generation, and JSONL logging.
- **Consumer integrations**: Alpha — four adapters implemented, integration validation pending.
- **Documentation**: Complete — architecture baseline, projection spec, component docs, design principles, glossary.
- **Installer**: Full workspace bootstrap with manifest-driven asset deployment, preserve-first upgrades.
- **Known gaps**: Consumer integration validation, Auto-TOC validation, projection quality benchmarking, IPC query endpoint, multi-language line ranges, legacy parallel structure removal.

For the full changelog, see [CHANGELOG.md](CHANGELOG.md). For the detailed architecture specification, see [docs/architecture.md](docs/architecture.md) and [PECS_ARCHITECTURE_BASELINE.md](PECS_ARCHITECTURE_BASELINE.md).
