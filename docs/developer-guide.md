# Coding Instructions

Keep this file short, operational, and always-on.

Put feature-specific behavior in scoped `.instructions.md` files near the relevant modules.

---

# Environment Bootstrap

Before making code changes:

```bash
cd "/Users/raj/Downloads/auto OCR app"
source .venv/bin/activate

if [[ -f ".pecs/daemon.pid" ]]; then
  pid=$(<.pecs/daemon.pid)

  if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
    echo "PECS daemon already running (pid=$pid)"
  else
    "/Users/raj/Downloads/PECS_PRO_V2_FINAL/pecs_pro/launch_pecs_daemon.sh"
  fi
else
  "/Users/raj/Downloads/PECS_PRO_V2_FINAL/pecs_pro/launch_pecs_daemon.sh"
fi
```

Do not restart the daemon if already active.

---

# Architectural Rules

- Modify only task-relevant modules.
- Prefer extending existing implementations over creating parallel logic.
- Search for existing ownership before introducing:
  - functions
  - services
  - state containers
  - signals
  - APIs
  - utilities
- Keep business logic in owning core modules.
- Keep UI, transport, and caller layers thin.
- Avoid cross-layer leakage of processing logic.
- Preserve public signatures unless explicitly instructed otherwise.
- Minimize changes to application wiring and startup paths.
- For Qt entry-point changes:
  - preserve launch behavior
  - preserve signal wiring
  - preserve initialization order

---

# Code Preservation Rules

Treat all existing code as potentially active unless proven otherwise.

## Never

- delete code because it appears unused
- remove duplicate-looking logic without verifying ownership
- replace large blocks when a targeted patch is sufficient
- truncate edits with placeholders
- silently rewrite unrelated sections
- infer deletion intent from ambiguity

## Always

- preserve displaced logic
- reinsert moved code into its correct scope
- verify imports after refactors
- preserve backward compatibility unless explicitly instructed otherwise
- prefer additive changes over destructive rewrites
- quarantine approved removals instead of hard-deleting when feasible

If logic is moved:

- explicitly state:
  - source location
  - destination location
  - reason for relocation

---

# Patch Discipline

Use small, verifiable edits.

Prefer:

1. localized patches
2. symbol-level edits
3. incremental validation

Avoid:

- file-wide rewrites
- broad formatting churn
- unrelated cleanup
- speculative refactors

After each patch:

- verify references
- verify imports
- verify call sites
- verify signal wiring
- verify startup paths if touched

If a task requires major architectural restructuring:
- stop and explain the required scope before proceeding

---

# File Selection Rules

Prefer active canonical files.

Avoid editing unless explicitly requested:

- backups
- snapshots
- archives
- migration bundles
- `*_next`
- deprecated variants
- generated outputs

When multiple candidate files exist:

- identify the active execution path first

---

# Reference Reading Rules

Minimize context consumption.

Default workflow:

1. read task-local files first
2. perform targeted symbol search second
3. open large reference files only if required

Do not preload:

- manifests
- topology dumps
- chat archives
- generated PECS artifacts

Prefer existing conversation summaries when available.

---

# Testing Rules

Do not invent test inputs.

Use:

- user-provided files
- task-specific samples
- existing regression assets

If no valid sample exists:

- ask for one

Never fabricate:

- execution results
- runtime behavior
- profiling data
- benchmark results
- validation status

Do not claim execution success unless execution was actually performed.

If execution was not performed:
- explicitly state that it was not performed

---

# Audit Rules

Record meaningful architectural or behavioral changes in:

```text
workspace_audit_log.md
```

Include:

- affected modules
- behavioral impact
- migration implications
- compatibility considerations

---

# Packaging Rules

Do not package unless explicitly requested:

- debug assets
- test scripts
- backup files
- migration internals
- temporary outputs
- sample PDFs
- development-only tooling

If shipping logic changes:
- update actively maintained mirrors in the same task

---

# Continuity Rules

Do not read:

- raw AI chat logs
- transcript dumps
- `AI_CHAT_HISTORY.md`

Unless explicitly requested.

Prefer:

- compact summaries
- structured continuity artifacts
- PECS-derived topology context

---

# Response Rules

End each response with:

```text
Progress: done / in-progress / blocked / next-step
```