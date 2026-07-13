# Workspace Registry

The Workspace Registry identifies user-facing **Features** versus **Infrastructure Units** from deterministic evidence. It provides a stable, hashed registry that projection engines consume, and indexes nodes by their containing feature/unit membership.

## Implementation

- File: `workspace_registry/models.py`
- Core classes: `WorkspaceRegistry`, `WorkspaceFeature`, `WorkspaceInfrastructureUnit`, `WorkspaceEvidence`, `WorkspaceRegistryMetadata`
- Classification values: `user_facing`, `infrastructure`

### Evidence fields

- Boolean flags: `package_locality`, `module_naming_locality`, `public_ui_registration`, `controller_ownership`, `import_export_locality`, `runtime_evidence`, `graph_topology_validated`
- Counts: `package_depth`, `ui_anchor_count`, `controller_count`, `support_module_count`, `observed_activation_count`, `inbound_feature_count`

## Construction

- File: `workspace_registry/builders/workspace_registry_builder.py`
- `WorkspaceRegistryBuilder.build(graph)`:
  1. Uses `FeatureIdentifier` to derive candidates from the graph.
  2. Classifies each candidate as `user_facing` or `infrastructure`.
  3. Computes confidence via weighted evidence + tanh normalization.
  4. Generates aliases.
  5. Links infrastructure units to the features they support based on shared node membership.
  6. Computes a deterministic `registry_hash`.

## Feature Classification Rules

A candidate is user-facing if it has at least one of:

- `public_ui_registration` evidence
- both `controller_ownership` and `runtime_evidence`
- its root node is in `graph.entrypoints`
- its root node name matches user-facing naming patterns (e.g., `dialog`, `viewer`, `workflow`)

Otherwise it is infrastructure.

## Deterministic Guarantees

- `registry_hash` is stable across repeated builds from the same graph.
- `WorkspaceRegistry.to_dict()` and `from_dict()` preserve the hash.

## Runtime Registry Hydration

The installer seeds a runtime registry at `~/.pecs/runtime_registry.json` with canonical keys for governance runtime, modes, and retrieval priority. This registry is advisory hydration: missing entries do not hard-fail the runtime. The canonical retrieval priority is:

1. `workspace_locality`
2. `topology`
3. `ownership`
4. `governance_runtime`
5. `modes`

See [installation.md](installation.md) for bootstrap and rebind behavior.
