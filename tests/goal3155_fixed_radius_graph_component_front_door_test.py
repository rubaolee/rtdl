from __future__ import annotations

from pathlib import Path
from unittest import mock
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal3155_fixed_radius_graph_component_front_door_2026-06-03.md"
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"


class _FakePreparedLower:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class Goal3155FixedRadiusGraphComponentFrontDoorTest(unittest.TestCase):
    def test_plan_is_explicit_and_non_authorizing(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=1024,
            radius=0.25,
            component_threshold=4,
            backend="optix",
            partner="cupy",
            strategy="grouped_stream",
        )

        self.assertEqual(plan["status"], "accepted_preview")
        self.assertEqual(plan["operation"], "fixed_radius_graph_component_labels_3d")
        self.assertEqual(plan["user_selected_backend"], "optix")
        self.assertEqual(plan["user_selected_partner"], "cupy")
        self.assertEqual(plan["user_selected_strategy"], "grouped_stream")
        self.assertEqual(plan["component_threshold"], 4)
        self.assertFalse(plan["fallback_selected"])
        self.assertFalse(plan["hidden_dispatch_allowed"])
        self.assertFalse(plan["automatic_partner_selection_allowed"])
        self.assertFalse(plan["app_specific_engine_logic_allowed"])
        self.assertFalse(plan["release_authorized"])
        self.assertFalse(plan["public_speedup_claim_authorized"])
        self.assertFalse(plan["rt_core_speedup_claim_authorized"])
        self.assertFalse(plan["true_zero_copy_claim_authorized"])

    def test_numba_partner_is_explicitly_supported_without_auto_fallback(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=1024,
            radius=0.25,
            component_threshold=4,
            backend="optix",
            partner="numba",
            strategy="grouped_stream",
        )

        self.assertEqual(plan["status"], "accepted_preview")
        self.assertEqual(plan["user_selected_partner"], "numba")
        self.assertFalse(plan["fallback_selected"])
        self.assertFalse(plan["automatic_partner_selection_allowed"])

    def test_front_door_wraps_existing_grouped_stream_contract(self) -> None:
        lower = _FakePreparedLower()
        lower_result = {
            "columns": {
                "point_ids": (0, 1, 2),
                "component_labels": (0, 0, 2),
                "is_core": (1, 1, 0),
                "neighbor_counts": (2, 2, 1),
            },
            "metadata": {
                "adapter": "PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D.run",
                "partner_reference_contract": "generic_prepared_optix_cupy_grouped_stream_component_labels_3d",
                "rt_core_accelerated": True,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": False,
            },
        }

        with mock.patch(
            "rtdsl.v2_8_fixed_radius_graph_component_front_door.prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d",
            return_value=lower,
        ) as prepare:
            prepared = rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d(
                ((0.0, 0.0, 0.0), (0.1, 0.0, 0.0), (2.0, 0.0, 0.0)),
                radius=0.25,
                component_threshold=2,
                partner="cupy",
                backend="optix",
            )
        prepare.assert_called_once()

        with mock.patch(
            "rtdsl.v2_8_fixed_radius_graph_component_front_door.radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns",
            return_value=lower_result,
        ) as run:
            result = rt.fixed_radius_graph_component_labels_3d_v2_8(
                prepared,
                component_threshold=2,
                return_metadata=True,
            )

        self.assertEqual(run.call_args.kwargs["min_neighbors"], 2)
        self.assertEqual(result["columns"]["component_labels"], (0, 0, 2))
        metadata = result["metadata"]
        self.assertEqual(metadata["front_door"], "v2_8_fixed_radius_graph_component_continuation_3d")
        self.assertEqual(metadata["component_threshold"], 2)
        self.assertEqual(metadata["user_selected_partner"], "cupy")
        self.assertEqual(metadata["lower_partner_reference_contract"], "generic_prepared_optix_cupy_grouped_stream_component_labels_3d")
        self.assertTrue(metadata["rt_core_accelerated"])
        self.assertFalse(metadata["automatic_partner_selection_allowed"])
        self.assertFalse(metadata["app_specific_engine_logic_allowed"])
        self.assertFalse(metadata["release_authorized"])
        prepared.close()
        self.assertTrue(lower.closed)

    def test_discovery_and_source_boundary_are_generic(self) -> None:
        source = MODULE.read_text(encoding="utf-8").lower()
        self.assertNotIn("dbscan", source)
        self.assertNotIn("cluster", source)

        matches = rt.find_primitive(text="fixed radius graph component labels")
        self.assertTrue(matches)
        self.assertEqual(matches[0].node_id, "continuation.fixed_radius_graph")

        catalog = CATALOG.read_text(encoding="utf-8")
        self.assertIn("continuation.fixed_radius_graph", catalog)
        self.assertIn("fixed_radius_graph_components", catalog)

    def test_report_records_goal_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3155",
            "fixed-radius graph component continuation",
            "explicit user-selected OptiX+CuPy grouped-stream contract",
            "no hidden dispatcher",
            "no automatic partner selection",
            "release_authorized: False",
            "public_speedup_claim_authorized: False",
            "rt_core_speedup_claim_authorized: False",
            "true_zero_copy_claim_authorized: False",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
