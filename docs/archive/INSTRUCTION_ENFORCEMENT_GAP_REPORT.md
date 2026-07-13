# Instruction Enforcement Gap Report

## Current instruction enforcement artifacts

### Copilot guidance
- `.github/copilot-instructions.md`
  - explicitly instructs: inspect `.pecs/active_context.json`, `.pecs/locality_index.json`, `.pecs/active_topology.json`
  - says: "Query PECS-LITE for runtime target projection"
  - emphasizes: "Use PECS artifacts ONLY to narrow locality and identify runtime targets"
  - labels `.pecs` as infrastructure only and not editable source

### Continue routing
- `.continue/config.yaml`
  - always applies `rules/pecs-first-routing.yaml`
- `.continue/rules/pecs-first-routing.yaml`
  - enables `pecs_enabled: true`
  - sets `pecs_priority: high`
  - lists `.pecs/active_context.json`, `.pecs/locality_index.json`, `.pecs/topology_compact.json`, `.pecs/session_context.json`
  - states fallback behavior: repository search only if PECS insufficient

### PECS authority advice
- `.continue/rules/PECS_CONTEXT_RULE.md`
  - defines PECS-PRO authority and PECS-LITE projection roles
  - directs agents to target runtime workspace modules, not `.pecs`
- `.continue/rules/PECS_APPEND_RULE.md`
  - defines chat history append process
  - encourages `python3 .pecs/tools/append_ai_chat_history.py` usage

### VS Code and workspace task integration
- `.vscode/tasks.json` provides explicit PECS start/stop/refresh/validate tasks
- `.vscode/settings.json` sets `pecs.contextPath` to `.pecs/active_context.json`

## Enforcement status

- `Copilot` instructions are explicit but advisory.
- `Continue` routing is explicit and has a high-priority rule.
- There is no internal runtime enforcement in the repository that forbids grep/search.
- No code path guarantees that Copilot or Continue will honor the instructions.

## Evidence of partial enforcement

- `integrations/copilot_adapter.py` and `integrations/continue_adapter.py` exist and implement the intended query adapter paths.
- `topology/retrieval/topology_retriever.py` supports `build_minimal_context()` and fallback semantics.
- `install_workspace_integration.py` installs `.github/copilot-instructions.md`, `.continue/config.yaml`, and `.continue/rules/pecs-first-routing.yaml`.

## Explicit requirements in current instructions

- The instruction files explicitly require PECS querying in guidance form.
- They require retrieving and inspecting PECS artifacts before edits.
- They do not require displaying retrieved context in a machine-verifiable way.
- They do not prove PECS was consulted except by providing the instruction itself.
- They do not prevent blind grep recursion strictly; only discourage it.

## Missing enforcement points

- No runtime hook or middleware is present inside this repo that intercepts Copilot/Continue search and blocks non-PECS search.
- There is no `pecs` API endpoint in the repository that Copilot must call.
- `TopologyRetriever` permits `allow_semantic_fallback=True`, meaning low-confidence or alternative retrieval may still be used.
- `.continue/rules/pecs-first-routing.yaml` explicitly allows fallback to repository search if PECS is insufficient.
- `.github/copilot-instructions.md` is not a hard rule; it is a user-level guidance file.

## Why agents still perform large grep scans

- The core integration is advisory, not enforced: external agents can ignore `.github/copilot-instructions.md`.
- Continue may still perform repository search after PECS artifacts are loaded, because fallback is built into the rule.
- The actual LLM agent invocation chain is external to this repo; this repo cannot force the agent to use PECS.
- The PECS adapter code is not directly connected to GitHub Copilot internals in a compiled callback; it is a pattern for middleware.
- If `.pecs` artifacts are stale, incomplete, or unavailable, the existing rules allow broad search.

## Recommended enforcement modifications

1. Add a hard guard in `.continue/rules/pecs-first-routing.yaml` and alias it with a strict mode that denies broad search until PECS artifacts are loaded.
2. Add a `Copilot` instruction section requiring explicit context quote or artifact path citation in the assistant response when `.pecs` data is used.
3. Implement a runtime validation step in the external integration that logs whether `.pecs` artifacts were actually consulted.
4. Add `pecs.retrieval_used` telemetry fields in `TopologyRetriever` and the `PECSProQueryAdapter` output.
5. Create a VS Code task or command `PECS: Ensure PECS Query Used` that checks `.pecs/daemon_health.json` and `locality_index.json` before edits.
6. Add stricter adapter mode flags: use `allow_semantic_fallback=False` for production guidance and `enforce=True` for edit-critical operations.
7. Surface missing or stale `.pecs` artifact warnings in the `workspace_bridge_cli.py status` command.

## Conclusion

The current instruction set is explicit and well-formed, but it remains a guidance layer. The implementation relies on external agent behavior and plugin support, so agents may still perform large repository scans if the external tooling or the model ignores the guidance.
