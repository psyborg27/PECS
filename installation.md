# Installation

This document describes how to install PECS Alpha 1 and bootstrap a workspace. It is implementation-focused.

## Requirements

- Python 3.9 or newer
- `watchdog` Python package
- `pip`, `setuptools`, and `wheel`
- Git
- VS Code (recommended for task integration)

## Supported Platforms

- macOS
- Linux
- Windows 10 / 11

## Recommended Install Location

Install PECS into a stable directory that is not transient:

- `~/Developer/PECS/`
- `~/Applications/PECS/`
- `C:\Users\<USER>\Developer\PECS\`

Do not install from `Downloads`, `Desktop`, `/tmp`, or removable media.

## Fresh Installation

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

## Editable Installation

The repository is intended to be installed in editable mode for CLI and script access.

```bash
python -m pip install -e .
```

## Workspace Bootstrap

Install PECS workspace assets for a target workspace:

```bash
./install_pecs_workspace.sh "/path/to/workspace"
```

Or use the CLI:

```bash
pecs bootstrap-workspace "/path/to/workspace" --repo-root "$(pwd)"
```

This deploys workspace assets and initializes continuity state.

## Verification

After bootstrap, verify the installation:

```bash
pecs doctor
pecs status "/path/to/workspace"
pecs validate "/path/to/workspace"
```

## Daemon Startup

Start the workspace daemon using the installed scripts:

```bash
bash .pecs/run_pecs_daemon.sh "/path/to/workspace"
```

Or use the CLI through workspace bootstrap assets.

## Workspace Registration

If the PECS install root changes, rebind workspace bindings:

```bash
pecs rebind-workspace "/path/to/workspace" --repo-root "$(pwd)"
```

## Upgrading

After updating PECS, run:

```bash
pecs upgrade-workspace "/path/to/workspace" --repo-root "$(pwd)"
```

## Reinstallation

To reinstall PECS into a new location, clone the repository again and repeat the installation steps. Then rebind or re-bootstrap target workspaces.

## Moving PECS Installation

If the repository moves, update workspace bindings:

```bash
pecs rebind-workspace "/path/to/workspace" --repo-root "$(pwd)"
```

## Rebiding Workspaces

To refresh all bound workspaces after a repository move:

```bash
pecs rebind-all-workspaces --repo-root "$(pwd)"
```

## Uninstallation and Cleanup

PECS does not provide a dedicated uninstall command. Remove the install directory and workspace asset deployments as needed.

Recommended cleanup steps:

- stop the daemon with `pecs stop-daemon "/path/to/workspace"`
- remove `.pecs/` from target workspaces if no longer needed
- remove installed workspace assets

## Common Installation Problems

- **Missing Python 3.9+**: ensure the correct interpreter is active.
- **Daemon does not start**: verify workspace root and `.pecs/run_pecs_daemon.sh` permissions.
- **Workspace assets not applied**: rerun `pecs bootstrap-workspace` or `pecs install-workspace-assets`.
- **Legacy install root**: use `pecs rebind-workspace` or `pecs rebind-all-workspaces`.

## Notes

This document describes the current Alpha 1 installation workflow only.
