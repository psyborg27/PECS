# PECS File-Class-Function Resolution Design

## Objective

Design a deterministic resolution path from engineering activity to:

- File
- Class
- Function
- PECS_ID

using only existing PECS architecture and no LLM inference.

## Summary

PECS can resolve file-level object identity deterministically in the current workspace using `locality_index.json` and normalized file paths.

Class- and function-level resolution is also possible in many cases, but only when structured evidence exists or when deterministic symbol matching can be applied.

The answer is: **PARTIAL**

### Justification

- `locality_index.json` already contains canonical `PECS_ID:` objects with `file`, `class`, and `method` metadata.
- `append_ai_chat_history.py` can accept structured locality hints and preserve `object_ids`.
- `integrations/pecs_pro_query_adapter.py` already provides deterministic symbol lookup and AST fallback helpers.
- runtime activation artifacts already provide object-level anchors.

However, not all engineering activity carries enough deterministic information to unambiguously select a single function-level object.

## Existing architecture used

- `.pecs/locality_index.json`
- `append_ai_chat_history.py`
- `integrations/pecs_pro_query_adapter.py`
- `runtime/runtime_activation_events.py`
- `runtime/daemon/workspace_continuity_daemon.py`
- `topology/indexing/locality_index.py`

## Resolution strategy per source

### 1. Git diffs

#### File resolution

- Normalize changed file paths to workspace-relative form.
- Use `.pecs/locality_index.json` to map `file` metadata to canonical object IDs.
- If a file appears in multiple `PECS_ID:` entries, retain all same-file candidates.

#### Class resolution

- If diff metadata includes class names, match those names against `class` values in `locality_index.json`.
- If not, enumerate classes from the file via AST using the existing `_bounded_ast_symbols()` helper.
- If the diff includes a changed symbol name, choose the exact matching class or method.

#### Function resolution

- If diff hunks include line numbers, use AST-based line-range ownership to map lines to the enclosing function or method.
- If the diff references a symbol name, choose the exact method/function from the file's AST symbol table.
- If the file contains multiple candidate functions and no line/symbol hint exists, use a deterministic fallback order:
  - exact name match to any hint
  - smallest enclosing AST node by line range
  - sorted candidate list by `(class, function)`

#### Confidence

- File: high
- Class: medium-high when hints exist, medium otherwise
- Function: medium when line/symbol hint exists, low otherwise

### 2. AI edit reports

#### File resolution

- Prefer explicit `correlation.file`, `correlation.target_file`, or `correlation.changed_files`.
- Resolve those files against `.pecs/locality_index.json`.
- If the report includes a direct `PECS_ID:` anchor, preserve it.

#### Class resolution

- Prefer explicit `correlation.class` or `correlation.target_class`.
- Otherwise infer from `correlation.symbol` if present.
- Use `locality_index.json` entries for the resolved file to match the class name.
- If only file is present, use AST symbol enumeration and exact class-name matching.

#### Function resolution

- Prefer explicit `correlation.method`, `correlation.function`, or `correlation.target_function`.
- Otherwise infer from `correlation.symbol` or `correlation.hunk_context`.
- Use `locality_index.json` method metadata to match the canonical object id.
- If multiple functions remain, fallback deterministically to the first matching function by sorted symbol name.

#### Confidence

- File: medium-high when structured metadata exists, medium otherwise
- Class: medium with explicit symbol metadata, low if only inferred
- Function: medium with explicit method metadata, low without it

### 3. Runtime activations

#### File resolution

- Use runtime activation `source` and `target` anchors.
- If they are already `PECS_ID:` forms, these are canonical object ids.
- If they are file-based anchors, normalize and resolve against `.pecs/locality_index.json`.

#### Class resolution

- If runtime anchor resolves to a `PECS_ID:` with `class` metadata, use that class.
- If the anchor resolves only to a file-level object, use the file's symbol metadata and runtime context to choose the most likely class.
- If multiple class candidates exist in the same file, use the activation anchor name or runtime interaction type to narrow them.

#### Function resolution

- If runtime anchor resolves directly to a `PECS_ID:` with `method` metadata, use that method.
- If anchor is file-level, infer method via overlap with active runtime objects in the same file and method metadata in `locality_index.json`.
- If runtime activation provides a callback or signal name, match it to the method name deterministically.

#### Confidence

- File: high
- Class: medium-high when direct object metadata is available, medium otherwise
- Function: medium when method metadata exists, low when only file-level activation exists

### 4. Validation events

#### File resolution

- Use structured fields such as `correlation.attempted_locality`, `correlation.locality`, and `correlation.runtime_authority_candidate`.
- Resolve these hints against `.pecs/locality_index.json` by file path or direct `PECS_ID:` anchor.

#### Class resolution

