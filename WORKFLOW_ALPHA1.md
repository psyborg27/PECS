# PECS Alpha 1 Workflow

This document describes the expected workflow for using PECS Alpha 1.

## 1. Setup

1. Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

2. Bootstrap a target workspace:

```bash
pecs bootstrap-workspace "/path/to/workspace" --repo-root "$(pwd)"
```

This installs `.github/`, `.continue/`, and `.pecs/` bridge assets into the workspace.

## 2. Run the daemon

Start the workspace daemon:

```bash
pecs-pro-daemon "/path/to/workspace"
```

Or use the provided helper script:

```bash
bash .pecs/run_pecs_daemon.sh "/path/to/workspace"
```

## 3. Refresh and validate

Refresh runtime continuity state:

```bash
pecs refresh "/path/to/workspace"
```

Validate generated artifacts:

```bash
pecs validate "/path/to/workspace"
```

## 4. Query and observe

Run a query:

```bash
pecs query-pipeline "/path/to/workspace" --terms "entrypoint discovery"
```

Capture an opt-in projection snapshot:

```bash
pecs observe-projection-snapshot "/path/to/workspace" --query "entrypoint discovery" --query-source manual
```

## 5. Troubleshoot

If the workspace is unhealthy:

- Inspect `.pecs/status/`
- Check `.pecs/logs/`
- Re-run `pecs refresh`
- Run `pecs validate`

## 6. Developer feedback

Alpha 1 is designed to be iterated quickly. Report issues as:

- missing entrypoint discovery
- invalid `.pecs` refresh output
- query pipeline misalignment
- projection snapshot failure
