# PECS CLI Manual Pages

This document provides user-facing manual page style reference for the current PECS Alpha 1 CLI commands. Every command listed exists in `workspace_bridge_cli.py`.

## bootstrap-workspace

### NAME
bootstrap-workspace — install, start daemon, refresh continuity, and validate a workspace

### SYNOPSIS
pecs bootstrap-workspace <workspace_root> [--repo-root <repo_root>] [--preserve-user-config]

### DESCRIPTION
Installs PECS workspace assets, starts or binds a daemon, refreshes continuity artifacts, and validates the workspace.

### OPTIONS
- `<workspace_root>` — target workspace root path.
- `--repo-root` — PECS repository root.
- `--preserve-user-config` — preserve local workspace configuration during asset install.

### EXAMPLES
pecs bootstrap-workspace "/path/to/workspace" --repo-root "$(pwd)"

### OUTPUT
Reports install progress, refresh status, and validation results to stdout.

### COMMON ERRORS
- invalid workspace root
- missing repository root
- workspace asset deployment failure

### NOTES
This command is the normal starting point for a new workspace.

## setup-workspace

### NAME
setup-workspace — alias for bootstrap-workspace

### SYNOPSIS
pecs setup-workspace <workspace_root> [--repo-root <repo_root>] [--preserve-user-config]

### DESCRIPTION
Alias to `bootstrap-workspace` with the same behavior.

### OPTIONS
- same as `bootstrap-workspace`

### NOTES
The command exists for compatibility with workspace setup workflows.

## init

### NAME
init — initialize PECS workspace (legacy)

### SYNOPSIS
pecs init <workspace_root> [--repo-root <repo_root>] [--preserve-user-config]

### DESCRIPTION
Legacy initialization command. It is retained for compatibility with older workflows.

### OPTIONS
- same as `bootstrap-workspace`

### NOTES
Use `bootstrap-workspace` for current workflows.

## install-workspace-assets

### NAME
install-workspace-assets — install PECS workspace assets

### SYNOPSIS
pecs install-workspace-assets <workspace_root> [--repo-root <repo_root>] [--preserve-user-config]

### DESCRIPTION
Installs or refreshes managed workspace assets without necessarily performing a full refresh.

### OPTIONS
- same as `bootstrap-workspace`

### NOTES
This command is used when asset deployment needs to be separated from continuity refresh.

## interactive-setup

### NAME
interactive-setup — interactively configure and bootstrap a workspace

### SYNOPSIS
pecs interactive-setup <workspace_root> [--repo-root <repo_root>] [--preserve-user-config]

### DESCRIPTION
Runs an interactive workspace bootstrap flow.

### OPTIONS
- same as `bootstrap-workspace`

## rebind-workspace

### NAME
rebind-workspace — refresh PECS workspace bindings after install root relocation

### SYNOPSIS
pecs rebind-workspace <workspace_root> [--repo-root <repo_root>] [--preserve-user-config]

### DESCRIPTION
Refreshes workspace bridge bindings, launcher scripts, and asset links after the PECS installation root changes.

### OPTIONS
- same as `bootstrap-workspace`

## refresh-workspace-bindings

### NAME
refresh-workspace-bindings — alias for rebind-workspace

### SYNOPSIS
pecs refresh-workspace-bindings <workspace_root> [--repo-root <repo_root>] [--preserve-user-config]

### DESCRIPTION
Alias for `rebind-workspace`.

## migrate-workspace

### NAME
migrate-workspace — migrate workspace bindings to current PECS install root

### SYNOPSIS
pecs migrate-workspace <workspace_root> [--repo-root <repo_root>] [--preserve-user-config]

### DESCRIPTION
Migrates workspace bindings after a PECS repository relocation.

### OPTIONS
- same as `rebind-workspace`

## rebind-all-workspaces

### NAME
rebind-all-workspaces — rebind all registered PECS workspaces to current install root

### SYNOPSIS
pecs rebind-all-workspaces [--repo-root <repo_root>] [--preserve-user-config]

### DESCRIPTION
Updates all registered workspace bindings to the current PECS repository root.

### OPTIONS
- `--repo-root` — PECS repository root.
- `--preserve-user-config` — preserve local configuration.

## verify-workspace

### NAME
verify-workspace — verify workspace installation

### SYNOPSIS
pecs verify-workspace <workspace_root> [--repo-root <repo_root>] [--json]

### DESCRIPTION
Verifies the workspace installation and PECS bridge state.

### OPTIONS
- `<workspace_root>` — target workspace root.
- `--repo-root` — PECS repository root.
- `--json` — output structured JSON.

## repair-workspace

### NAME
repair-workspace — repair broken workspace installation

### SYNOPSIS
pecs repair-workspace <workspace_root> [--repo-root <repo_root>]

### DESCRIPTION
Attempts to repair workspace installation issues.

### OPTIONS
- same as `verify-workspace` without `--json`.

## status

### NAME
status — show daemon and workspace status

### SYNOPSIS
pecs status [<workspace_root>]

### DESCRIPTION
Shows the current PECS daemon and workspace status.

### OPTIONS
- `<workspace_root>` — optional workspace root. Defaults to current directory.

## health

### NAME
health — show authoritative daemon health status

