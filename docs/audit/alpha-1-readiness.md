# Alpha-1 Readiness Assessment — PECS Core v1 Alpha 1

## Objective

Determine whether the repository is ready for `git tag v0.1.0-alpha1` and identify exactly what remains if not.

---

## Readiness Criteria

| Criterion | Status | Notes |
|---|---|---|
| **Core architecture implemented** | ✅ PASS | Workspace Graph, Registry, Evidence Correlation, Navigation Builder, Query Pipeline all implemented |
| **Daemon operational** | ✅ PASS | Healthy daemon with file-watching, topology rebuild, artifact generation, JSONL logging |
| **Consumer adapters exist** | ✅ PASS | Copilot, Continue, Kimi, Command Code adapters implemented |
| **Installer functional** | ✅ PASS | Manifest-driven installation, preserve-first upgrade, cross-platform launchers |
| **Bridge scripts functional** | ✅ PASS | Refresh, export, validate all working |
| **Documentation complete** | ❌ FAIL | See blockers below |
| **Version consistent** | ❌ FAIL | VERSION = `1.0.0-alpha1`, pyproject.toml = `0.1.0` — must match |
| **Determinism validated** | ✅ PASS | Confirmed: `sort_keys=True`, hash-based dedup, timestamp exclusion |
| **Tests pass** | ⚠️ UNKNOWN | Tests were checked but not executed. Should verify before tagging. |
| **Legacy content archived** | ❌ FAIL | 4 obsolete root documents not yet archived |
| **Docs match implementation** | ❌ FAIL | 1 critical, 1 high-severity discrepancy |

---

## Release Blockers

### Blocker 1: Version Mismatch (HIGH)

`VERSION` file says `1.0.0-alpha1`. `pyproject.toml` says `0.1.0`.

Before tagging, these must be synchronized. Choose one:
- `pyproject.toml` version → `1.0.0-alpha1` (matches VERSION file)
- Both → `0.1.0-alpha1` (honest about pre-release status)

**Recommendation:** Set both to `0.1.0-alpha1`. The VERSION file is the human-readable project version; `pyproject.toml` is the package version. Making them consistent avoids confusion.

### Blocker 2: Developer Guide Corrupted (CRITICAL)

`docs/developer-guide.md` contains Auto-TOC workspace content (paths, rules for Qt signals, etc.) instead of PECS developer guidance. This must be restored before release.

**Required action:** Rewrite `docs/developer-guide.md` with:
- PECS coding conventions (from AGENTS.md)
- Patch discipline
- Module organization
- Testing guidance
- Contribution workflow

### Blocker 3: Obsolete Root Documents Not Archived (MEDIUM)

Four documents at root level describe architectures that were never implemented or are superseded:
- `PECS_AUTHORITY_ENGINE_ARCHITECTURE.md`
- `PECS_FILE_CLASS_FUNCTION_RESOLUTION_DESIGN.md`
- `PECS_OBJECT_ID_PRODUCER_DESIGN.md`
- `PECS_CONSUMER_AUTHORITY_MODEL.md` (partially superseded)

These must be moved to `docs/archive/` before release.

### Blocker 4: Documentation Discrepancy (MEDIUM)

`docs/architecture.md` and `docs/artifacts.md` reference `--dump-workspace-graph` and `--dump-workspace-registry` CLI flags that don't exist in the current daemon implementation. These references must be removed or corrected.

---

## Non-Blocking Items (Can Ship With Alpha-1 Tag)

| Item | Severity | Why Non-Blocking |
|---|---|---|
| **Contract consolidation** | Low | Three contract docs overlap but don't contradict. Consolidation is cleanup, not correctness. |
| **Archive reorganization** | Low | Archive files are already in `docs/archive/`. Subdirectory reorganization is nice-to-have. |
| **AGENTS.md structure sync** | Low | Minor structure list update. Doesn't affect functionality. |
| **Consumer integration validation** | Low | Documented as "in progress" in CHANGELOG. Not a release requirement. |
| **Multi-language line ranges** | Low | Documented as future work. |
| **IPC query endpoint** | Low | Documented as future work. |
| **Legacy parallel structures** | Low | Documented as "not yet migrated" in docs. |

---

## Release Checklist

### Before Tagging

- [ ] Sync `VERSION` and `pyproject.toml` to a consistent version string
- [ ] Restore `docs/developer-guide.md` with canonical PECS developer guidance
- [ ] Move 4 obsolete root documents to `docs/archive/`:
  - `PECS_AUTHORITY_ENGINE_ARCHITECTURE.md`
  - `PECS_FILE_CLASS_FUNCTION_RESOLUTION_DESIGN.md`
  - `PECS_OBJECT_ID_PRODUCER_DESIGN.md`
  - `PECS_CONSUMER_AUTHORITY_MODEL.md`
- [ ] Update `docs/architecture.md` to remove `--dump-workspace-graph`/`--dump-workspace-registry` flag references
- [ ] Update `docs/artifacts.md` to remove `--dump-workspace-graph`/`--dump-workspace-registry` flag references
- [ ] Update `AGENTS.md` repository structure to match current layout
- [ ] Run `python3 -m unittest discover -s tests -v` and confirm all tests pass
- [ ] Tag release: `git tag -a v0.1.0-alpha1 -m "PECS Core v1 Alpha 1"`

### Nice-to-Have Before Tagging

- [ ] Create `docs/audit/` directory and include these deliverables
- [ ] Consolidate `PECS_CANONICAL_QUERY_AND_PROJECTION_CONTRACT.md` + `PECS_QUERY_CONTRACT.md` into one contract document
- [ ] Move `PECS_ARCHITECTURAL_PROJECTION_SPEC.md` → `docs/reference/` if directory is created

### After Tagging

- [ ] Push tag: `git push origin v0.1.0-alpha1`
- [ ] Update `CHANGELOG.md` if any additional fixes land before the tag

---

## Verdict

**The repository is NOT ready for `git tag v0.1.0-alpha1`.** Four blockers must be resolved first. The estimated scope of remaining work is:

| Blocker | Estimated Effort |
|---|---|
| Version sync | 1 edit (2 files) |
| Developer guide restore | 1 file creation (~100 lines) |
| Archive 4 obsolete docs | 4 file moves |
| Fix flag documentation | 2 file edits |
| AGENTS.md structure update | 1 file edit |
| Test suite run | 1 command |

**With these fixes, the repository IS ready for tagging.** No architectural changes, no feature additions, and no code modifications beyond version string updates are required.
