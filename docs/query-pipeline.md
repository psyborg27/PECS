# Query Pipeline

The Query Pipeline exposes the full flow `query terms → Evidence Correlation → Cluster Selection → Navigation Graph → JSON response` via the CLI. It loads or builds required artifacts deterministically.

## CLI Entry Point

- Entry point: `workspace_bridge_cli.py`, subcommand `query-pipeline`
- Command: `pecs query-pipeline [workspace_root] --terms TERM ...`

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `workspace_root` | `.` | Target workspace |
| `--terms` | required | Query term, repeatable; multi-word values are split on whitespace |
| `--max-clusters` | 3 | Maximum evidence clusters to select |
| `--max-nodes` | 40 | Maximum navigation graph nodes |
| `--max-depth` | 2 | Maximum graph expansion depth |
| `--output` | stdout | File to write JSON result |
| `--use-dumps` | false | Prefer daemon-written `workspace_graph.json` / `workspace_registry.json` |

## Artifact Loading Strategy

1. Requires `.pecs/locality_index.json` and `.pecs/topology_compact.json`.
2. If `--use-dumps` and `.pecs/workspace_graph.json` exist, load it; otherwise rebuild the graph from locality/topology.
3. If `--use-dumps` and `.pecs/workspace_registry.json` exist, load it; otherwise rebuild the registry from the graph.
4. Build the evidence index, correlate, select clusters, build navigation graph.
5. Emit JSON with schema `pecs.query_pipeline.v1`.

## Lifecycle Records

The command appends `query_pipeline_started`, `query_pipeline_completed`, and `query_pipeline_failed` events to `.pecs/logs/lifecycle_commands.jsonl`.

## Query Contract

A canonical PECS query is a JSON envelope containing consumer metadata, model metadata, profile/projection directives, workspace context, task framing, locality expectations, execution semantics, and constraints.

### Mandatory fields

- `query_id`: unique per request
- `consumer`: `copilot`, `continue`, `kimi`, `commandcode`, or `other`
- `workspace_id`: workspace identifier or path hash
- `projection_profile`: profile instructions for PECS-LITE
- `task_type`: `bug_fix`, `feature_addition`, `refactor`, `inspection`, `validation`, `documentation`, or `other`
- `issue`: primary issue, feature request, or task description
- `execution_mode`: `development`, `inspection`, `repair`, `test`, `review`, or `analysis`
- `constraints`: hard constraints such as max targets, token budget, or exploration budget
- `timestamp`: ISO8601 timestamp

### Required projection profile fields

- `profile`: `large`, `medium`, `small`, or `execution`
- `reasoning_budget`: `low`, `medium`, `high`, or `very_high`
- `exploration_constraints`: `strict`, `bounded`, or `expanded`
- `target_count`: suggested maximum projected candidates
- `continuity_depth`: `minimal`, `balanced`, or `deep`
- `include_advisories`: whether to include advisory commentary

### Response sections

A PECS response includes:

- `PECS_Status`: consultation state, artifact availability, fallback reason
- `PECS_Query`: echoed query metadata
- `PECS_Response`: runtime targets, secondary neighbors, continuity/validation/locality/divergence evidence, advisory cognition, diagnostics
- `PECS_Confidence`: authority confidence, tier contributions, evidence balance
- `Relying_On_PECS`: whether projection/continuity were authoritative
- `Reason`: high-level justification

## Relationship to Other Components

- The [Workspace Graph](workspace-graph.md) provides nodes and edges.
- The [Workspace Registry](workspace-registry.md) provides feature/unit classification.
- The [Evidence Correlation Engine](evidence-correlation.md) ranks clusters.
- The [Navigation Builder](navigation-builder.md) builds the projected subgraph.

See the [integrations/](integrations/) directory for consumer-specific query and projection profiles.