### SYNOPSIS
pecs health [<workspace_root>]

### DESCRIPTION
Displays the authoritative health status of the PECS daemon.

### OPTIONS
- `<workspace_root>` — optional workspace root. Defaults to current directory.

## doctor

### NAME
doctor — diagnose PECS installation and environment

### SYNOPSIS
pecs doctor [<workspace_root>] [--repo-root <repo_root>]

### DESCRIPTION
Diagnoses the local PECS installation and workspace environment.

### OPTIONS
- `<workspace_root>` — optional workspace root. Defaults to current directory.
- `--repo-root` — PECS repository root.

## upgrade-workspace

### NAME
upgrade-workspace — run the canonical PECS workspace upgrade pipeline

### SYNOPSIS
pecs upgrade-workspace <workspace_root> [--repo-root <repo_root>]

### DESCRIPTION
Runs the canonical workspace upgrade pipeline, refreshes managed assets, and validates the workspace.

## refresh-managed-assets

### NAME
refresh-managed-assets — refresh managed PECS workspace assets without wiping continuity

### SYNOPSIS
pecs refresh-managed-assets <workspace_root> [--repo-root <repo_root>] [--preserve-user-config]

### DESCRIPTION
Refreshes installed workspace assets while preserving existing continuity state.

## stop-daemon

### NAME
stop-daemon — stop the PECS daemon for the workspace

### SYNOPSIS
pecs stop-daemon <workspace_root>

### DESCRIPTION
Stops the workspace daemon associated with the target workspace.

## restart-daemon

### NAME
restart-daemon — restart the PECS daemon for the workspace

### SYNOPSIS
pecs restart-daemon <workspace_root>

### DESCRIPTION
Restarts the workspace daemon.

## rebuild-continuity

### NAME
rebuild-continuity — regenerate derived continuity artifacts without destructive reset

### SYNOPSIS
pecs rebuild-continuity <workspace_root> [--repo-root <repo_root>]

### DESCRIPTION
Regenerates continuity artifacts from existing workspace state.

## rebuild-topology

### NAME
rebuild-topology — refresh runtime and topology artifacts without destroying continuity

### SYNOPSIS
pecs rebuild-topology <workspace_root> [--repo-root <repo_root>]

### DESCRIPTION
Refreshes topology and runtime-derived artifacts while keeping continuity state intact.

## safe-migration

### NAME
safe-migration — alias for rebind-workspace with preserve-first behavior

### SYNOPSIS
pecs safe-migration <workspace_root> [--repo-root <repo_root>] [--preserve-user-config]

### DESCRIPTION
Alias for `rebind-workspace` that emphasizes preserve-first migration semantics.

## refresh

### NAME
refresh — refresh continuity state (continuity bootstrap)

### SYNOPSIS
pecs refresh <workspace_root> [--repo-root <repo_root>]

### DESCRIPTION
Refreshes continuity artifacts for the workspace.

## hydrate-workspace

### NAME
hydrate-workspace — hydrate workspace continuity from chat history and runtime artifacts

### SYNOPSIS
pecs hydrate-workspace <workspace_root> [--repo-root <repo_root>]

### DESCRIPTION
Hydrates continuity state from existing chat history and runtime artifacts.

## validate

### NAME
validate — validate continuity state

### SYNOPSIS
pecs validate <workspace_root> [--repo-root <repo_root>]

### DESCRIPTION
Validates the workspace continuity artifacts and reports any inconsistencies.

## query-pipeline

### NAME
query-pipeline — run query terms through Evidence Correlation → Navigation Graph

### SYNOPSIS
pecs query-pipeline [<workspace_root>] --terms <term> [--terms <term> ...] [options]

### DESCRIPTION
Runs a query through the current evidence correlation and navigation builder pipeline.

### OPTIONS
- `--terms` — query terms, repeatable.
- `--max-clusters` — maximum evidence clusters to select.
- `--max-nodes` — maximum navigation graph nodes.
- `--max-depth` — maximum expansion depth.
- `--output` — write JSON result to a file.
- `--prefer-daemon-dumps` — prefer `.pecs/workspace_graph.json` and `.pecs/workspace_registry.json` dumps.

## observe-projection-snapshot

### NAME
observe-projection-snapshot — capture one optional emitted-envelope projection snapshot

### SYNOPSIS
pecs observe-projection-snapshot <workspace_root> --model-name <name> --profile-class <class> --local-vs-frontier <value> [options]

### DESCRIPTION
Captures a one-off projection snapshot for analysis.

### OPTIONS
- `--query`
- `--query-source`
- `--model-name`
- `--model-source`
- `--provider`
- `--model-size`
- `--profile-class`
- `--local-vs-frontier`
- `--reasoning-capability-class`
- `--context-window`
- `--session-id`
- `--max-records`

## observe-projection-daemon

### NAME
observe-projection-daemon — capture bounded optional emitted-envelope projection snapshots

### SYNOPSIS
pecs observe-projection-daemon <workspace_root> --model-name <name> --profile-class <class> --local-vs-frontier <value> [options]

### DESCRIPTION
Runs repeated projection observations over time for a workspace.

### OPTIONS
- same as `observe-projection-snapshot`

## Notes

Use `pecs <command> --help` for detailed option syntax and the latest command metadata.
