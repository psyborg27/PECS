# PECS Alpha 1 Finalization

This document describes the Alpha 1 release preparation process for the current implementation.

## Alpha Release Process

The Alpha 1 release is completed when the repository has:

- a proper landing `README.md`
- current architecture documentation
- an installation guide aligned to the implemented setup
- an upgrade guide aligned to the implemented CLI path
- workflow guidance for daily use
- a set of generated artifact and output documents
- a legal notice that clarifies experimental status
- a man page or command reference for every implemented CLI command
- a repository cleanup report identifying duplicate or obsolete docs

## Pre-release Checklist

- [ ] Confirm `README.md` reflects current implementation only.
- [ ] Confirm `docs/ARCHITECTURE.md` is accurate for current code.
- [ ] Confirm `docs/INSTALLATION.md`, `docs/UPGRADE.md`, and `docs/WORKFLOW.md` match implemented commands.
- [ ] Confirm workspace asset and daemon paths are accurately documented.
- [ ] Confirm all documentation files are present in `docs/index.md`.

## Validation Checklist

- [ ] Run `pecs doctor` from the repository root.
- [ ] Run `python3 -m unittest discover -s tests -p "test_*.py" -v`.
- [ ] Confirm `workspace_bridge_cli.py` contains every documented command.
- [ ] Confirm no document describes features not present in the repository.
- [ ] Confirm `.pecs/` is referenced as generated infrastructure only.

## Test Checklist

- [ ] Validate the existing test suite passes for the repository.
- [ ] Confirm no documentation change requires new Python behavior.
- [ ] Confirm documentation references reflect current CLI output and options.

## Documentation Checklist

- [ ] Update `README.md` to a concise repository entry point.
- [ ] Create `docs/index.md` as a doc landing page.
- [ ] Create `docs/LEGAL.md` with experimental disclaimer language.
- [ ] Create `docs/CONFIGURATION.md`, `docs/OUTPUTS.md`, `docs/FINALIZATION.md`, `docs/FAQ.md`, and `docs/MAN_PAGES.md`.
- [ ] Confirm `docs/INSTALLATION.md` and `docs/WORKFLOW.md` describe actual commands.
- [ ] Confirm every command in `docs/MAN_PAGES.md` exists in `workspace_bridge_cli.py`.

## Installer Checklist

- [ ] Confirm `docs/INSTALLATION.md` documents bootstrap, upgrade, rebind, and cleanup.
- [ ] Confirm workspace asset files and `.pecs/` bridge script locations are described.
- [ ] Confirm workspace install examples use current CLI commands and scripts.

## Upgrade Checklist

- [ ] Confirm `docs/UPGRADE.md` documents `upgrade-workspace`, `rebind-workspace`, and `rebuild-*` commands.
- [ ] Confirm upgrade advice includes backups and rollback guidance.
- [ ] Confirm compatibility notes mention Alpha 1 limitations.

## Artifact Verification

- [ ] Confirm `docs/OUTPUTS.md` lists current `.pecs/` files and optional dumps.
- [ ] Confirm artifact ownership and consumer roles are described.
- [ ] Confirm no artifact description claims unsupported behavior.

## Release Checklist

- [ ] Tag the repository with `v1.0.0-alpha1` or equivalent.
- [ ] Verify the release tag points to the implementation described in docs.
- [ ] Confirm the tag is accompanied by a release note referencing Alpha 1 limitations.

## Git Tagging Checklist

- [ ] Create a Git tag for the Alpha 1 commit.
- [ ] Verify tag naming is consistent with semantic alpha releases.
- [ ] Confirm the tag is based on the current branch and documentation set.

## Recommended Repository Cleanup

- [ ] Identify duplicate documents and archive candidates.
- [ ] Document deprecated artifacts and docs without removing them.
- [ ] Keep the repository focused on current implementation.

## Future Release Workflow

For future releases, use this process:

1. update implementation code
2. update documentation in `docs/`
3. verify existing tests
4. run `pecs doctor`
5. confirm CLI and artifact output
6. update `docs/index.md` and release metadata

## Notes

This document is a release preparation guide for Alpha 1. It does not introduce new functionality or require code changes.
