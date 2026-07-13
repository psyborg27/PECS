#!/usr/bin/env python3
from __future__ import annotations

import random
import unittest
from pathlib import Path

from runtime.daemon.workspace_continuity_daemon import WorkspaceContinuityDaemon
from topology.retrieval.topology_retriever import TopologyRetriever


class RuntimeLocalityDeterminismTests(unittest.TestCase):
    def setUp(self) -> None:
        random.seed(0)
        self.daemon = WorkspaceContinuityDaemon(
            workspace_root=Path("."),
            runtime_session=None,
            compact_builder=None,
        )
        self.retriever = TopologyRetriever(
            locality_index=None,
            execution_index=None,
            ownership_index=None,
            scoring_engine=None,
        )

    def test_anchor_group_key_is_stable_for_semantic_neighborhoods(self) -> None:
        class_method_key = self.retriever._anchor_group_key(
            "PECS_ID:module.Class.method"
        )
        alternate_class_method_key = self.retriever._anchor_group_key(
            "PECS_ID:module.Class.other"
        )
        top_level_class_key = self.retriever._anchor_group_key("PECS_ID:module.Class")

        self.assertEqual(class_method_key, alternate_class_method_key)
        self.assertEqual(class_method_key, top_level_class_key)
        self.assertEqual(class_method_key, "PECS_ID:module.Class")

        self.assertEqual(
            self.retriever._anchor_group_key("PECS_ID:action.save"),
            "PECS_ID:action.save",
        )
        self.assertEqual(
            self.retriever._anchor_group_key("PECS_ID:dialog.open_file"),
            "PECS_ID:dialog.open_file",
        )

    def test_anchor_group_key_is_deterministic_across_order_variation(self) -> None:
        anchors = [
            "PECS_ID:action.save",
            "PECS_ID:module.Class.method",
            "PECS_ID:dialog.open_file",
            "PECS_ID:module.Class.other",
        ]
        group_keys = [self.retriever._anchor_group_key(anchor) for anchor in anchors]
        shuffled = anchors[:]
        random.shuffle(shuffled)
        shuffled_group_keys = [self.retriever._anchor_group_key(anchor) for anchor in shuffled]

        self.assertEqual(set(group_keys), set(shuffled_group_keys))
        self.assertEqual(
            group_keys[0],
            self.retriever._anchor_group_key("PECS_ID:action.save"),
        )
        self.assertEqual(
            self.retriever._anchor_group_key("PECS_ID:module.Class.other"),
            self.retriever._anchor_group_key("PECS_ID:module.Class.method"),
        )

    def test_runtime_anchor_ids_from_edges_preserves_runtime_interaction_neighborhoods(self) -> None:
        self.daemon._pecs_id_from_path = lambda _: "PECS_ID:dummy.py"
        path = Path("dummy.py")

        base_edges = [
            {
                "from": "PECS_ID:dummy.py",
                "to": "PECS_ID:action.save",
                "type": "qaction_register",
            },
            {
                "from": "PECS_ID:dummy.py",
                "to": "PECS_ID:shortcut.save",
                "type": "shortcut_ownership",
            },
            {
                "from": "PECS_ID:callback.save",
                "to": "PECS_ID:dummy.py",
                "type": "callback_ownership",
            },
            {
                "from": "PECS_ID:dummy.py",
                "to": "PECS_ID:dialog.open_file",
                "type": "dialog_launch",
            },
            {
                "from": "PECS_ID:dummy.py",
                "to": "PECS_ID:module.Class.method",
                "type": "import",
            },
            {
                "from": "PECS_ID:dummy.py",
                "to": "PECS_ID:module.Class.other",
                "type": "import",
            },
            {
                "from": "PECS_ID:dummy.py",
                "to": "PECS_ID:dummy.py",
                "type": "self_link",
            },
        ]

        expected_runtime_anchors = {
            "PECS_ID:action.save",
            "PECS_ID:shortcut.save",
            "PECS_ID:callback.save",
            "PECS_ID:dialog.open_file",
        }

        extracted = self.daemon._runtime_anchor_ids_from_edges(path, base_edges)
        self.assertEqual(extracted, expected_runtime_anchors)

        shuffled_edges = base_edges[:]
        random.shuffle(shuffled_edges)
        extracted_again = self.daemon._runtime_anchor_ids_from_edges(path, shuffled_edges)
        self.assertEqual(extracted_again, expected_runtime_anchors)

    def test_runtime_anchor_ids_from_edges_ignores_nonsemantic_topology_noise(self) -> None:
        self.daemon._pecs_id_from_path = lambda _: "PECS_ID:dummy.py"
        path = Path("dummy.py")
        edges = [
            {
                "from": "PECS_ID:dummy.py",
                "to": "PECS_ID:module.Class.method",
                "type": "import",
            },
            {
                "from": "PECS_ID:module.Class.method",
                "to": "PECS_ID:dummy.py",
                "type": "import",
            },
            {
                "from": "PECS_ID:dummy.py",
                "to": "PECS_ID:action.save",
                "type": "qaction_ownership",
            },
        ]

        extracted = self.daemon._runtime_anchor_ids_from_edges(path, edges)
        self.assertEqual(extracted, {"PECS_ID:action.save"})

    def test_prioritize_hydration_anchor_list_keeps_runtime_neighborhood_cohesion(self) -> None:
        anchors = [
            "PECS_ID:module.Class.method",
            "PECS_ID:action.save",
            "PECS_ID:module.Class.other",
            "PECS_ID:dialog.open_file",
            "PECS_ID:module.Class",
        ]
        ordered = self.retriever._prioritize_hydration_anchor_list(anchors)
        runtime_keys = [
            self.retriever._anchor_group_key(anchor)
            for anchor in ordered
            if self.retriever._anchor_is_runtime_interaction(anchor)
        ]
        non_runtime_keys = [
            self.retriever._anchor_group_key(anchor)
            for anchor in ordered
            if not self.retriever._anchor_is_runtime_interaction(anchor)
        ]

        self.assertTrue(all(key.startswith("PECS_ID:action.") or key.startswith("PECS_ID:dialog.") for key in runtime_keys))
        self.assertTrue(runtime_keys)
        self.assertTrue(non_runtime_keys)
        self.assertLess(
            ordered.index("PECS_ID:action.save"),
            ordered.index("PECS_ID:module.Class.method"),
        )
        self.assertLess(
            ordered.index("PECS_ID:dialog.open_file"),
            ordered.index("PECS_ID:module.Class.method"),
        )
        self.assertEqual(
            len(ordered),
            len({self.retriever._anchor_group_key(anchor) for anchor in anchors}),
        )
        self.assertEqual(
            len({self.retriever._anchor_group_key(anchor) for anchor in ordered}),
            len(ordered),
        )

    def test_anchor_group_key_bounded_class_grouping(self) -> None:
        anchor_keys = [
            self.retriever._anchor_group_key("PECS_ID:module.Class.method"),
            self.retriever._anchor_group_key("PECS_ID:module.Class.other"),
            self.retriever._anchor_group_key("PECS_ID:module.Class"),
            self.retriever._anchor_group_key("PECS_ID:module.Class.method.sub")
        ]

        self.assertTrue(all(key == "PECS_ID:module.Class" for key in anchor_keys))
        self.assertEqual(len(set(anchor_keys)), 1)


if __name__ == "__main__":
    unittest.main()
