# Getting Started with PECS

PECS-PRO v2 provides deterministic, topology-first continuity infrastructure for AI-assisted engineering workspaces. This guide walks through your first install and workspace bootstrap.

## What PECS Does

- Reconstructs runtime topology, execution locality, and ownership relationships from workspace source files.
- Produces a canonical **Workspace Graph**, **Workspace Registry**, and **Evidence Correlation** index.
- Exposes locality projections through a stateless **PECS-LITE** layer for AI consumers such as Copilot, Continue, Kimi, and CommandCode.
- Writes all continuity artifacts under `.pecs/`; live workspace modules remain the authoritative sourcecode.

For the full project overview, purpose, and architecture, see `README.md`.

## Install PECS

Choose a stable location and clone the repository:

```bash
git clone <repo-url> ~/Developer/PECS
cd ~/Developer/PECS
```

Create the virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e .
```

Verify the installation:

```bash
pecs doctor
```

See `README_MANUAL_SETUP.md` and [installation.md](installation.md) for detailed setup options.

## Bootstrap Your First Workspace

The automated installer configures VS Code tasks, Continue rules, Copilot instructions, and `.pecs/` bridge assets:

```bash
./install_pecs_workspace.sh "/path/to/workspace"
```

Or use the CLI directly:

```bash
pecs bootstrap-workspace "/path/to/workspace" --repo-root "$(pwd)"
```

After bootstrap, the daemon generates `.pecs/` continuity artifacts from the workspace source files.

## Daily Workflow

1. **Query PECS first** using `pecs query-pipeline` or your AI consumer's PECS integration.
2. **Edit live runtime workspace modules**, not `.pecs/` files.
3. **Refresh continuity** after significant changes:
   ```bash
   pecs refresh "/path/to/workspace"
   pecs validate "/path/to/workspace"
   ```
4. **Preserve continuity** during upgrades:
   ```bash
   pecs rebind-workspace "/path/to/workspace" --upgrade
   ```

## Next Steps

- [Architecture](architecture.md) — high-level components and data flow
- [Workspace Graph](workspace-graph.md) — canonical graph model
- [Query Pipeline](query-pipeline.md) — CLI query contract
- [Artifacts](artifacts.md) — what `.pecs/` contains
- [Integrations](integrations/) — consumer-specific contracts
- [Troubleshooting](troubleshooting.md) — health checks and repair
