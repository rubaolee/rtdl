from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4024_partition_summary_edge_case_strengthening_2026-06-08.md"


class Goal4024PartitionSummaryEdgeCaseStrengtheningTest(unittest.TestCase):
    def test_single_point_summary_and_component_labels_are_complete(self) -> None:
        points = ((7, 0.0, 0.0, 0.0),)
        summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
        )
        self.assertEqual(summary["columns"]["point_partition_ids"], (0,))
        self.assertEqual(summary["columns"]["near_pair_status"], (1,))
        self.assertTrue(summary["metadata"]["complete_candidate_coverage"])
        component = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
            partition_summary=summary,
        )
        self.assertEqual(component["metadata"]["status"], "accept")
        self.assertEqual(component["columns"]["point_ids"], (7,))
        self.assertEqual(component["columns"]["component_labels"], (0,))

    def test_summary_can_exercise_all_near_pair_status_values(self) -> None:
        points = (
            (0.0, 0.0, 0.0),
            (0.2, 0.0, 0.0),
            (1.2, 0.0, 0.0),
            (1.5, 0.0, 0.0),
        )
        summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
        )
        statuses = set(summary["columns"]["near_pair_status"])
        self.assertEqual(statuses, {0, 1, 2})
        self.assertGreater(summary["metadata"]["status_counts"]["safe_skip_partition_pairs"], 0)
        self.assertGreater(summary["metadata"]["status_counts"]["safe_full_partition_pairs"], 0)
        self.assertGreater(summary["metadata"]["status_counts"]["ambiguous_partition_pairs"], 0)
        component = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
            partition_summary=summary,
        )
        self.assertEqual(component["metadata"]["status"], "accept")
        self.assertTrue(component["metadata"]["same_contract_against_all_pairs"])

    def test_float_tolerance_accepts_small_aabb_drift_and_rejects_large_drift(self) -> None:
        points = (
            (0.0, 0.0, 0.0),
            (0.2, 0.0, 0.0),
            (1.2, 0.0, 0.0),
            (3.0, 0.0, 0.0),
        )
        summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
        )
        small_drift = {"columns": dict(summary["columns"]), "metadata": dict(summary["metadata"])}
        small_drift["columns"]["partition_aabb_max_x"] = tuple(
            value + 1.0e-7 for value in summary["columns"]["partition_aabb_max_x"]
        )
        accepted = rt.validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
            candidate=small_drift,
            float_abs_tol=1.0e-6,
        )
        self.assertEqual(accepted["status"], "accept")

        large_drift = {"columns": dict(summary["columns"]), "metadata": dict(summary["metadata"])}
        large_drift["columns"]["partition_aabb_max_x"] = tuple(
            value + 1.0e-3 for value in summary["columns"]["partition_aabb_max_x"]
        )
        rejected = rt.validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
            candidate=large_drift,
            float_abs_tol=1.0e-6,
        )
        self.assertEqual(rejected["status"], "reject")
        self.assertIn("partition_aabb_max_x", rejected["mismatch_columns"])

    def test_report_records_edge_case_strengthening(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "single point",
            "safe-skip",
            "safe-full",
            "ambiguous",
            "floating-point tolerance",
            "does not add a native ABI",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