- If the validation event contains a class or symbol hint, match it to class metadata in `locality_index.json`.
- Otherwise determine candidate classes from the resolved file and the validation locality hint.

#### Function resolution

- Use explicit method or function hints in validation metadata if present.
- Otherwise use deterministic overlap with runtime or git-derived candidates in the same file.
- If multiple candidates remain, select by stable ordered preference:
  - direct hint match
  - line-range ownership when validation can be mapped to a change location
  - sorted `(class, method)` fallback

#### Confidence

- File: medium-high
- Class: medium
- Function: medium-low unless explicit symbol or line-level evidence exists

### 5. Consumer projections

#### File resolution

- The consumer projection already receives a canonical `object_id`.
- Resolve `object_id` to a file via `.pecs/locality_index.json`.
- This is deterministic.

#### Class resolution

- Use the resolved object id's `class` metadata directly from `locality_index.json`.
- If the object id has no class metadata, class resolution is not applicable.

#### Function resolution

- Use the resolved object id's `method` metadata directly from `locality_index.json`.
- If no method metadata exists, function resolution cannot be produced from that object id.

#### Confidence

- File: very high
- Class: very high when metadata exists, not applicable otherwise
- Function: very high when metadata exists, not applicable otherwise

## Deterministic candidate selection rules

When multiple candidate classes/functions exist, PECS should resolve deterministically as follows:

1. Exact symbol match
   - If the event provides an exact class or method name, prefer candidates whose `class` or `method` metadata matches exactly.

2. Line-range ownership
   - For git diffs or instrumented validation events with line numbers, use AST line-range mapping to choose the enclosing function/method.
   - This is deterministic and does not depend on semantics.

3. Symbol lookup
   - If a symbol string is available, use AST symbol enumeration and `locality_index.json` metadata to match the symbol.
   - Existing architecture already supports AST symbol extraction for file-level symbol lists.

4. Runtime activation overlap
   - Prefer candidates that are active in current runtime context or present in the same runtime activation neighborhood.
   - Use exact `PECS_ID:` runtime anchors first.

5. Validation locality overlap
   - Prefer candidates whose file/class/method metadata overlaps with validation locality hints.
   - If multiple objects share the same file, deterministic fallback to sorted order is used.

6. Stable fallback order
   - If evidence remains ambiguous, choose deterministically by stable sort order:
     - `file` path ascending
     - `class` name ascending
     - `method` name ascending
   - Do not choose randomly.

## Can File → Class → Function be resolved entirely from current workspace state and locality_index.json?

### Answer: PARTIAL

#### Why not YES

- `locality_index.json` does not always contain complete class and method metadata for every file.
- Some engineering signals provide only file-level evidence and no exact symbol hints.
- Function-level resolution without explicit symbol or line-range evidence is ambiguous in files with multiple classes/functions.

#### Why not NO

- Deterministic file resolution is already strong.
- Class/function resolution is supported by existing architecture when the event carries structured hints or when AST-based symbol lookup is available.
- Many sources can therefore be resolved without manual tagging or LLM inference.

## Practical implementation plan

### Use current workspace state

- `locality_index.json` for canonical `PECS_ID:` objects and metadata.
- file normalization and file map helpers from `integrations/pecs_pro_query_adapter.py`.
- AST symbol extraction from existing `_bounded_ast_symbols()`.

### Add deterministic resolution paths

- `Git diffs`:
  - use diff paths and line numbers to map to file/class/function
  - if exact symbol hint exists, match against `locality_index.json`

- `AI edit reports`:
  - use explicit structured metadata fields
  - resolve exact symbols before falling back to file-level candidates

- `Runtime activations`:
  - use `PECS_ID:` anchors when available
  - when not, resolve file-level anchors and then the best matching class/method by activation overlap

- `Validation events`:
  - resolve structured locality hints to canonical object IDs
  - use deterministic fallback on sorted candidate sets

- `Consumer projections`:
  - directly use the explicit canonical `object_id`
  - resolve metadata from `locality_index.json`

### Deterministic fallback

- For ambiguity, prefer exact matches.
- Then use line-range ownership.
- Then use runtime/validation overlap.
- Finally use stable sorted fallback.

## Confidence matrix

| Source | File | Class | Function |
|---|---|---|---|
| Git diffs | high | medium-high | medium (line-range available) / low (none) |
| AI edit reports | medium-high | medium | medium (only with explicit symbol names) |
| Runtime activations | high | medium-high | medium |
| Validation events | medium-high | medium | low-medium |
| Consumer projections | very high | very high | very high |

## Key conclusion

PECS can generate canonical function-level object IDs from deterministic engineering evidence in many practical cases.

The result is **PARTIAL** because full resolution depends on the presence of structured hints or line-level evidence; purely file-level or prose-only signals are not sufficient for unambiguous function-level mapping without additional instrumentation.
