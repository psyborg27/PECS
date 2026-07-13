# Copilot Workspace Instructions — PECS v2 Architecture

PECS artifacts are generated continuity infrastructure only.
They do NOT contain editable engineering sourcecode.

## Authority Model

PECS-PRO owns and maintains:
- runtime topology reconstruction
- execution graph continuity
- workspace state truth
- continuity persistence

PECS-LITE is a stateless projection layer:
- queries PECS-PRO
- returns compact locality guidance
- never owns topology or state
- never runs as independent daemon

## Before Suggesting Edits

Inspect these authoritative files when present:
- .pecs/active_context.json (PECS-PRO context)
- .pecs/locality_index.json (PECS-PRO locality)
- .pecs/active_topology.json (PECS-PRO topology)
- .continue/rules/CONTINUITY_MAP.md (if present)

Copilot guidance:
1. Live workspace runtime modules are authoritative and editable
2. Use .pecs artifacts ONLY to narrow locality and identify runtime targets
3. Never edit .pecs files or treat them as sourcecode
4. Query PECS-LITE for runtime target projection
5. Respect execution neighborhood and continuity hints
6. Trust PECS-PRO topology over ad-hoc repository search

## Editing Rules

- Target only live workspace runtime modules for changes
- Use PECS-LITE locality guidance to narrow search scope
- Do NOT edit .pecs infrastructure files
- Do NOT treat PECS artifacts as authoritative sourcecode
- When in doubt, rely on PECS-PRO continuity authority
- Use accepted engineering continuity chains to continue prior accepted locality
- Downrank repeatedly rejected locality before proposing edits

## Environment

When running workspace commands, prefer:
```
cd "${workspaceFolder}"
if [[ -f .venv/bin/activate ]]; then source .venv/bin/activate; fi
```

For chat continuity tracking:
```
python3 .pecs/tools/append_ai_chat_history.py "${workspaceFolder}" \
  --source copilot --message "<summary>"
```

## PECS-LITE Adaptive Projection Profiles

PECS-LITE adapts locality projection richness based on model constraints.
Projection profile selection belongs to middleware/client integrations, NOT PECS.

### Profile Selection for Copilot

**Default Profile: MEDIUM**
- Suitable for Claude/GPT-4 class reasoning models
- Default: `projection_profile: medium` unless overridden
- Receives: 3-6 primary targets, execution adjacency hints
- Token efficiency: ~2000-3000 tokens

**For Small Models (if using local/constrained models):**
- Override: `projection_profile: small`
- Receives: 1-3 primary targets, 1-2 secondary candidates
- Focus: extreme execution-locality precision
- Token efficiency: ~850-1500 tokens

**For Very Large Models:**
- Override: `projection_profile: large`
- Receives: fuller execution-locality relationships + bounded richness
- Focus: structured continuity exploration
- Token efficiency: ~4000-8000 tokens

### Important

- COPILOT DOES NOT INFER MODEL CAPABILITY
- Profile selection is YOUR responsibility
- Default (medium) is conservative and well-tested
- Always verify projected targets make sense for your edit scope
- When uncertain, use profile: medium

## Engineering Continuity Principle

PECS preserves structured accepted engineering continuity only:
- accepted locality
- rejected locality chains
- continuity confidence
- unresolved engineering locality tensions

PECS does NOT preserve raw conversational transcripts as projection context.
Use confidence-aware continuity signals as probabilistic guidance.

## Important

- This file is guidance for PECS integration, not authoritative sourcecode
- PECS improves locality certainty but does not replace reasoning
- Always verify changes against actual runtime behavior
- Test before committing


<!-- ASSET:copilot_instructions -->
# Copilot Instructions — PECS Workspace Integration

## PECS IS CONTINUITY INFRASTRUCTURE

PECS artifacts are generated continuity infrastructure only.
They do NOT contain editable engineering sourcecode.
Runtime workspace modules are the authoritative implementation.

## Decision Guidance

Before suggesting or applying edits, inspect these files when present:

- `.pecs/active_context.json` — Continuity-local execution context
- `.pecs/compact_bundle.json` — Compressed continuity snapshot
- `.pecs/session_context.json` — Session-specific context
- `.pecs/locality_index.json` — Locality projection index
- `.continue/rules/CONTINUITY_MAP.md` — Continuity guidance map (if present)

### 1. Authority Order

1. Live workspace runtime modules
2. PECS locality projection and continuity artifacts
3. Historical chat memory

### 2. Locality & Targeting

- Use `.pecs` to identify runtime target files and execution locality
- Do not treat `.pecs` paths as editable targets
- Prefer runtime workspace files for actual code edits
- Avoid patching or editing `.pecs` files

### 3. Context Narrowing

- Narrow scope with PECS locality data
- Verify candidate edits against live code
- Use filesystem search only after runtime locality is understood

## Command Execution

When running workspace commands, always activate the environment:

```bash
cd "${workspaceFolder}"
if [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
fi
```

For PECS-specific operations:

```bash
python3 .pecs/tools/append_ai_chat_history.py "${workspaceFolder}" \
  --source copilot \
  --message "Summary of changes"
```

## Chat Continuity

After significant Copilot interactions:

```bash
python3 .pecs/tools/append_ai_chat_history.py "${workspaceFolder}" \
  --source copilot \
  --message "Description of work completed"
```

## Principle

- Live runtime workspace modules are authoritative
- PECS artifacts are continuity infrastructure only
- Use PECS for locality/projection, not for source edits
- Do not edit or patch continuity artifacts

## Errors and Warnings

### If PECS Artifacts Are Missing

Copilot will continue to work, but:
- Search will be broader (filesystem-based)
- Context narrowing will be less effective
- Run `pecs repair-workspace` to recover assets

### If PECS Artifacts Are Stale

- The daemon may have stopped
- Run `pecs status`
- Run `pecs refresh-workspace`

## Useful PECS Commands

```bash
# Check status
pecs status

# Refresh artifacts
pecs refresh-workspace $(pwd)

# Validate continuity
pecs verify-workspace $(pwd)

# Diagnose issues
pecs doctor

# Repair installation
pecs repair-workspace $(pwd)
```

## Notes

- This file is installed by the PECS workspace installer
- Do NOT delete or edit `.pecs` files
- PECS is a locality projection layer, not editable sourcecode
