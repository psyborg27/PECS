#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from execution_graph.indexes.execution_index import ExecutionIndex
from execution_graph.indexes.ownership_index import OwnershipIndex
from topology.indexing.locality_index import LocalityIndex
from topology.retrieval.topology_retriever import TopologyRetriever
from topology.scoring.continuity_score_engine import ContinuityScoreEngine


@dataclass
class RetrievalScenario:
    name: str
    description: str
    object_id: str
    path_id: str
    owner_id: str
    object_locality: List[str]
    execution_locality: List[str]
    ownership_locality: List[str]
    continuity_signals: Dict[str, Any] = field(default_factory=dict)
    accepted_locality_scores: Dict[str, float] = field(default_factory=dict)
    staged_execution_locality: Optional[List[str]] = None
    symbolic_only: bool = False


@dataclass
class RetrievalTrace:
    mode: str
    scenario_name: str
    hydration_phase: str
    selected_anchors: List[str]
    anchor_scores: Dict[str, float]
    duplicate_lineages: List[str]
    source_counts: Dict[str, int]
    runtime_anchor_count: int
    runtime_selected_count: int
    entropy: float
    staged_phase: str
    full_result: Dict[str, Any]

    @property
    def runtime_ratio(self) -> float:
        if not self.selected_anchors:
            return 0.0
        return round(self.runtime_selected_count / len(self.selected_anchors), 3)

    def to_text(self) -> str:
        lines: List[str] = [
            f"Mode: {self.mode}",
            f"Scenario: {self.scenario_name}",
            f"Hydration Phase: {self.hydration_phase}",
            f"Selected Anchors: {len(self.selected_anchors)} -> {self.selected_anchors}",
            f"Runtime Anchor Selected: {self.runtime_selected_count}",
            f"Runtime Ratio: {self.runtime_ratio:.3f}",
            f"Anchor Sources: {self.source_counts}",
            f"Anchor Entropy: {self.entropy:.3f}",
            f"Duplicate Lineages: {self.duplicate_lineages}",
            "Anchor Scores:",
        ]
        for anchor, score in sorted(
            self.anchor_scores.items(),
            key=lambda item: (-item[1], item[0]),
        ):
            lines.append(f"  - {anchor}: {score:.3f}")
        return "\n".join(lines)


