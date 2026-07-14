# Upgrade Guide

This document describes the current PECS Alpha 1 upgrade process.

## Upgrade Workflow

To upgrade a workspace after updating the PECS repository, run:

```bash
pecs upgrade-workspace "/path/to/workspace" --repo-root "$(pwd)"
```

The upgrade process:

1. refreshes workspace assets
2. regenerates continuity artifacts
3. verifies workspace installation
4. validates continuity outputs

## Asset Migration

To refresh managed workspace assets without resetting continuity state:

```bash
pecs refresh-managed-assets "/path/to/workspace" --repo-root "$(pwd)"
```

To install workspace assets explicitly:

```bash
pecs install-workspace-assets "/path/to/workspace" --repo-root "$(pwd)"
```

## Workspace Preservation

To preserve local workspace settings during asset updates, use:

```bash
pecs install-workspace-assets "/path/to/workspace" --repo-root "$(pwd)" --preserve-user-config
```

Many commands support `--preserve-user-config` to keep existing workspace configuration when refreshing assets.

## Backups and Rollback

PECS Alpha 1 does not provide a formal rollback command. Use version control for rollback and inspect workspace asset backups if available.

If workspace assets are updated, preserve or copy `.pecs/` state and local workspace files before retrying.

## Rebind

If the repository root changes, update workspace bindings:

```bash
pecs rebind-workspace "/path/to/workspace" --repo-root "$(pwd)"
```

To rebind all registered workspaces after a repository move:

```bash
pecs rebind-all-workspaces --repo-root "$(pwd)"
```

`rebind-workspace` refreshes bridge scripts and workspace asset links.

## Validation

After upgrade, validate the workspace:

```bash
pecs validate "/path/to/workspace" --repo-root "$(pwd)"
pecs doctor "/path/to/workspace" --repo-root "$(pwd)"
```

Use `pecs verify-workspace` to inspect installation status.

## Compatibility Between Alpha Releases

PECS Alpha 1 is experimental. Compatibility across Alpha releases is not guaranteed. Always validate workspace state after upgrading and preserve your source and continuity artifacts in version control.

## Notes

- `upgrade-workspace` is the canonical upgrade command in Alpha 1.
- `rebuild-topology` and `rebuild-continuity` refresh derived artifacts without destroying continuity state.
- Deleting `.pecs/` is not recommended unless you plan to re-bootstrap.
- Use `pecs rebind-workspace` after moving the PECS install root.
