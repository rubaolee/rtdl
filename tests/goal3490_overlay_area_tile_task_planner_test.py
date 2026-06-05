from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3490_overlay_area_tile_task_planner_2026-06-05.md"


def _fixture_pair_rows():
    concave_l = ((0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0))
    square = ((0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5))
    left = rt.prepare_simple_polygon_component_payload((concave_l,))
    right = rt.prepare_simple_polygon_component_payload((square,))
    return rt.prepare_overlay_area_pair_rows(left, right, ((0, 0),))


class Goal3490OverlayAreaTileTaskPlannerTest(unittest.TestCase):
    def test_single_pair_row_splits_into_bounded_tile_tasks(self) -> None:
        pair_rows = _fixture_pair_rows()
        tasks = rt.plan_prepared_overlay_area_tile_tasks(pair_rows, max_triangle_pairs_per_task=3)
        summary = rt.summarize_prepared_overlay_area_tile_tasks(pair_rows, tasks)

        self.assertEqual([task.pair_count for task in tasks], [3, 3, 2])
        self.assertEqual([task.pair_offset for task in tasks], [0, 3, 6])
        self.assertEqual([task.pair_stop for task in tasks], [3, 6, 8])
        self.assertEqual([task.left_triangle_stop for task in tasks], [4, 4, 4])
        self.assertEqual([task.right_triangle_stop for task in tasks], [2, 2, 2])
        self.assertEqual(summary["status"], "accept", summary)
        self.assertEqual(summary["expected_triangle_pair_count"], 8)
        self.assertEqual(summary["planned_triangle_pair_count"], 8)
        self.assertEqual(summary["task_count"], 3)
        self.assertEqual(summary["max_task_pair_count"], 3)

    def test_multiple_component_pairs_can_share_relation_owner(self) -> None:
        left_components = (
            ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)),
            ((10.0, 10.0), (12.0, 10.0), (12.0, 12.0), (10.0, 12.0)),
        )
        right_components = (
            ((1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)),
            ((10.5, 10.5), (11.5, 10.5), (11.5, 11.5), (10.5, 11.5)),
        )
        left = rt.prepare_simple_polygon_component_payload(left_components)
        right = rt.prepare_simple_polygon_component_payload(right_components)
        pair_rows = rt.prepare_overlay_area_pair_rows(left, right, ((0, 0), (1, 1)))
        tasks = rt.plan_prepared_overlay_area_tile_tasks(
            pair_rows,
            max_triangle_pairs_per_task=2,
            relation_row_ordinals=(5, 5),
        )
        summary = rt.summarize_prepared_overlay_area_tile_tasks(pair_rows, tasks)

        self.assertEqual(summary["status"], "accept", summary)
        self.assertEqual(summary["relation_row_count"], 1)
        self.assertEqual(summary["pair_row_count"], 2)
        self.assertEqual(summary["task_count"], 4)
        self.assertEqual({task.relation_row_ordinal for task in tasks}, {5})
        self.assertEqual([task.pair_row_ordinal for task in tasks], [0, 0, 1, 1])

    def test_tile_planner_fails_closed_for_invalid_capacity(self) -> None:
        with self.assertRaisesRegex(ValueError, "tile planning must fail closed"):
            rt.plan_prepared_overlay_area_tile_tasks(_fixture_pair_rows(), max_triangle_pairs_per_task=0)

    def test_summary_blocks_claims(self) -> None:
        pair_rows = _fixture_pair_rows()
        tasks = rt.plan_prepared_overlay_area_tile_tasks(pair_rows, max_triangle_pairs_per_task=3)
        summary = rt.summarize_prepared_overlay_area_tile_tasks(pair_rows, tasks)

        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "runtime_kernel_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(summary[field])

    def test_spatial_rayjoin_gap_row_records_tile_task_planner(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("relation-owner tile tasks", spatial["current_best_path"])
        self.assertIn("Goal3491 added a CuPy tile-task executor", spatial["current_bottleneck"])
        self.assertIn("Goal3490", spatial["evidence_refs"])
        self.assertFalse(spatial["release_authorized"])

    def test_report_documents_planner_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "component/tile tasks",
            "relation-row owner",
            "reduce by relation id",
            "does not authorize",
            "Goal3489",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
