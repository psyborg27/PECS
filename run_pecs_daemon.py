from __future__ import annotations

import argparse
from pathlib import Path

from run_pecs_pro import PECSProRuntime
from runtime.daemon import WorkspaceContinuityDaemon


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the PECS-PRO workspace continuity daemon."
    )
    parser.add_argument(
        "workspace_root",
        nargs="?",
        default=".",
        help="Path to the workspace root to monitor (default: current directory).",
    )
    parser.add_argument(
        "--dump-workspace-graph",
        action="store_true",
        default=False,
        help="Write workspace_graph.json on each refresh in addition to required validation artifacts.",
    )
    parser.add_argument(
        "--dump-workspace-registry",
        action="store_true",
        default=False,
        help="Write workspace_registry.json on each refresh in addition to required validation artifacts.",
    )
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    runtime = PECSProRuntime(workspace_root=workspace_root)
    components = runtime.initialize()

    daemon = WorkspaceContinuityDaemon(
        workspace_root=workspace_root,
        runtime_session=components["runtime_session"],
        compact_builder=components["compact_builder"],
        dump_workspace_graph=args.dump_workspace_graph,
        dump_workspace_registry=args.dump_workspace_registry,
    )

    daemon.start()


if __name__ == "__main__":
    main()
