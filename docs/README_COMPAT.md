# PECS Alpha 1 Compatibility Notes

This file documents the compatibility expectations for PECS Alpha 1.

## Supported environments

- Python 3.9+
- macOS, Linux, and Windows PowerShell
- Workspaces containing Python source files

## Requirements

- `watchdog` runtime dependency
- Editable install for CLI entrypoints and daemon scripts
- A workspace root accessible for file watching and artifact writing

## Known limitations

- Alpha 1 does not support non-Python runtime discovery.
- It relies on AST-based import scanning and may miss dynamic import patterns.
- Large monorepos may require tuning before runtime refresh completes.
- `.pecs/` artifacts are workspace-local and not intended for direct editing.

## Upgrade path

- `bootstrap-workspace` adds workspace integration assets.
- Future releases will add a versioned upgrade pipeline.

## Observability

- Use `pecs observe-projection-snapshot` and `.pecs/logs/` for debugging.
- `pecs validate` checks artifact integrity and continuity shape.
