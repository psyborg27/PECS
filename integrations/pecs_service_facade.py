"""PECS Service Facade — thin internal API for adapters.

This facade exposes existing PECS functionality through stable Python methods
without duplicating engineering logic. All business logic lives in the owning
core modules (runtime/, topology/, evidence_correlation/, etc.).

Future adapters (MCP, SDK, VS Code, Cursor, etc.) must consume ONLY this
facade and never import core modules directly.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PECSServiceFacade:
    """Internal service facade for PECS.

    Each method delegates to existing PECS modules. No business logic lives here.
    """

    def __init__(self, workspace_root: Optional[str] = None):
        resolved = Path(workspace_root or Path.cwd()).resolve()
        self.workspace_root: Path = resolved
        self._pecs_dir = self.workspace_root / ".pecs"

    # ------------------------------------------------------------------
    # Helpers (delegating to existing loading utilities)
    # ------------------------------------------------------------------

    def _load_json(self, path: Path, default: Any = None) -> Any:
        if default is None:
            default = {}
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default

    @classmethod
    def _resolve_adapter(cls) -> Any:
        """Import and return a PECSLiteRuntimeAdapter instance."""
        try:
            from integrations.pecs_lite_runtime_adapter import (
                PECSLiteRuntimeAdapter,
            )
        except ImportError:
            try:
                from pecs_pro.integrations.pecs_lite_runtime_adapter import (
                    PECSLiteRuntimeAdapter,
                )
            except ImportError:
                raise RuntimeError("PECS-LITE runtime adapter not available")
        return PECSLiteRuntimeAdapter

    # ------------------------------------------------------------------
    # Tool 1 — pecs_consult
    # ------------------------------------------------------------------

    def consult(self, query: str, profile: str = "medium") -> Dict[str, Any]:
        """Return the current PECS consult response.

        Delegates to PECSLiteRuntimeAdapter.build_projection_safe() — the same
        code path as ``pecs consult`` on the CLI.
        """
        PECSLiteRuntimeAdapter = self._resolve_adapter()
        projection = PECSLiteRuntimeAdapter.build_projection_safe(
            workspace_root=str(self.workspace_root),
            query=query,
            model_name="",
            model_source="",
            context_window=32768,
            model_size="medium",
            provider="",
            profile_class=profile,
            local_vs_frontier="unknown",
            reasoning_capability_class="unknown",
            query_source="mcp",
        )
        return projection

    # ------------------------------------------------------------------
    # Tool 2 — pecs_projection
    # ------------------------------------------------------------------

    def projection(self, projection_id: str = "") -> Dict[str, Any]:
        """Return the detailed projection from the current consult result.

        This reads the projection snapshot from the observation log, or falls
        back to a fresh consult if no projection_id is given.
        """
        if projection_id:
            observation_log = (
                self._pecs_dir / "logs" / "observation" / "projection_snapshot.jsonl"
            )
            if observation_log.exists():
                try:
                    for line in observation_log.read_text(
                        encoding="utf-8"
                    ).splitlines():
                        record = json.loads(line)
                        if record.get("projection_id") == projection_id:
                            return record
                except Exception:
                    pass

        # Fall back to a fresh consult projection
        return self.consult(query="runtime locality")

    # ------------------------------------------------------------------
    # Tool 3 — pecs_explain
    # ------------------------------------------------------------------

    def explain(self, query: str) -> Dict[str, Any]:
        """Return the query explanation that PECS already generates.

        Delegates to the same logic as ``pecs explain-query`` on the CLI:
        parses the query, scans locality and topology artifacts, and returns
        match analysis.
        """
        from pecs_query.query_parser import QueryParser

        parse_result = QueryParser.parse(query)
        query_terms = parse_result.terms

        locality = self._load_json(self._pecs_dir / "locality_index.json", {})
        topology = self._load_json(self._pecs_dir / "topology_compact.json", {})

        locality_matches: List[Dict[str, Any]] = []
        if isinstance(locality, dict):
            for pecs_id, meta in sorted(locality.items()):
                if not isinstance(meta, dict):
                    continue
                text = (pecs_id + " " + str(meta)).lower()
                matching = [t for t in query_terms if t in text]
                if matching:
                    locality_matches.append(
                        {
                            "id": pecs_id,
                            "matched_terms": matching,
                            "file": meta.get("file", ""),
                            "zone": meta.get("runtime_zone", ""),
                        }
                    )

        topology_matches: List[Dict[str, Any]] = []
        if isinstance(topology, dict):
            for edge in topology.get("edges", []):
                if not isinstance(edge, dict):
                    continue
                text = (
                    str(edge.get("from", "")) + " " + str(edge.get("to", ""))
                ).lower()
                matching = [t for t in query_terms if t in text]
                if matching:
                    topology_matches.append(
                        {
                            "from": edge.get("from", ""),
                            "to": edge.get("to", ""),
                            "type": edge.get("type", ""),
                            "matched_terms": matching,
                        }
                    )

        matches = len(locality_matches)
        topo = len(topology_matches)
        confidence = min(
            1.0,
            matches / max(1, len(query_terms)) * 0.5
            + topo / max(1, len(query_terms)) * 0.3,
        )

        return {
            "query": query,
            "parsed_terms": query_terms,
            "sections": dict(parse_result.sections),
            "semantic_hints": dict(parse_result.semantic_hints),
            "locality_matches": locality_matches,
            "locality_match_count": len(locality_matches),
            "topology_matches": topology_matches,
            "topology_match_count": len(topology_matches),
            "confidence": round(confidence, 3),
        }

    # ------------------------------------------------------------------
    # Tool 4 — pecs_health
    # ------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """Return diagnostic health information for the current workspace."""
        pecs_dir = self._pecs_dir

        health_state = self._load_json(pecs_dir / "daemon_health.json", {})
        daemon_state = self._load_json(pecs_dir / "daemon_state.json", {})
        graph_validation = self._load_json(
            pecs_dir / "workspace_graph_validation.json", {}
        )
        registry_validation = self._load_json(
            pecs_dir / "workspace_registry_validation.json", {}
        )

        daemon_pid_file = pecs_dir / "daemon.pid"
        daemon_running = daemon_pid_file.exists()
        daemon_pid = None
        if daemon_running:
            try:
                raw = daemon_pid_file.read_text(encoding="utf-8").strip()
                if raw.isdigit():
                    daemon_pid = int(raw)
            except Exception:
                pass

        locality_index = self._load_json(pecs_dir / "locality_index.json", {})
        topology = self._load_json(pecs_dir / "topology_compact.json", {})

        return {
            "daemon_running": daemon_running,
            "daemon_pid": daemon_pid,
            "daemon_status": health_state.get("status", "unknown"),
            "daemon_version": health_state.get("daemon_version", "unknown"),
            "topology_ready": bool(health_state.get("topology_ready", False)),
            "retrieval_ready": bool(health_state.get("retrieval_ready", False)),
            "continuity_ready": bool(health_state.get("continuity_ready", False)),
            "workspace": str(self.workspace_root),
            "workspace_graph_valid": bool(
                graph_validation.get("valid", False)
            ),
            "workspace_registry_valid": bool(
                registry_validation.get("valid", False)
            ),
            "locality_entry_count": (
                len(locality_index) if isinstance(locality_index, dict) else 0
            ),
            "topology_edge_count": len(topology.get("edges", [])),
            "runtime_reachable_count": daemon_state.get(
                "runtime_reachable_count", 0
            ),
            "version": "1.0.0-alpha1",
        }
