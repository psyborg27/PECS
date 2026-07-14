from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Set

from integrations.commandcode_adapter import CommandCodeAdapter
from integrations.consumer_integration_core import (
    CANONICAL_CONSUMER_RESPONSE_SCHEMA,
    CanonicalConsumerContract,
)
from integrations.continue_adapter import ContinueAdapter
from integrations.copilot_adapter import CopilotAdapter
from integrations.kimi_adapter import KimiAdapter
from integrations.pecs_lite_runtime_adapter import PECSLiteRuntimeAdapter
from workspace_assets_manager import WorkspaceAssetsManager


class _DummyTopologyRetriever:
    def build_minimal_context(self, object_id: str) -> Dict[str, Any]:
        return {"object_id": object_id}


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _safe_bool(value: Any) -> bool:
    return bool(value)


def _top_level_signature(payload: Dict[str, Any]) -> Set[str]:
    return set(payload.keys()) - {"consumer", "adapter", "canonical_query"}


def run_canonical_workspace_validation(
    workspace_root: Path,
    repo_root: Path,
) -> Dict[str, Any]:
    workspace_root = workspace_root.resolve()
    repo_root = repo_root.resolve()

    manager = WorkspaceAssetsManager(repo_root, workspace_root)
    managed_assets_result = manager.verify_installation()

    daemon_state = _load_json(workspace_root / ".pecs" / "daemon_state.json")
    daemon_health = _load_json(workspace_root / ".pecs" / "daemon_health.json")
    daemon_cycle_validation = _load_json(
        workspace_root / ".pecs" / "daemon_cycle_validation.json"
    )
    graph_validation = _load_json(
        workspace_root / ".pecs" / "workspace_graph_validation.json"
    )
    registry_validation = _load_json(
        workspace_root / ".pecs" / "workspace_registry_validation.json"
    )

    runtime_ok = all(
        key in daemon_state
        for key in (
            "runtime_reachable_count",
            "topology_edge_count",
            "runtime_locality_payload_count",
        )
    )
    daemon_ok = (
        daemon_health.get("status") == "healthy"
        and _safe_bool(daemon_health.get("retrieval_ready"))
        and _safe_bool(daemon_health.get("topology_ready"))
        and _safe_bool(daemon_health.get("continuity_ready"))
    )
    cycle_ok = all(
        key in daemon_cycle_validation
        for key in (
            "topology_validation",
            "archaeology_validation",
            "confidence_validation",
        )
    )

    graph_ok = bool(graph_validation.get("valid", False))
    if not graph_validation:
        graph_ok = bool(daemon_health.get("topology_ready", False))

    registry_ok = bool(registry_validation.get("valid", False))
    if not registry_validation:
        registry_ok = bool(daemon_health.get("continuity_ready", False))

    consumer_assets_ok = all(
        (workspace_root / path).exists()
        for path in (
            ".github/copilot-instructions.md",
            ".continue/config.yaml",
            ".kimi/instructions.md",
            ".commandcode/instructions.md",
            ".pecs/config/consumer_consultation.json",
        )
    )

    projection = PECSLiteRuntimeAdapter.build_projection_safe(
        workspace_root=str(workspace_root),
        query="workspace validation",
        model_name="validation-model",
        model_source="pecs",
        context_window=32768,
        model_size="small",
        provider="pecs",
        profile_class="unknown",
        local_vs_frontier="unknown",
        reasoning_capability_class="unknown",
        query_source="copilot",
    )
    projection_ok = str(projection.get("schema", "")).startswith(
        "pecs_lite.runtime_projection"
    )

    dummy = _DummyTopologyRetriever()
    adapters = [
        CopilotAdapter(dummy, workspace_root=workspace_root).build_copilot_context(
            "contract-check"
        ),
        ContinueAdapter(dummy, workspace_root=workspace_root).build_continue_context(
            "contract-check"
        ),
        CommandCodeAdapter(dummy, workspace_root=workspace_root).build_commandcode_context(
            "contract-check"
        ),
        KimiAdapter(dummy, workspace_root=workspace_root).build_kimi_context(
            "contract-check"
        ),
    ]

    contract_validation = [CanonicalConsumerContract.validate(payload) for payload in adapters]
    contract_signatures = [_top_level_signature(payload) for payload in adapters]
    contract_schema_ok = all(
        str(payload.get("schema", "")) == CANONICAL_CONSUMER_RESPONSE_SCHEMA
        for payload in adapters
    )
    contract_shape_ok = len({tuple(sorted(signature)) for signature in contract_signatures}) == 1
    contract_ok = all(v.get("valid", False) for v in contract_validation) and contract_shape_ok and contract_schema_ok

    checks = {
        "managed_assets": bool(managed_assets_result.get("valid", False)),
        "runtime": runtime_ok,
        "daemon": daemon_ok,
        "workspace_graph": graph_ok,
        "workspace_registry": registry_ok,
        "consumer_integrations": consumer_assets_ok,
        "diagnostics": cycle_ok,
        "projection_engine": projection_ok,
        "canonical_contract": contract_ok,
        "workspace_health": daemon_ok and graph_ok and registry_ok,
    }

    valid = all(checks.values())

    return {
        "schema": "pecs.workspace_verification.alpha1.v1",
        "workspace_root": str(workspace_root),
        "repo_root": str(repo_root),
        "valid": valid,
        "checks": checks,
        "details": {
            "managed_assets": managed_assets_result,
            "daemon_state": {
                "runtime_locality_payload_count": daemon_state.get(
                    "runtime_locality_payload_count", 0
                ),
                "runtime_reachable_count": daemon_state.get("runtime_reachable_count", 0),
                "topology_edge_count": daemon_state.get("topology_edge_count", 0),
            },
            "daemon_health": daemon_health,
            "daemon_cycle_validation": daemon_cycle_validation,
            "workspace_graph_validation": graph_validation,
            "workspace_registry_validation": registry_validation,
            "canonical_contract_validation": contract_validation,
            "canonical_contract_shape_identical": contract_shape_ok,
            "projection_schema": projection.get("schema", ""),
        },
    }
