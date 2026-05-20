from __future__ import annotations

import json
import re
import ast
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import time


class PECSProQueryAdapter:
    """PECS-PRO query adapter for stateless locality projection."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root).resolve()
        self.pecs_root = self.workspace_root / ".pecs"
        self.continuity_dir = self.pecs_root / "continuity"
        self._load_artifacts()

    def _load_json(self, path: Path, default: Any = None) -> Any:
        if default is None:
            default = {}
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default

    def _load_artifacts(self) -> None:
        self.active_context = self._load_json(
            self.pecs_root / "active_context.json", {}
        )
        self.compact_bundle = self._load_json(
            self.pecs_root / "compact_bundle.json", {}
        )
        self.locality_index = self._load_json(
            self.pecs_root / "locality_index.json", {}
        )
        self.topology_compact = self._load_json(
            self.pecs_root / "topology_compact.json", {}
        )
        self.locality_state = self._load_json(
            self.continuity_dir / "locality_state.json", {}
        )
        self.active_topology = self._load_json(
            self.continuity_dir / "active_topology.json", {}
        )
        self.engineering_continuity = self._load_json(
            self.continuity_dir / "engineering_continuity_state.json",
            {
                "schema": "pecs.engineering_continuity.v1",
                "active_engineering_chains": [],
                "updated_at": "",
            },
        )

    def _runtime_observability_available(self) -> bool:
        health = self._load_json(self.pecs_root / "daemon_health.json", {})
        return bool(isinstance(health, dict) and health.get("retrieval_ready", False))

    def _symbol_index(self) -> Dict[str, Dict[str, Any]]:
        index: Dict[str, Dict[str, Any]] = {}
        if not isinstance(self.locality_index, dict):
            return index

        for object_id, value in self.locality_index.items():
            if not isinstance(value, dict):
                continue
            file_path = self._normalize_path(str(value.get("file", "") or ""))
            if not file_path:
                continue
            entry = index.setdefault(
                file_path,
                {
                    "classes": set(),
                    "methods": set(),
                    "functions": set(),
                    "object_ids": [],
                },
            )
            cls = str(value.get("class", "") or "").strip()
            method = str(value.get("method", "") or "").strip()
            if cls:
                entry["classes"].add(cls)
            if method:
                if cls:
                    entry["methods"].add(f"{cls}.{method}")
                else:
                    entry["functions"].add(method)
            entry["object_ids"].append(str(object_id))

        return {
            path: {
                "classes": sorted(v["classes"]),
                "methods": sorted(v["methods"]),
                "functions": sorted(v["functions"]),
                "object_ids": v["object_ids"],
            }
            for path, v in index.items()
        }

    def _bounded_ast_symbols(self, file_path: str) -> Dict[str, List[str]]:
        abs_path = (self.workspace_root / file_path).resolve()
        if not abs_path.exists() or not abs_path.is_file() or abs_path.suffix != ".py":
            return {"classes": [], "methods": [], "functions": []}

        try:
            source = abs_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            return {"classes": [], "methods": [], "functions": []}

        classes: List[str] = []
        methods: List[str] = []
        functions: List[str] = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        methods.append(f"{node.name}.{child.name}")
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)

        return {
            "classes": classes[:8],
            "methods": methods[:16],
            "functions": functions[:16],
        }

    def resolve_symbol_authority(
        self,
        file_path: str,
        issue_query: str = "",
    ) -> Dict[str, Any]:
        file_path = self._normalize_path(file_path)
        symbol_index = self._symbol_index().get(file_path, {})
        ast_symbols = self._bounded_ast_symbols(file_path)

        classes = list(symbol_index.get("classes", [])) or ast_symbols.get("classes", [])
        methods = list(symbol_index.get("methods", [])) or ast_symbols.get("methods", [])
        functions = list(symbol_index.get("functions", [])) or ast_symbols.get("functions", [])

        tokens = [
            t
            for t in re.split(r"[^a-z0-9_]+", str(issue_query or "").lower())
            if len(t) > 2
        ]

        def _pick(items: List[str]) -> str:
            if not items:
                return ""
            if not tokens:
                return items[0]
            scored: List[Tuple[int, str]] = []
            for item in items:
                lowered = item.lower()
                score = sum(1 for token in tokens if token in lowered)
                scored.append((score, item))
            scored.sort(key=lambda x: (-x[0], len(x[1])))
            return scored[0][1]

        probable_class = _pick(classes)
        probable_method = _pick(methods)
        if not probable_method and functions:
            probable_method = _pick(functions)

        supporting_symbols: List[str] = []
        for item in (methods + functions)[:12]:
            if item != probable_method:
                supporting_symbols.append(item)

        return {
            "probable_class": probable_class or "",
            "probable_method": probable_method or "",
            "supporting_symbols": supporting_symbols[:8],
            "symbol_resolution_used": bool(classes or methods or functions),
            "symbol_resolution_fallback_reason": "" if (classes or methods or functions) else "no_symbol_metadata_or_ast",
        }

    def classify_authority_type(self, file_path: str) -> str:
        lowered = self._normalize_path(file_path).lower()
        if not lowered:
            return "secondary"
        if any(token in lowered for token in ["legacy", "old", "backup", "deprecated", "archive"]):
            return "legacy"
        if any(token in lowered for token in ["generated", "dist/", "build/"]):
            return "generated"
        if any(token in lowered for token in ["wrapper", "adapter", "bridge"]):
            return "wrapper"
        if any(token in lowered for token in ["deprecate", "obsolete"]):
            return "deprecated"
        return "primary"

    def related_files_for(self, file_path: str, max_related: int = 3) -> List[str]:
        file_path = self._normalize_path(file_path)
        edges = self.topology_compact.get("edges", []) if isinstance(self.topology_compact, dict) else []
        file_map = self._build_file_map()
        reverse_file_map = {k: v for k, v in file_map.items()}

        file_to_ids: Dict[str, List[str]] = {}
        for object_id, path in reverse_file_map.items():
            file_to_ids.setdefault(path, []).append(object_id)

        source_ids = file_to_ids.get(file_path, [])
        related: List[str] = []
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            from_id = str(edge.get("from", "") or "")
            to_id = str(edge.get("to", "") or "")
            if from_id in source_ids:
                target_path = self._normalize_path(file_map.get(to_id, ""))
            elif to_id in source_ids:
                target_path = self._normalize_path(file_map.get(from_id, ""))
            else:
                continue

            if target_path and target_path != file_path and not target_path.startswith(".pecs/"):
                if target_path not in related:
                    related.append(target_path)
            if len(related) >= max_related:
                break

        return related[:max_related]

    def entrypoint_chain_for(self, file_path: str, max_depth: int = 4) -> List[str]:
        file_path = self._normalize_path(file_path)
        if not isinstance(self.topology_compact, dict):
            return [file_path] if file_path else []

        entrypoints = self.topology_compact.get("entrypoints", []) or []
        edges = self.topology_compact.get("edges", []) or []
        file_map = self._build_file_map()

        adjacency: Dict[str, List[str]] = {}
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            src = str(edge.get("from", "") or "")
            dst = str(edge.get("to", "") or "")
            if src and dst:
                adjacency.setdefault(src, []).append(dst)

        target_ids = [obj_id for obj_id, path in file_map.items() if self._normalize_path(path) == file_path]
        if not target_ids:
            return [file_path] if file_path else []

        from collections import deque

        for ep in entrypoints:
            ep_id = str(ep)
            queue = deque([(ep_id, [ep_id])])
            visited = {ep_id}
            while queue:
                node, chain = queue.popleft()
                if node in target_ids:
                    result = [self._normalize_path(file_map.get(x, x)) for x in chain]
                    return [x for x in result if x][: max_depth + 1]
                if len(chain) > max_depth:
                    continue
                for nxt in adjacency.get(node, []):
                    if nxt in visited:
                        continue
                    visited.add(nxt)
                    queue.append((nxt, chain + [nxt]))

        return [file_path] if file_path else []

    def detect_behavioral_failures(
        self,
        issue_query: str,
        model_source: str,
        context_window: int,
    ) -> Dict[str, Any]:
        normalized = str(issue_query or "").lower()
        namespace_synthesis = bool(re.search(r"([a-z]+)_[a-z]+\s+\1_[a-z]+", normalized))
        grep_storm = normalized.count("grep") >= 3 or normalized.count("cat") >= 4
        recursive_expansion = bool(re.search(r"recursive|loop|expand", normalized))

        env_hint = os.environ.get("PECS_LITE_BEHAVIORAL_HINTS", "")
        if env_hint:
            try:
                hint_data = json.loads(env_hint)
                grep_storm = grep_storm or int(hint_data.get("grep_frequency", 0) or 0) >= 8
                recursive_expansion = recursive_expansion or bool(hint_data.get("recursive_expansion", False))
            except Exception:
                pass

        collapse_detected = namespace_synthesis or grep_storm or recursive_expansion
        constrained_context = context_window <= 262000 or model_source in {"ollama", "local"}
        return {
            "advisory_only": True,
            "grep_storm": grep_storm,
            "recursive_topology_expansion": recursive_expansion,
            "namespace_synthesis": namespace_synthesis,
            "context_collapse_detected": collapse_detected,
            "constrained_context": constrained_context,
        }

    def projection_status(
        self,
        symbol_resolution_used: bool,
        behavioral_analysis_used: bool,
        capability_detection_used: bool,
        authority_confidence: float,
        fallback_reason: str = "",
    ) -> Dict[str, Any]:
        runtime_used = self._runtime_observability_available()
        continuity_used = bool(
            isinstance(self.engineering_continuity, dict)
            and self.engineering_continuity.get("active_engineering_chains", [])
        )
        result = {
            "runtime_observability_used": runtime_used,
            "engineering_continuity_used": continuity_used,
            "workspace_scan_performed": False,
            "symbol_resolution_used": bool(symbol_resolution_used),
            "behavioral_analysis_used": bool(behavioral_analysis_used),
            "capability_detection_used": bool(capability_detection_used),
            "authority_confidence": round(max(0.0, min(1.0, authority_confidence)), 3),
        }
        if not runtime_used:
            result["runtime_observability_fallback_reason"] = "runtime artifacts missing"
        if not continuity_used:
            result["engineering_continuity_fallback_reason"] = "engineering continuity missing"
        if fallback_reason:
            result["fallback_reason"] = fallback_reason
        return result

    def refresh(self) -> None:
        self._load_artifacts()

    def _normalize_path(self, path: str) -> str:
        if not path:
            return ""
        normalized = path.replace("\\", "/").strip()
        normalized = re.sub(r"^\.\/", "", normalized)
        normalized = normalized.replace(
            str(self.workspace_root).replace("\\", "/") + "/", ""
        )
        return normalized

    def _build_file_map(self) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        if isinstance(self.locality_index, dict):
            for object_id, value in self.locality_index.items():
                if isinstance(value, dict):
                    file_path = value.get("file")
                    if isinstance(file_path, str) and file_path.strip():
                        mapping[str(object_id)] = self._normalize_path(
                            file_path.strip()
                        )
        return mapping

    def _file_from_bundle_entry(self, entry: Dict[str, Any]) -> Optional[str]:
        if not isinstance(entry, dict):
            return None
        file_path = entry.get("file") or entry.get("path") or entry.get("source_file")
        if isinstance(file_path, str) and file_path.strip():
            return self._normalize_path(file_path.strip())
        return None

    def issue_term_lookup(self, term: str) -> List[Dict[str, Any]]:
        term_lower = str(term or "").lower().strip()
        if not term_lower:
            return []
        matches: List[Dict[str, Any]] = []
        for entry in (
            self.compact_bundle.get("bundle", [])
            if isinstance(self.compact_bundle, dict)
            else []
        ):
            if not isinstance(entry, dict):
                continue
            combined = " ".join(
                str(entry.get(field, "") or "")
                for field in ["pecs_id", "title", "summary", "description"]
            ).lower()
            if term_lower in combined:
                matches.append(entry)
        return matches

    def runtime_zone_lookup(self, zone_id: Optional[str] = None) -> List[str]:
        zone_id = str(zone_id or "").strip()
        zones = []
        if isinstance(self.active_topology, dict):
            zones = self.active_topology.get("active_runtime_zones", []) or []
        if zone_id:
            return [zone for zone in zones if zone_id in zone]
        return zones

    def locality_cluster_lookup(self, cluster_id: str) -> Dict[str, Any]:
        if not cluster_id:
            return {}
        for cluster in (
            self.locality_state.get("active_locality_clusters", [])
            if isinstance(self.locality_state, dict)
            else []
        ):
            if cluster.get("cluster") == cluster_id:
                return cluster
        return {}

    def runtime_target_candidates(self, max_targets: int = 48) -> List[Dict[str, Any]]:
        """Return confidence-ordered runtime target candidates.

        This method is query-only and reads PECS-PRO artifacts. It never scans the workspace.
        """
        fusion = self.evidence_fusion_lookup(max_files=max_targets * 2)
        ranked_files = fusion.get("ranked_files", [])

        candidates: List[Dict[str, Any]] = []
        for item in ranked_files[:max_targets]:
            file_path = str(item.get("file", "") or "")
            if not file_path or file_path.startswith(".pecs/"):
                continue
            tier_scores = item.get("tier_scores", {})
            candidates.append(
                {
                    "file": file_path,
                    "evidence": "evidence_fusion",
                    "base_confidence": float(item.get("fused_score", 0.0) or 0.0),
                    "is_active": float(tier_scores.get("tier_1_runtime", 0.0) or 0.0) > 0.0,
                    "tier_scores": tier_scores,
                    "evidence_sources": item.get("tier_sources", {}),
                    "provenance": item.get("provenance", []),
                }
            )

        return candidates

    def evidence_fusion_lookup(self, max_files: int = 128) -> Dict[str, Any]:
        """Build deterministic, provenance-visible evidence fusion scores."""
        weights = {
            "tier_0_static": 0.20,
            "tier_1_runtime": 0.35,
            "tier_2_continuity": 0.25,
            "tier_3_validation": 0.20,
        }

        file_map = self._build_file_map()
        object_to_file = {str(k): self._normalize_path(v) for k, v in file_map.items() if self._normalize_path(v)}
        file_set = set(object_to_file.values())

        compact_bundle_entries = self.compact_bundle.get("bundle", []) if isinstance(self.compact_bundle, dict) else []
        for entry in compact_bundle_entries:
            path = self._file_from_bundle_entry(entry)
            if path:
                file_set.add(path)

        runtime_touched = self.locality_state.get("active_runtime_touched_files", []) if isinstance(self.locality_state, dict) else []
        touch_counter: Dict[str, int] = {}
        for touched in runtime_touched:
            if not isinstance(touched, dict):
                continue
            path = self._normalize_path(str(touched.get("file", "") or ""))
            if not path:
                continue
            file_set.add(path)
            try:
                touch_counter[path] = max(touch_counter.get(path, 0), int(touched.get("touch_count", 0) or 0))
            except Exception:
                touch_counter[path] = max(touch_counter.get(path, 0), 0)

        active_objects = self.active_context.get("activated_objects", []) if isinstance(self.active_context, dict) else []
        active_object_files = {
            object_to_file.get(str(object_id), "")
            for object_id in active_objects
            if object_to_file.get(str(object_id), "")
        }
        file_set.update(active_object_files)

        edges = self.topology_compact.get("edges", []) if isinstance(self.topology_compact, dict) else []
        edge_object_ids = set()
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            src = str(edge.get("from", "") or "")
            dst = str(edge.get("to", "") or "")
            if src:
                edge_object_ids.add(src)
            if dst:
                edge_object_ids.add(dst)
        edge_files = {object_to_file.get(obj_id, "") for obj_id in edge_object_ids if object_to_file.get(obj_id, "")}
        file_set.update(edge_files)

        engineering_lookup = self.engineering_continuity_lookup(issue_query="", max_chains=16)
        accepted_scores = {
            self._normalize_path(str(path or "")): float(score or 0.0)
            for path, score in (engineering_lookup.get("accepted_locality_scores", {}) or {}).items()
            if self._normalize_path(str(path or ""))
        }
        rejected_scores = {
            self._normalize_path(str(path or "")): float(score or 0.0)
            for path, score in (engineering_lookup.get("rejected_locality_scores", {}) or {}).items()
            if self._normalize_path(str(path or ""))
        }
        runtime_confirmed_scores = {
            self._normalize_path(str(path or "")): float(score or 0.0)
            for path, score in (engineering_lookup.get("runtime_confirmed_locality_scores", {}) or {}).items()
            if self._normalize_path(str(path or ""))
        }
        survivability_scores = {
            self._normalize_path(str(path or "")): float(score or 0.0)
            for path, score in (engineering_lookup.get("continuity_survivability_scores", {}) or {}).items()
            if self._normalize_path(str(path or ""))
        }
        authority_scores = {
            self._normalize_path(str(path or "")): float(score or 0.0)
            for path, score in (engineering_lookup.get("locality_authority_scores", {}) or {}).items()
            if self._normalize_path(str(path or ""))
        }
        file_set.update(accepted_scores.keys())
        file_set.update(runtime_confirmed_scores.keys())
        file_set.update(survivability_scores.keys())
        file_set.update(authority_scores.keys())

        chain_records = self.engineering_continuity.get("active_engineering_chains", []) if isinstance(self.engineering_continuity, dict) else []
        error_object_correlation: Dict[str, float] = {}
        unresolved_penalty: Dict[str, float] = {}
        fix_validation: Dict[str, float] = {}
        max_chain_count: Dict[str, int] = {}
        for chain in chain_records:
            if not isinstance(chain, dict):
                continue
            accepted_locality = self._normalize_path(str(chain.get("accepted_locality", "") or ""))
            attempted_locality = self._normalize_path(str(chain.get("attempted_locality", "") or ""))
            runtime_candidate = self._normalize_path(str(chain.get("runtime_authority_candidate", "") or ""))
            for loc in (accepted_locality, attempted_locality, runtime_candidate):
                if loc:
                    max_chain_count[loc] = max_chain_count.get(loc, 0) + 1
                    file_set.add(loc)
            if attempted_locality:
                error_object_correlation[attempted_locality] = error_object_correlation.get(attempted_locality, 0.0) + 1.0
            if accepted_locality and bool(chain.get("accepted_followup", False)):
                fix_validation[accepted_locality] = fix_validation.get(accepted_locality, 0.0) + 1.0
            unresolved_locations = chain.get("unresolved_locality", []) or []
            if isinstance(unresolved_locations, list):
                for loc in unresolved_locations:
                    normalized = self._normalize_path(str(loc or ""))
                    if normalized:
                        unresolved_penalty[normalized] = unresolved_penalty.get(normalized, 0.0) + 1.0
                        file_set.add(normalized)
            if bool(chain.get("unresolved_persistence", False)) and accepted_locality:
                unresolved_penalty[accepted_locality] = unresolved_penalty.get(accepted_locality, 0.0) + 1.0

        max_touch = max(touch_counter.values()) if touch_counter else 0
        max_correlation = max(error_object_correlation.values()) if error_object_correlation else 0.0
        max_fix_validation = max(fix_validation.values()) if fix_validation else 0.0
        max_unresolved = max(unresolved_penalty.values()) if unresolved_penalty else 0.0

        runtime_neighborhood = set(self.runtime_confirmed_neighborhood_lookup(max_neighbors=max_files * 2))
        ownership_focus = self.ownership_locality_lookup()

        ranked_files: List[Dict[str, Any]] = []
        for file_path in sorted(file_set):
            if not file_path or file_path.startswith(".pecs/"):
                continue

            full_path = (self.workspace_root / file_path).resolve()
            exists = full_path.exists()

            tier_0_import_topology = 1.0 if file_path in object_to_file.values() else 0.0
            tier_0_dependency_topology = 1.0 if file_path in edge_files else 0.0
            tier_0_filesystem = 1.0 if exists else 0.0
            tier_0_static = round(
                (tier_0_import_topology + tier_0_dependency_topology + tier_0_filesystem) / 3.0,
                3,
            )

            tier_1_runtime_activation = 1.0 if file_path in active_object_files else 0.0
            tier_1_runtime_touch = round((touch_counter.get(file_path, 0) / max_touch), 3) if max_touch > 0 else 0.0
            tier_1_runtime_chain = 1.0 if file_path in runtime_neighborhood else 0.0
            tier_1_runtime = round(
                (tier_1_runtime_activation + tier_1_runtime_touch + tier_1_runtime_chain) / 3.0,
                3,
            )

            tier_2_ownership_continuity = 1.0 if ownership_focus and file_path == ownership_focus else 0.0
            tier_2_continuity_hotspot = round(max(accepted_scores.get(file_path, 0.0), authority_scores.get(file_path, 0.0)), 3)
            tier_2_engineering_chain = round(survivability_scores.get(file_path, 0.0), 3)
            tier_2_continuity = round(
                (tier_2_ownership_continuity + tier_2_continuity_hotspot + tier_2_engineering_chain) / 3.0,
                3,
            )

            tier_3_user_confirmed = round(runtime_confirmed_scores.get(file_path, 0.0), 3)
            tier_3_error_object = round((error_object_correlation.get(file_path, 0.0) / max_correlation), 3) if max_correlation > 0 else 0.0
            tier_3_fix_validation = round((fix_validation.get(file_path, 0.0) / max_fix_validation), 3) if max_fix_validation > 0 else 0.0
            unresolved_norm = round((unresolved_penalty.get(file_path, 0.0) / max_unresolved), 3) if max_unresolved > 0 else 0.0
            rejected_norm = round(min(1.0, rejected_scores.get(file_path, 0.0)), 3)
            tier_3_validation_raw = (tier_3_user_confirmed + tier_3_error_object + tier_3_fix_validation) / 3.0
            tier_3_validation = round(max(0.0, tier_3_validation_raw - (0.35 * unresolved_norm) - (0.25 * rejected_norm)), 3)

            tier_scores = {
                "tier_0_static": tier_0_static,
                "tier_1_runtime": tier_1_runtime,
                "tier_2_continuity": tier_2_continuity,
                "tier_3_validation": tier_3_validation,
            }

            fused_score = round(
                sum(weights[tier] * tier_scores[tier] for tier in weights),
                3,
            )

            tier_sources = {
                "tier_0_static": [
                    "import_topology" if tier_0_import_topology > 0 else "",
                    "dependency_topology" if tier_0_dependency_topology > 0 else "",
                    "filesystem_structure" if tier_0_filesystem > 0 else "",
                ],
                "tier_1_runtime": [
                    "runtime_activation" if tier_1_runtime_activation > 0 else "",
                    "runtime_touched_files" if tier_1_runtime_touch > 0 else "",
                    "runtime_chain_neighborhood" if tier_1_runtime_chain > 0 else "",
                ],
                "tier_2_continuity": [
                    "ownership_continuity" if tier_2_ownership_continuity > 0 else "",
                    "continuity_hotspots" if tier_2_continuity_hotspot > 0 else "",
                    "engineering_continuity_chain" if tier_2_engineering_chain > 0 else "",
                ],
                "tier_3_validation": [
                    "user_confirmed_runtime_validation" if tier_3_user_confirmed > 0 else "",
                    "error_to_object_correlation" if tier_3_error_object > 0 else "",
                    "accepted_rejected_fix_validation" if tier_3_fix_validation > 0 or rejected_norm > 0 else "",
                    "unresolved_persistence_penalty" if unresolved_norm > 0 else "",
                ],
            }
            tier_sources = {
                tier: sorted([source for source in sources if source])
                for tier, sources in tier_sources.items()
            }

            provenance = sorted(
                set(
                    [
                        source
                        for tier in ("tier_0_static", "tier_1_runtime", "tier_2_continuity", "tier_3_validation")
                        for source in tier_sources[tier]
                    ]
                )
            )

            ranked_files.append(
                {
                    "file": file_path,
                    "fused_score": fused_score,
                    "tier_scores": tier_scores,
                    "tier_sources": tier_sources,
                    "provenance": provenance,
                }
            )

        ranked_files.sort(
            key=lambda item: (
                -float(item.get("fused_score", 0.0) or 0.0),
                -float(item.get("tier_scores", {}).get("tier_3_validation", 0.0) or 0.0),
                -float(item.get("tier_scores", {}).get("tier_2_continuity", 0.0) or 0.0),
                -float(item.get("tier_scores", {}).get("tier_1_runtime", 0.0) or 0.0),
                -float(item.get("tier_scores", {}).get("tier_0_static", 0.0) or 0.0),
                str(item.get("file", "")),
            )
        )

        return {
            "schema": "pecs.evidence_fusion.v1",
            "deterministic": True,
            "weights": weights,
            "ranked_files": ranked_files[:max_files],
        }

    def runtime_target_lookup(
        self, max_targets: int = 12, model_size: str = "small"
    ) -> List[str]:
        candidates = self.runtime_target_candidates(max_targets=max_targets)
        unique_targets = [
            str(item.get("file", "")) for item in candidates if item.get("file")
        ]

        if model_size == "small":
            return unique_targets[:6]
        if model_size == "medium":
            return unique_targets[:12]
        return unique_targets[:20]

    def ownership_locality_lookup(self) -> str:
        top_touched = (
            self.locality_state.get("active_runtime_touched_files", [])
            if isinstance(self.locality_state, dict)
            else []
        )
        if top_touched:
            return self._normalize_path(
                top_touched[0].get("file", "")
                if isinstance(top_touched[0], dict)
                else ""
            )
        hotspot = (
            self.locality_state.get("ownership_hotspots", [])
            if isinstance(self.locality_state, dict)
            else []
        )
        if hotspot and isinstance(hotspot[0], dict):
            return self._normalize_path(hotspot[0].get("id", ""))
        return ""

    def wrapper_warning_lookup(self) -> bool:
        clusters = (
            self.locality_state.get("active_locality_clusters", [])
            if isinstance(self.locality_state, dict)
            else []
        )
        touched_files = (
            self.locality_state.get("active_runtime_touched_files", [])
            if isinstance(self.locality_state, dict)
            else []
        )
        return len(clusters) > 3 and len(touched_files) > 8

    def execution_depth_lookup(self) -> str:
        zone_count = len(self.runtime_zone_lookup())
        cluster_count = len(
            self.locality_state.get("active_locality_clusters", [])
            if isinstance(self.locality_state, dict)
            else []
        )
        if zone_count >= 3 or cluster_count >= 4:
            return "deep"
        if zone_count == 2 or cluster_count == 3:
            return "moderate"
        return "shallow"

    def active_continuity_lookup(self) -> Dict[str, Any]:
        return {
            "active_topology_zone": self.active_topology.get(
                "active_topology_zone", "general_runtime"
            ),
            "active_runtime_zones": self.active_topology.get(
                "active_runtime_zones", []
            ),
            "active_context_size": (
                len(self.active_context.get("activated_objects", []))
                if isinstance(self.active_context, dict)
                else 0
            ),
            "locality_cluster_count": (
                len(self.locality_state.get("active_locality_clusters", []))
                if isinstance(self.locality_state, dict)
                else 0
            ),
            "runtime_confirmation_density": (
                float(
                    self.active_topology.get("runtime_validation", {}).get(
                        "runtime_confirmation_density", 0.0
                    )
                )
                if isinstance(self.active_topology, dict)
                else 0.0
            ),
            "engineering_chain_count": (
                len(self.engineering_continuity.get("active_engineering_chains", []))
                if isinstance(self.engineering_continuity, dict)
                else 0
            ),
        }

    def engineering_continuity_lookup(
        self,
        issue_query: str = "",
        max_chains: int = 4,
    ) -> Dict[str, Any]:
        """Return compact engineering continuity signals.

        This returns structured signals only (issue->locality->outcome chains).
        It never returns raw chat transcripts or verbose conversational history.
        """

        chains = (
            self.engineering_continuity.get("active_engineering_chains", [])
            if isinstance(self.engineering_continuity, dict)
            else []
        )

        query_tokens = [
            token
            for token in re.split(r"[^a-z0-9_]+", str(issue_query or "").lower())
            if len(token) > 2
        ]

        accepted_scores: Dict[str, float] = {}
        rejected_scores: Dict[str, float] = {}
        runtime_confirmed_scores: Dict[str, float] = {}
        survivability_scores: Dict[str, float] = {}
        authority_scores: Dict[str, float] = {}
        duplicate_shadow_scores: Dict[str, float] = {}
        dead_execution_path_scores: Dict[str, float] = {}
        topology_mismatch_scores: Dict[str, float] = {}
        normalized_chains: List[Dict[str, Any]] = []

        for item in chains:
            if not isinstance(item, dict):
                continue

            issue = str(item.get("issue", "") or "").strip()
            accepted_locality = self._normalize_path(
                str(item.get("accepted_locality", "") or "")
            )
            if not accepted_locality or accepted_locality.startswith(".pecs/"):
                continue

            rejected_locality = [
                self._normalize_path(str(path or ""))
                for path in (item.get("rejected_locality", []) or [])
                if str(path or "").strip()
                and not self._normalize_path(str(path or "")).startswith(".pecs/")
            ]

            if query_tokens:
                lowered_issue = issue.lower()
                token_hits = sum(1 for token in query_tokens if token in lowered_issue)
                if token_hits == 0:
                    continue

            base_strength = float(item.get("continuity_strength", 0.55) or 0.55)
            locality_stability = float(item.get("locality_stability", 0.55) or 0.55)
            accepted_followup = bool(item.get("accepted_followup", False))
            repeat_success = int(item.get("repeat_success_count", 0) or 0)
            rollback_count = int(item.get("rollback_count", 0) or 0)
            abandoned_count = int(item.get("abandoned_count", 0) or 0)
            contradictory_followups = int(item.get("contradictory_followups", 0) or 0)

            confidence = base_strength
            if accepted_followup:
                confidence += 0.08
            if locality_stability >= 0.80:
                confidence += 0.06
            if repeat_success >= 2:
                confidence += 0.06
            if rollback_count == 0:
                confidence += 0.03
            if rollback_count > 0:
                confidence -= min(0.24, 0.12 * rollback_count)
            if abandoned_count > 0:
                confidence -= min(0.16, 0.08 * abandoned_count)
            if contradictory_followups > 0:
                confidence -= min(0.18, 0.06 * contradictory_followups)

            confidence = max(0.0, min(1.0, confidence))

            accepted_scores[accepted_locality] = max(
                accepted_scores.get(accepted_locality, 0.0), confidence
            )

            for rejected in rejected_locality:
                rejected_scores[rejected] = max(
                    rejected_scores.get(rejected, 0.0),
                    0.45 + (0.30 if rollback_count > 0 else 0.0),
                )

            unresolved = [
                self._normalize_path(str(path or ""))
                for path in (item.get("unresolved_locality", []) or [])
                if str(path or "").strip()
                and not self._normalize_path(str(path or "")).startswith(".pecs/")
            ]

            attempted_locality = self._normalize_path(
                str(item.get("attempted_locality", accepted_locality) or accepted_locality)
            )
            runtime_authority_candidate = self._normalize_path(
                str(item.get("runtime_authority_candidate", accepted_locality) or accepted_locality)
            )

            runtime_effect_confirmed_raw = item.get("runtime_effect_confirmed", None)
            runtime_effect_confirmed = (
                bool(runtime_effect_confirmed_raw)
                if runtime_effect_confirmed_raw is not None
                else None
            )

            unresolved_persistence = bool(item.get("unresolved_persistence", False))
            duplicate_shadow_suspicion = float(
                item.get("duplicate_shadow_suspicion", 0.0) or 0.0
            )
            dead_execution_path_suspicion = float(
                item.get("dead_execution_path_suspicion", 0.0) or 0.0
            )
            topology_mismatch_suspicion = float(
                item.get("topology_mismatch_suspicion", 0.0) or 0.0
            )
            ownership_ambiguity = float(item.get("ownership_ambiguity", 0.0) or 0.0)
            locality_authority_confidence = float(
                item.get("locality_authority_confidence", confidence) or confidence
            )
            survivability_confidence = float(
                item.get("continuity_survivability_confidence", confidence) or confidence
            )

            authority_scores[accepted_locality] = max(
                authority_scores.get(accepted_locality, 0.0),
                max(0.0, min(1.0, locality_authority_confidence)),
            )
            survivability_scores[accepted_locality] = max(
                survivability_scores.get(accepted_locality, 0.0),
                max(0.0, min(1.0, survivability_confidence)),
            )
            duplicate_shadow_scores[accepted_locality] = max(
                duplicate_shadow_scores.get(accepted_locality, 0.0),
                max(0.0, min(1.0, duplicate_shadow_suspicion)),
            )
            dead_execution_path_scores[accepted_locality] = max(
                dead_execution_path_scores.get(accepted_locality, 0.0),
                max(0.0, min(1.0, dead_execution_path_suspicion)),
            )
            topology_mismatch_scores[accepted_locality] = max(
                topology_mismatch_scores.get(accepted_locality, 0.0),
                max(0.0, min(1.0, topology_mismatch_suspicion)),
            )

            if runtime_effect_confirmed:
                runtime_confirmed_scores[accepted_locality] = max(
                    runtime_confirmed_scores.get(accepted_locality, 0.0),
                    1.0,
                )
                if runtime_authority_candidate:
                    runtime_confirmed_scores[runtime_authority_candidate] = max(
                        runtime_confirmed_scores.get(runtime_authority_candidate, 0.0),
                        1.0,
                    )

            normalized_chains.append(
                {
                    "issue": issue,
                    "accepted_locality": accepted_locality,
                    "attempted_locality": attempted_locality,
                    "runtime_authority_candidate": runtime_authority_candidate,
                    "runtime_effect_confirmed": runtime_effect_confirmed,
                    "unresolved_persistence": unresolved_persistence,
                    "rejected_locality": rejected_locality,
                    "continuity_confidence": round(confidence, 3),
                    "accepted_followup": accepted_followup,
                    "locality_stability": round(locality_stability, 3),
                    "duplicate_shadow_suspicion": round(
                        max(0.0, min(1.0, duplicate_shadow_suspicion)), 3
                    ),
                    "dead_execution_path_suspicion": round(
                        max(0.0, min(1.0, dead_execution_path_suspicion)), 3
                    ),
                    "topology_mismatch_suspicion": round(
                        max(0.0, min(1.0, topology_mismatch_suspicion)), 3
                    ),
                    "ownership_ambiguity": round(
                        max(0.0, min(1.0, ownership_ambiguity)), 3
                    ),
                    "locality_authority_confidence": round(
                        max(0.0, min(1.0, locality_authority_confidence)), 3
                    ),
                    "continuity_survivability_confidence": round(
                        max(0.0, min(1.0, survivability_confidence)), 3
                    ),
                    "stable_engineering_owner": str(
                        item.get("stable_engineering_owner", accepted_locality) or ""
                    ),
                    "unresolved_locality": unresolved,
                    "runtime_ambiguity": bool(item.get("runtime_ambiguity", False)),
                    "continuity_outcome": str(
                        item.get("continuity_outcome", "accepted") or "accepted"
                    ),
                }
            )

        normalized_chains.sort(
            key=lambda chain: (-float(chain["continuity_confidence"]), chain["issue"])
        )
        bounded_chains = normalized_chains[: max(1, max_chains)]

        locality_authority_confidence = 0.0
        continuity_survivability_confidence = 0.0
        duplicate_shadow_suspicion = 0.0
        dead_execution_path_suspicion = 0.0
        topology_mismatch_suspicion = 0.0
        runtime_confirmed_locality = False

        if bounded_chains:
            locality_authority_confidence = sum(
                float(chain.get("locality_authority_confidence", 0.0) or 0.0)
                for chain in bounded_chains
            ) / len(bounded_chains)
            continuity_survivability_confidence = sum(
                float(
                    chain.get("continuity_survivability_confidence", 0.0) or 0.0
                )
                for chain in bounded_chains
            ) / len(bounded_chains)
            duplicate_shadow_suspicion = max(
                float(chain.get("duplicate_shadow_suspicion", 0.0) or 0.0)
                for chain in bounded_chains
            )
            dead_execution_path_suspicion = max(
                float(chain.get("dead_execution_path_suspicion", 0.0) or 0.0)
                for chain in bounded_chains
            )
            topology_mismatch_suspicion = max(
                float(chain.get("topology_mismatch_suspicion", 0.0) or 0.0)
                for chain in bounded_chains
            )
            runtime_confirmed_locality = any(
                chain.get("runtime_effect_confirmed", None) is True
                for chain in bounded_chains
            )

        return {
            "schema": "pecs.engineering_continuity_projection.v1",
            "active_engineering_chains": bounded_chains,
            "accepted_locality_scores": accepted_scores,
            "rejected_locality_scores": rejected_scores,
            "runtime_confirmed_locality_scores": runtime_confirmed_scores,
            "continuity_survivability_scores": survivability_scores,
            "locality_authority_scores": authority_scores,
            "duplicate_shadow_scores": duplicate_shadow_scores,
            "dead_execution_path_scores": dead_execution_path_scores,
            "topology_mismatch_scores": topology_mismatch_scores,
            "runtime_confirmed_locality": runtime_confirmed_locality,
            "locality_authority_confidence": round(locality_authority_confidence, 3),
            "continuity_survivability_confidence": round(
                continuity_survivability_confidence, 3
            ),
            "duplicate_shadow_suspicion": round(duplicate_shadow_suspicion, 3),
            "dead_execution_path_suspicion": round(dead_execution_path_suspicion, 3),
            "topology_mismatch_suspicion": round(topology_mismatch_suspicion, 3),
            "has_high_confidence_continuity": any(
                float(chain.get("continuity_confidence", 0.0)) >= 0.75
                for chain in bounded_chains
            ),
        }

    def runtime_confirmed_neighborhood_lookup(
        self, max_neighbors: int = 12
    ) -> List[str]:
        neighborhood: List[str] = []
        for obj in (
            self.active_context.get("activated_objects", [])
            if isinstance(self.active_context, dict)
            else []
        ):
            file_path = self._build_file_map().get(str(obj))
            if file_path and file_path not in neighborhood:
                neighborhood.append(file_path)
        for touched in (
            self.locality_state.get("active_runtime_touched_files", [])
            if isinstance(self.locality_state, dict)
            else []
        ):
            file_path = touched.get("file")
            if isinstance(file_path, str) and file_path.strip():
                normalized = self._normalize_path(file_path)
                if normalized not in neighborhood:
                    neighborhood.append(normalized)
        return neighborhood[:max_neighbors]

    def manage_evidence_lifecycle(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage the lifecycle of evidence records, including confidence decay and stale detection.

        Args:
            evidence (Dict[str, Any]): The evidence record to manage.

        Returns:
            Dict[str, Any]: Updated evidence record with lifecycle adjustments.
        """
        current_time = time.time()

        # Ensure required fields exist
        evidence.setdefault("creation_source", "unknown")
        evidence.setdefault("confidence_score", 1.0)
        evidence.setdefault("validation_timestamp", current_time)
        evidence.setdefault("last_runtime_confirmation", current_time)
        evidence.setdefault("stale", False)
        evidence.setdefault("invalidation_state", False)

        # Confidence decay logic
        time_since_validation = current_time - evidence["validation_timestamp"]
        time_since_runtime = current_time - evidence["last_runtime_confirmation"]

        # Decay confidence for stale evidence
        if time_since_runtime > 86400:  # 1 day
            evidence["confidence_score"] *= 0.9

        # Mark evidence as stale if not confirmed recently
        if time_since_runtime > 604800:  # 1 week
            evidence["stale"] = True

        # Invalidate evidence if too old or explicitly invalidated
        if time_since_validation > 2592000:  # 30 days
            evidence["invalidation_state"] = True

        return evidence

    def get_query_diagnostics(self) -> Dict[str, Any]:
        """Return diagnostics proving query-driven architecture."""
        return {
            "queried_pecs_pro": True,
            "workspace_scan_performed": False,
            "topology_reconstructed": False,
            "continuity_state_owned": False,
            "projection_mode": "query_driven",
            "artifacts_accessed": [
                ".pecs/active_context.json",
                ".pecs/compact_bundle.json",
                ".pecs/locality_index.json",
                ".pecs/topology_compact.json",
                ".pecs/continuity/locality_state.json",
                ".pecs/continuity/active_topology.json",
                ".pecs/continuity/engineering_continuity_state.json",
            ],
            "artifacts_not_generated": [
                ".pecs/daemon_lite_v2.pid",
                ".pecs/daemon_lite_v2_state.json",
                ".pecs/pecs_lite_runtime_topology.json",
            ],
        }

    def get_health_metrics(self) -> Dict[str, Any]:
        """Return adapter health and load metrics."""
        return {
            "artifacts_loaded": sum(
                [
                    1 if self.active_context else 0,
                    1 if self.compact_bundle else 0,
                    1 if self.locality_index else 0,
                    1 if self.topology_compact else 0,
                    1 if self.locality_state else 0,
                    1 if self.active_topology else 0,
                ]
            ),
            "activated_object_count": len(
                self.active_context.get("activated_objects", [])
                if isinstance(self.active_context, dict)
                else []
            ),
            "touched_file_count": len(
                self.locality_state.get("active_runtime_touched_files", [])
                if isinstance(self.locality_state, dict)
                else []
            ),
            "bundle_entry_count": len(
                self.compact_bundle.get("bundle", [])
                if isinstance(self.compact_bundle, dict)
                else []
            ),
            "locality_cluster_count": len(
                self.locality_state.get("active_locality_clusters", [])
                if isinstance(self.locality_state, dict)
                else []
            ),
            "runtime_zone_count": len(self.runtime_zone_lookup()),
            "engineering_chain_count": len(
                self.engineering_continuity.get("active_engineering_chains", [])
                if isinstance(self.engineering_continuity, dict)
                else []
            ),
        }
