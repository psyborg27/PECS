# PECS MIGRATION PLAN

# STEP 1

Create clean workspace:

```text
project_pecs_test/
```

Never migrate directly into production first.

---

# STEP 2

Create folders:

```text
pecs/core
pecs/ingestion
pecs/continuity
pecs/runtime
pecs/integrations
pecs/tools
pecs/lite
pecs/exports
```

---

# STEP 3

Move consolidated files into new structure.

---

# STEP 4

Delete:
- duplicate runtimes
- duplicate exporters
- duplicate registries
- duplicate scanners
- semantic supervision modules

---

# STEP 5

Run:

```bash
python final_runtime_core.py
```

---

# STEP 6

Inspect:

- pecs_runtime.md
- runtime_context.json
- final_runtime.json

using:
- pecs_testing_console.py

---

# STEP 7

Only after validation:
- enable live daemon
- connect Continue
- connect local models
- connect online models

---

# STEP 8

Use overlays:

```text
pecs/runtime/pro/
pecs/runtime/lite/
```

to isolate:
- authoritative continuity
- lightweight continuity