class BaselineTopologyRetriever(TopologyRetriever):
    """Symbolic baseline retrieval without runtime interaction prioritization."""

    def _anchor_is_runtime_interaction(self, anchor: str) -> bool:
        return False

    def _prioritize_hydration_anchor_list(self, anchors: List[str]) -> List[str]:
        ordered: List[str] = []
        seen = set()
        for anchor in anchors:
            if anchor and anchor not in seen:
                ordered.append(anchor)
                seen.add(anchor)
        return ordered

    def _collect_anchors(
        self,
        object_locality: List[str],
        execution_locality: List[str],
        ownership_locality: List[str],
        continuity_signals: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        source_weights = {
            "object_locality": 1.0,
            "execution_locality": 0.85,
            "ownership_locality": 0.75,
        }
        anchor_scores: Dict[str, float] = {}
        duplicate_counts: Dict[str, int] = {}
        first_seen: Dict[str, int] = {}

        all_sources = [
            ("object_locality", object_locality),
            ("execution_locality", execution_locality),
            ("ownership_locality", ownership_locality),
        ]

        position = 0
        for source_name, locality in all_sources:
            weight = source_weights.get(source_name, 0.0)
            for anchor in locality:
                duplicate_counts[anchor] = duplicate_counts.get(anchor, 0) + 1
                anchor_scores[anchor] = anchor_scores.get(anchor, 0.0) + weight
                if anchor not in first_seen:
                    first_seen[anchor] = position
                    position += 1

        sorted_anchors = sorted(
            anchor_scores.keys(),
            key=lambda anchor: (
                -anchor_scores.get(anchor, 0.0),
                first_seen.get(anchor, 0),
            ),
        )

        duplicate_lineages = [
            anchor
            for anchor, count in duplicate_counts.items()
            if count > 1
        ]

        return {
            "anchors": sorted_anchors,
            "anchor_scores": anchor_scores,
            "duplicate_lineages": duplicate_lineages,
            "retrieval_source_count": len(sorted_anchors),
            "duplicate_count": len(duplicate_lineages),
        }


class RetrievalTraceHarness:
    """Deterministic retrieval trace harness for before/after comparisons."""

    def __init__(self) -> None:
        self.score_engine = ContinuityScoreEngine()
        self.baseline_retriever = BaselineTopologyRetriever(
            locality_index=LocalityIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=OwnershipIndex(),
            scoring_engine=self.score_engine,
        )
        self.runtime_retriever = TopologyRetriever(
            locality_index=LocalityIndex(),
            execution_index=ExecutionIndex(),
            ownership_index=OwnershipIndex(),
            scoring_engine=self.score_engine,
        )

    def _scenario_retriever(
        self,
        scenario: RetrievalScenario,
        mode: str,
    ) -> TopologyRetriever:
        class ScenarioTopologyRetriever(TopologyRetriever):
            def __init__(
                self,
                object_locality: List[str],
                execution_locality: List[str],
                ownership_locality: List[str],
                scoring_engine: ContinuityScoreEngine,
            ):
                super().__init__(
                    locality_index=LocalityIndex(),
                    execution_index=ExecutionIndex(),
                    ownership_index=OwnershipIndex(),
                    scoring_engine=scoring_engine,
                )
                self._object_locality = object_locality
                self._execution_locality = execution_locality
                self._ownership_locality = ownership_locality

            def retrieve_object_locality(self, object_id: str) -> List[str]:
                return self._object_locality

            def retrieve_execution_locality(self, path_id: str) -> List[str]:
                return self._execution_locality

            def retrieve_ownership_locality(self, owner_id: str) -> List[str]:
                return self._ownership_locality

        return ScenarioTopologyRetriever(
            object_locality=scenario.object_locality,
            execution_locality=scenario.execution_locality,
            ownership_locality=scenario.ownership_locality,
            scoring_engine=self.score_engine,
        )

    @staticmethod
    def _runtime_anchor_count(anchors: List[str], retriever: TopologyRetriever) -> int:
        return sum(
            1
            for anchor in anchors
            if anchor and retriever._anchor_is_runtime_interaction(anchor)
        )

    @staticmethod
    def _entropy(anchors: List[str]) -> float:
        if not anchors:
            return 0.0
        unique = len(set(anchors))
        total = len(anchors)
        return unique / total if total else 0.0

    def _default_accepted_scores(self, scenario: RetrievalScenario) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for idx, anchor in enumerate(scenario.object_locality[:4]):
            scores[anchor] = 1.0 - idx * 0.1
        for anchor in scenario.object_locality:
            if anchor.startswith("PECS_ID:action.") or anchor.startswith("PECS_ID:callback."):
                scores[anchor] = max(scores.get(anchor, 0.0), 1.0)
        return scores

    def _trace_mode(
        self,
        scenario: RetrievalScenario,
        mode: str,
    ) -> RetrievalTrace:
        if mode == "baseline_symbolic":
            retriever = self.baseline_retriever
            continuity_signals = {}
            execution_locality = scenario.execution_locality
        elif mode == "runtime_registration":
            retriever = self.runtime_retriever
            continuity_signals = scenario.continuity_signals.copy()
            execution_locality = scenario.execution_locality
        elif mode == "staged_hydration":
            retriever = self.runtime_retriever
            continuity_signals = {
                **scenario.continuity_signals,
                "runtime_confirmed_locality": True,
                "accepted_locality_scores": scenario.accepted_locality_scores
                or self._default_accepted_scores(scenario),
            }
            execution_locality = (
                scenario.staged_execution_locality
                if scenario.staged_execution_locality is not None
                else scenario.execution_locality
            )
        elif mode == "contextual_runtime":
            retriever = self.runtime_retriever
            continuity_signals = {
                **scenario.continuity_signals,
                "runtime_confirmed_locality": True,
                "locality_authority_confidence": 0.88,
                "continuity_survivability_confidence": 0.75,
            }
            execution_locality = scenario.execution_locality
        else:
            raise ValueError(f"Unknown mode: {mode}")

        anchors_info = retriever._collect_anchors(
            object_locality=scenario.object_locality,
            execution_locality=execution_locality,
            ownership_locality=scenario.ownership_locality,
            continuity_signals=continuity_signals,
        )
        hydration = retriever._select_hydration_anchors(
            object_locality=scenario.object_locality,
            execution_locality=execution_locality,
            ownership_locality=scenario.ownership_locality,
            continuity_signals=continuity_signals,
            locality_limit=12,
        )
        scenario_retriever = self._scenario_retriever(scenario, mode)
        final_result = scenario_retriever.retrieve_continuity_context(
            object_id=scenario.object_id,
            path_id=scenario.path_id,
            owner_id=scenario.owner_id,
            continuity_signals=continuity_signals,
            locality_limit=12,
            enforce=False,
            manual_override=False,
        )

        return RetrievalTrace(
            mode=mode,
            scenario_name=scenario.name,
            hydration_phase=hydration["hydration_phase"],
            selected_anchors=hydration["anchors"],
            anchor_scores=anchors_info["anchor_scores"],
            duplicate_lineages=anchors_info["duplicate_lineages"],
            source_counts={
                "object_locality": len(scenario.object_locality),
                "execution_locality": len(scenario.execution_locality),
                "ownership_locality": len(scenario.ownership_locality),
            },
            runtime_anchor_count=self._runtime_anchor_count(
                anchors_info["anchors"], retriever
            ),
            runtime_selected_count=self._runtime_anchor_count(
                hydration["anchors"], retriever
            ),
            entropy=self._entropy(hydration["anchors"]),
            staged_phase=hydration["hydration_phase"],
            full_result=final_result,
        )

    def compare_scenario(self, scenario: RetrievalScenario) -> List[RetrievalTrace]:
        return [
            self._trace_mode(scenario, mode)
            for mode in (
                "baseline_symbolic",
                "runtime_registration",
                "staged_hydration",
                "contextual_runtime",
            )
        ]

    def _anchor_category(self, anchor: str) -> str:
        if not anchor.startswith("PECS_ID:"):
            return "other"
        if anchor.startswith("PECS_ID:action."):
            return "action"
        if anchor.startswith("PECS_ID:callback."):
            return "callback"
        if anchor.startswith("PECS_ID:shortcut."):
            return "shortcut"
        if anchor.startswith("PECS_ID:dialog."):
            return "dialog"
        if anchor.startswith("PECS_ID:qaction_factory."):
            return "qaction_factory"
        if anchor.startswith("PECS_ID:module."):
            return "symbolic_module"
        if anchor.startswith("PECS_ID:shortcut."):
            return "shortcut"
        return "symbolic_other"

    def _anchor_deltas(
        self, base: RetrievalTrace, other: RetrievalTrace
    ) -> Dict[str, List[str]]:
        base_set = set(base.selected_anchors)
        other_set = set(other.selected_anchors)
        return {
            "added": sorted(other_set - base_set),
            "removed": sorted(base_set - other_set),
        }

    def _runtime_anchor_promotions(
        self,
        base: RetrievalTrace,
        other: RetrievalTrace,
    ) -> List[str]:
        result: List[str] = []
        for anchor in set(base.selected_anchors) | set(other.selected_anchors):
            if not anchor:
                continue
            if not self.runtime_retriever._anchor_is_runtime_interaction(anchor):
                continue
            base_score = base.anchor_scores.get(anchor, 0.0)
            other_score = other.anchor_scores.get(anchor, 0.0)
            if other_score > base_score + 0.01:
                result.append(anchor)
        return sorted(result)

    def _archaeology_leaks(
        self,
        trace: RetrievalTrace,
    ) -> List[str]:
        leaks = [
            anchor
            for anchor in trace.selected_anchors
            if self._anchor_category(anchor) == "symbolic_module"
        ]
        return sorted(leaks)

    def _hydration_pressure_analysis(
        self,
        baseline: RetrievalTrace,
        trace: RetrievalTrace,
    ) -> List[str]:
        findings: List[str] = []
        if trace.staged_phase != baseline.staged_phase:
            findings.append(
                f"phase changed from {baseline.staged_phase} to {trace.staged_phase}"
            )
        if len(trace.selected_anchors) > len(baseline.selected_anchors):
            findings.append(
                "selected anchor count increased, hydration widened retrieval"
            )
            if trace.runtime_ratio <= baseline.runtime_ratio:
                findings.append(
                    "hydration widened without increasing runtime-locality dominance"
                )
        elif len(trace.selected_anchors) < len(baseline.selected_anchors):
            findings.append("selection tightened relative to baseline")
        else:
            findings.append("selection size remained bounded")
        return findings

    def _duplicate_shadow_analysis(
        self,
        baseline: RetrievalTrace,
        trace: RetrievalTrace,
    ) -> List[str]:
        findings: List[str] = []
        if len(trace.duplicate_lineages) < len(baseline.duplicate_lineages):
            findings.append(
                "duplicate-shadow lineages suppressed relative to baseline"
            )
        elif len(trace.duplicate_lineages) > len(baseline.duplicate_lineages):
            findings.append("duplicate-shadow expansion observed")
        if trace.runtime_ratio > baseline.runtime_ratio:
            findings.append("runtime continuity improved duplicate refinement")
        return findings

    def _mutation_locality_convergence(
        self,
        trace: RetrievalTrace,
    ) -> List[str]:
        findings: List[str] = []
        top_anchors = trace.selected_anchors[:3]
        top_categories = [self._anchor_category(a) for a in top_anchors]
        if any(cat in ("action", "callback", "dialog", "shortcut") for cat in top_categories):
            findings.append("top anchors include runtime/mutation-locality primitives")
        if trace.runtime_ratio >= 0.5:
            findings.append("runtime-locality dominates final selection")
        if trace.runtime_ratio < 0.5:
            findings.append("symbolic locality still contributes materially")
        if trace.duplicate_lineages and trace.runtime_ratio < 0.3:
            findings.append("duplicate-shadow leakage remains in low runtime dominance")
        return findings

    def interpret_scenario(
        self,
        scenario: RetrievalScenario,
        traces: List[RetrievalTrace],
    ) -> str:
        baseline = next(t for t in traces if t.mode == "baseline_symbolic")
        runtime = next(t for t in traces if t.mode == "runtime_registration")
        staged = next(t for t in traces if t.mode == "staged_hydration")
        contextual = next(t for t in traces if t.mode == "contextual_runtime")

        lines: List[str] = [
            f"Scenario: {scenario.name}",
            f"Description: {scenario.description}",
            "",
            "Mode summaries:",
        ]

        for trace in (baseline, runtime, staged, contextual):
            lines.append(
                f"- {trace.mode}: selected={len(trace.selected_anchors)}, runtime_ratio={trace.runtime_ratio:.3f}, duplicates={len(trace.duplicate_lineages)}, phase={trace.hydration_phase}"
            )
            lines.append(
                f"  anchors={trace.selected_anchors}"
            )

        deltas = {
            "runtime_registration": self._anchor_deltas(baseline, runtime),
            "staged_hydration": self._anchor_deltas(baseline, staged),
            "contextual_runtime": self._anchor_deltas(baseline, contextual),
        }

        lines.append("")
        lines.append("Deltas relative to baseline:")
        for mode, delta in deltas.items():
            lines.append(f"- {mode} added={delta['added']} removed={delta['removed']}")
            promotions = self._runtime_anchor_promotions(baseline, next(t for t in traces if t.mode == mode))
            if promotions:
                lines.append(f"  runtime promotions={promotions}")
            leaks = self._archaeology_leaks(next(t for t in traces if t.mode == mode))
            if leaks:
                lines.append(f"  archaeology leaks={leaks}")
            lines.extend(
                [f"  {item}" for item in self._hydration_pressure_analysis(baseline, next(t for t in traces if t.mode == mode))]
            )
            lines.extend(
                [f"  {item}" for item in self._duplicate_shadow_analysis(baseline, next(t for t in traces if t.mode == mode))]
            )
            lines.extend(
                [f"  {item}" for item in self._mutation_locality_convergence(next(t for t in traces if t.mode == mode))]
            )

        lines.append("")
        lines.append("Narrative:")
        for trace in (baseline, runtime, staged, contextual):
            narrative: List[str] = []
            if trace.runtime_ratio > baseline.runtime_ratio:
                narrative.append("runtime locality gained influence")
            if trace.staged_phase != baseline.staged_phase:
                narrative.append(f"phase shifted to {trace.staged_phase}")
            if self._archaeology_leaks(trace):
                narrative.append("still retains symbolic archaeology leaks")
            if trace.runtime_ratio >= 0.5:
                narrative.append("final selection is runtime-mutation focused")
            if not narrative:
                narrative.append("no significant mode-specific evolution")
            lines.append(f"- {trace.mode}: {'; '.join(narrative)}")

        return "\n".join(lines)

    def build_text_report(self) -> str:
        reports: List[str] = []
        for scenario in self.all_scenarios():
            traces = self.compare_scenario(scenario)
            reports.append(self.interpret_scenario(scenario, traces))
            reports.append("\n" + "=" * 80 + "\n")
        return "\n".join(reports)

    def build_report(self) -> Dict[str, Any]:
        return [
            RetrievalScenario(
                name="broken_keyboard_shortcut_callback",
                description="Shortcut action leads through QAction ownership to a callback mutation surface.",
                object_id="keyboard_shortcut_handler",
                path_id="path.keyboard_shortcut_handler",
                owner_id="owner.keyboard",
                object_locality=[
                    "PECS_ID:module.KeyboardHandler",
                    "PECS_ID:module.KeyboardHandler.on_shortcut",
                    "PECS_ID:shortcut.save",
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                ],
                execution_locality=[
                    "PECS_ID:shortcut.save",
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                    "PECS_ID:module.KeyboardHandler.on_shortcut",
                ],
                ownership_locality=[
                    "PECS_ID:shortcut.save",
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                ],
            ),
            RetrievalScenario(
                name="qaction_ownership_mutation",
                description="QAction ownership drives the mutation surface instead of import adjacency.",
                object_id="editor_save_handler",
                path_id="path.editor_save_handler",
                owner_id="owner.editor",
                object_locality=[
                    "PECS_ID:module.Editor",
                    "PECS_ID:module.Editor.save_action",
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                ],
                execution_locality=[
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                    "PECS_ID:module.Editor.perform_save",
                ],
                ownership_locality=[
                    "PECS_ID:action.save",
                    "PECS_ID:qaction_factory.save_factory",
                ],
                staged_execution_locality=[],
                accepted_locality_scores={
                    "PECS_ID:action.save": 1.0,
                    "PECS_ID:callback.save": 0.95,
                    "PECS_ID:qaction_factory.save_factory": 0.9,
                },
            ),
            RetrievalScenario(
                name="lambda_callback_continuity",
                description="Lambda callback continuity with runtime ownership and delayed mutation locality.",
                object_id="lambda_save_callback",
                path_id="path.lambda_save_callback",
                owner_id="owner.lambda",
                object_locality=[
                    "PECS_ID:module.DialogBuilder",
                    "PECS_ID:module.DialogBuilder.<lambda>",
                    "PECS_ID:callback.lambda_save",
                    "PECS_ID:action.save",
                ],
                execution_locality=[
                    "PECS_ID:callback.lambda_save",
                    "PECS_ID:action.save",
                    "PECS_ID:module.DialogBuilder.handle_save",
                ],
                ownership_locality=[
                    "PECS_ID:callback.lambda_save",
                ],
            ),
            RetrievalScenario(
                name="functools_partial_callback_locality",
                description="functools.partial callback remains part of runtime mutation locality instead of symbolic fragmentation.",
                object_id="partial_save_callback",
                path_id="path.partial_save_callback",
                owner_id="owner.partial",
                object_locality=[
                    "PECS_ID:module.CallbackFactory",
                    "PECS_ID:module.CallbackFactory.partial_save",
                    "PECS_ID:callback.partial_save",
                ],
                execution_locality=[
                    "PECS_ID:callback.partial_save",
                    "PECS_ID:action.save",
                    "PECS_ID:module.CallbackFactory.execute_save",
                ],
                ownership_locality=[
                    "PECS_ID:callback.partial_save",
                ],
            ),
            RetrievalScenario(
                name="wrapper_factory_qaction_registration",
                description="Wrapper/factory-driven QAction registration surfaces runtime ownership topologies.",
                object_id="qaction_factory_wrapper",
                path_id="path.qaction_factory_wrapper",
                owner_id="owner.qaction_factory",
                object_locality=[
                    "PECS_ID:module.QActionWrapper",
                    "PECS_ID:module.QActionWrapper.register",
                    "PECS_ID:action.save",
                    "PECS_ID:qaction_factory.wrapper_factory",
                ],
                execution_locality=[
                    "PECS_ID:qaction_factory.wrapper_factory",
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                ],
                ownership_locality=[
                    "PECS_ID:qaction_factory.wrapper_factory",
                    "PECS_ID:action.save",
                ],
                staged_execution_locality=[],
                accepted_locality_scores={
                    "PECS_ID:action.save": 1.0,
                    "PECS_ID:callback.save": 0.9,
                    "PECS_ID:qaction_factory.wrapper_factory": 0.95,
                },
            ),
            RetrievalScenario(
                name="duplicate_shadow_ambiguity",
                description="Duplicate-shadow implementations are disambiguated by runtime-surviving callback locality.",
                object_id="save_handler_shadow",
                path_id="path.save_handler_shadow",
                owner_id="owner.save_shadow",
                object_locality=[
                    "PECS_ID:module.LegacySave",
                    "PECS_ID:module.ActiveSave",
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                    "PECS_ID:callback.save_legacy",
                ],
                execution_locality=[
                    "PECS_ID:callback.save",
                    "PECS_ID:callback.save_legacy",
                    "PECS_ID:action.save",
                    "PECS_ID:module.ActiveSave.perform_save",
                ],
                ownership_locality=[
                    "PECS_ID:callback.save",
                    "PECS_ID:callback.save_legacy",
                ],
                continuity_signals={
                    "duplicate_shadow_scores": {
                        "PECS_ID:callback.save_legacy": 0.8,
                    },
                },
            ),
            RetrievalScenario(
                name="stale_compatibility_path_pollution",
                description="Stale compatibility paths are present but runtime locality should retain the active save handler.",
                object_id="compat_save_handler",
                path_id="path.compat_save_handler",
                owner_id="owner.compat",
                object_locality=[
                    "PECS_ID:module.CompatibilityLayer",
                    "PECS_ID:module.new.SaveHandler",
                    "PECS_ID:action.compat_save",
                    "PECS_ID:callback.compat_save",
                ],
                execution_locality=[
                    "PECS_ID:action.compat_save",
                    "PECS_ID:callback.compat_save",
                    "PECS_ID:module.new.SaveHandler.save",
                ],
                ownership_locality=[
                    "PECS_ID:action.compat_save",
                ],
            ),
            RetrievalScenario(
                name="dialog_launch_mutation_surface",
                description="Dialog launch traversal surfaces the mutation handler instead of symbolic dialog references alone.",
                object_id="dialog_open_handler",
                path_id="path.dialog_open_handler",
                owner_id="owner.dialog",
                object_locality=[
                    "PECS_ID:module.DialogController",
                    "PECS_ID:module.DialogController.open_file",
                    "PECS_ID:dialog.open_file",
                    "PECS_ID:callback.open_file_loaded",
                ],
                execution_locality=[
                    "PECS_ID:dialog.open_file",
                    "PECS_ID:callback.open_file_loaded",
                    "PECS_ID:module.DialogController.handle_open",
                ],
                ownership_locality=[
                    "PECS_ID:dialog.open_file",
                    "PECS_ID:callback.open_file_loaded",
                ],
                staged_execution_locality=[],
                accepted_locality_scores={
                    "PECS_ID:dialog.open_file": 1.0,
                    "PECS_ID:callback.open_file_loaded": 0.95,
                    "PECS_ID:module.DialogController.handle_open": 0.8,
                },
            ),
            RetrievalScenario(
                name="hydration_pressure_escalation",
                description="Hydration pressure scenario with many symbolic candidates but limited runtime-locality retention.",
                object_id="pressure_handler",
                path_id="path.pressure_handler",
                owner_id="owner.pressure",
                object_locality=[
                    "PECS_ID:module.PressureHandler",
                    "PECS_ID:module.PressureHandler.handle",
                    "PECS_ID:module.LegacySupport.handle",
                    "PECS_ID:module.CompatibilityAdapter.handle",
                    "PECS_ID:action.pressure",
                    "PECS_ID:callback.pressure",
                ],
                execution_locality=[
                    "PECS_ID:action.pressure",
                    "PECS_ID:callback.pressure",
                    "PECS_ID:module.PressureHandler.apply",
                ],
                ownership_locality=[
                    "PECS_ID:action.pressure",
                    "PECS_ID:callback.pressure",
                    "PECS_ID:module.LegacySupport.handle",
                ],
                staged_execution_locality=[],
                accepted_locality_scores={
                    "PECS_ID:action.pressure": 1.0,
                    "PECS_ID:callback.pressure": 0.95,
                    "PECS_ID:module.LegacySupport.handle": 0.8,
                },
            ),
        ]

    def _trace_summary(self, trace: RetrievalTrace) -> Dict[str, Any]:
        return {
            "mode": trace.mode,
            "hydration_phase": trace.hydration_phase,
            "selected_count": len(trace.selected_anchors),
            "runtime_selected_count": trace.runtime_selected_count,
            "runtime_ratio": round(
                trace.runtime_selected_count / len(trace.selected_anchors)
                if trace.selected_anchors
                else 0.0,
                3,
            ),
            "entropy": trace.entropy,
            "duplicate_count": len(trace.duplicate_lineages),
            "source_counts": trace.source_counts,
            "selected_anchors": trace.selected_anchors,
            "duplicate_lineages": trace.duplicate_lineages,
        }

    def all_scenarios(self) -> List[RetrievalScenario]:
        return [
            RetrievalScenario(
                name="broken_keyboard_shortcut_callback",
                description="Shortcut action leads through QAction ownership to a callback mutation surface.",
                object_id="keyboard_shortcut_handler",
                path_id="path.keyboard_shortcut_handler",
                owner_id="owner.keyboard",
                object_locality=[
                    "PECS_ID:module.KeyboardHandler",
                    "PECS_ID:module.KeyboardHandler.on_shortcut",
                    "PECS_ID:shortcut.save",
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                ],
                execution_locality=[
                    "PECS_ID:shortcut.save",
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                    "PECS_ID:module.KeyboardHandler.on_shortcut",
                ],
                ownership_locality=[
                    "PECS_ID:shortcut.save",
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                ],
            ),
            RetrievalScenario(
                name="qaction_ownership_mutation",
                description="QAction ownership drives the mutation surface instead of import adjacency.",
                object_id="editor_save_handler",
                path_id="path.editor_save_handler",
                owner_id="owner.editor",
                object_locality=[
                    "PECS_ID:module.Editor",
                    "PECS_ID:module.Editor.save_action",
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                ],
                execution_locality=[
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                    "PECS_ID:module.Editor.perform_save",
                ],
                ownership_locality=[
                    "PECS_ID:action.save",
                    "PECS_ID:qaction_factory.save_factory",
                ],
                staged_execution_locality=[],
                accepted_locality_scores={
                    "PECS_ID:action.save": 1.0,
                    "PECS_ID:callback.save": 0.95,
                    "PECS_ID:qaction_factory.save_factory": 0.9,
                },
            ),
            RetrievalScenario(
                name="lambda_callback_continuity",
                description="Lambda callback continuity with runtime ownership and delayed mutation locality.",
                object_id="lambda_save_callback",
                path_id="path.lambda_save_callback",
                owner_id="owner.lambda",
                object_locality=[
                    "PECS_ID:module.DialogBuilder",
                    "PECS_ID:module.DialogBuilder.<lambda>",
                    "PECS_ID:callback.lambda_save",
                    "PECS_ID:action.save",
                ],
                execution_locality=[
                    "PECS_ID:callback.lambda_save",
                    "PECS_ID:action.save",
                    "PECS_ID:module.DialogBuilder.handle_save",
                ],
                ownership_locality=[
                    "PECS_ID:callback.lambda_save",
                ],
                staged_execution_locality=[],
                accepted_locality_scores={
                    "PECS_ID:callback.lambda_save": 1.0,
                    "PECS_ID:action.save": 0.95,
                },
            ),
            RetrievalScenario(
                name="functools_partial_callback_locality",
                description="functools.partial callback remains part of runtime mutation locality instead of symbolic fragmentation.",
                object_id="partial_save_callback",
                path_id="path.partial_save_callback",
                owner_id="owner.partial",
                object_locality=[
                    "PECS_ID:module.CallbackFactory",
                    "PECS_ID:module.CallbackFactory.partial_save",
                    "PECS_ID:callback.partial_save",
                ],
                execution_locality=[
                    "PECS_ID:callback.partial_save",
                    "PECS_ID:action.save",
                    "PECS_ID:module.CallbackFactory.execute_save",
                ],
                ownership_locality=[
                    "PECS_ID:callback.partial_save",
                ],
                staged_execution_locality=[],
                accepted_locality_scores={
                    "PECS_ID:callback.partial_save": 1.0,
                    "PECS_ID:action.save": 0.95,
                },
            ),
            RetrievalScenario(
                name="wrapper_factory_qaction_registration",
                description="Wrapper/factory-driven QAction registration surfaces runtime ownership topologies.",
                object_id="qaction_factory_wrapper",
                path_id="path.qaction_factory_wrapper",
                owner_id="owner.qaction_factory",
                object_locality=[
                    "PECS_ID:module.QActionWrapper",
                    "PECS_ID:module.QActionWrapper.register",
                    "PECS_ID:action.save",
                    "PECS_ID:qaction_factory.wrapper_factory",
                ],
                execution_locality=[
                    "PECS_ID:qaction_factory.wrapper_factory",
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                ],
                ownership_locality=[
                    "PECS_ID:qaction_factory.wrapper_factory",
                    "PECS_ID:action.save",
                ],
                staged_execution_locality=[],
                accepted_locality_scores={
                    "PECS_ID:action.save": 1.0,
                    "PECS_ID:callback.save": 0.9,
                    "PECS_ID:qaction_factory.wrapper_factory": 0.95,
                },
            ),
            RetrievalScenario(
                name="duplicate_shadow_ambiguity",
                description="Duplicate-shadow implementations are disambiguated by runtime-surviving callback locality.",
                object_id="save_handler_shadow",
                path_id="path.save_handler_shadow",
                owner_id="owner.save_shadow",
                object_locality=[
                    "PECS_ID:module.LegacySave",
                    "PECS_ID:module.ActiveSave",
                    "PECS_ID:action.save",
                    "PECS_ID:callback.save",
                    "PECS_ID:callback.save_legacy",
                ],
                execution_locality=[
                    "PECS_ID:callback.save",
                    "PECS_ID:callback.save_legacy",
                    "PECS_ID:action.save",
                    "PECS_ID:module.ActiveSave.perform_save",
                ],
                ownership_locality=[
                    "PECS_ID:callback.save",
                    "PECS_ID:callback.save_legacy",
                ],
                continuity_signals={
                    "duplicate_shadow_scores": {
                        "PECS_ID:callback.save_legacy": 0.8,
                    },
                },
            ),
            RetrievalScenario(
                name="stale_compatibility_path_pollution",
                description="Stale compatibility paths are present but runtime locality should retain the active save handler.",
                object_id="compat_save_handler",
                path_id="path.compat_save_handler",
                owner_id="owner.compat",
                object_locality=[
                    "PECS_ID:module.CompatibilityLayer",
                    "PECS_ID:module.new.SaveHandler",
                    "PECS_ID:action.compat_save",
                    "PECS_ID:callback.compat_save",
                ],
                execution_locality=[
                    "PECS_ID:action.compat_save",
                    "PECS_ID:callback.compat_save",
                    "PECS_ID:module.new.SaveHandler.save",
                ],
                ownership_locality=[
                    "PECS_ID:action.compat_save",
                ],
            ),
            RetrievalScenario(
                name="dialog_launch_mutation_surface",
                description="Dialog launch traversal surfaces the mutation handler instead of symbolic dialog references alone.",
                object_id="dialog_open_handler",
                path_id="path.dialog_open_handler",
                owner_id="owner.dialog",
                object_locality=[
                    "PECS_ID:module.DialogController",
                    "PECS_ID:module.DialogController.open_file",
                    "PECS_ID:dialog.open_file",
                    "PECS_ID:callback.open_file_loaded",
                ],
                execution_locality=[
                    "PECS_ID:dialog.open_file",
                    "PECS_ID:callback.open_file_loaded",
                    "PECS_ID:module.DialogController.handle_open",
                ],
                ownership_locality=[
                    "PECS_ID:dialog.open_file",
                    "PECS_ID:callback.open_file_loaded",
                ],
                staged_execution_locality=[],
                accepted_locality_scores={
                    "PECS_ID:dialog.open_file": 1.0,
                    "PECS_ID:callback.open_file_loaded": 0.95,
                    "PECS_ID:module.DialogController.handle_open": 0.8,
                },
            ),
            RetrievalScenario(
                name="hydration_pressure_escalation",
                description="Hydration pressure scenario with many symbolic candidates but limited runtime-locality retention.",
                object_id="pressure_handler",
                path_id="path.pressure_handler",
                owner_id="owner.pressure",
                object_locality=[
                    "PECS_ID:module.PressureHandler",
                    "PECS_ID:module.PressureHandler.handle",
                    "PECS_ID:module.LegacySupport.handle",
                    "PECS_ID:module.CompatibilityAdapter.handle",
                    "PECS_ID:action.pressure",
                    "PECS_ID:callback.pressure",
                ],
                execution_locality=[
                    "PECS_ID:action.pressure",
                    "PECS_ID:callback.pressure",
                    "PECS_ID:module.PressureHandler.apply",
                ],
                ownership_locality=[
                    "PECS_ID:action.pressure",
                    "PECS_ID:callback.pressure",
                    "PECS_ID:module.LegacySupport.handle",
                ],
                staged_execution_locality=[],
                accepted_locality_scores={
                    "PECS_ID:action.pressure": 1.0,
                    "PECS_ID:callback.pressure": 0.95,
                    "PECS_ID:module.LegacySupport.handle": 0.8,
                },
            ),
        ]

    def build_report(self) -> Dict[str, Any]:
        report: Dict[str, Any] = {}
        for scenario in self.all_scenarios():
            traces = self.compare_scenario(scenario)
            baseline = next(t for t in traces if t.mode == "baseline_symbolic")
            runtime = next(t for t in traces if t.mode == "runtime_registration")
            staged = next(t for t in traces if t.mode == "staged_hydration")
            contextual = next(t for t in traces if t.mode == "contextual_runtime")
            report[scenario.name] = {
                "scenario": scenario.description,
                "comparisons": {
                    "baseline_symbolic": self._trace_summary(baseline),
                    "runtime_registration": self._trace_summary(runtime),
                    "staged_hydration": self._trace_summary(staged),
                    "contextual_runtime": self._trace_summary(contextual),
                },
                "deltas": {
                    "runtime_anchor_delta": runtime.runtime_selected_count - baseline.runtime_selected_count,
                    "selected_count_delta": len(runtime.selected_anchors) - len(baseline.selected_anchors),
                    "entropy_delta": round(runtime.entropy - baseline.entropy, 3),
                    "duplicate_count_delta": len(runtime.duplicate_lineages) - len(baseline.duplicate_lineages),
                },
            }
        return report


def main() -> None:
    harness = RetrievalTraceHarness()
    print(harness.build_text_report())
    print("--- Summary JSON ---")
    print(json.dumps(harness.build_report(), indent=2))


if __name__ == "__main__":
    main()
