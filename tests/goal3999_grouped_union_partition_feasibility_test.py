from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3999_grouped_union_partition_feasibility.json"
REPORT = ROOT / "docs" / "reports" / "goal3999_grouped_union_partition_feasibility_2026-06-08.md"


class Goal3999GroupedUnionPartitionFeasibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_artifact_is_non_authorizing_feasibility_evidence(self) -> None:
        self.assertEqual(self.artifact["goal"], "Goal3999")
        self.assertEqual(self.artifact["status"], "pass")
        boundary = self.artifact["interpretation_boundary"]
        self.assertTrue(boundary["cpu_feasibility_probe_only"])
        self.assertFalse(boundary["native_abi_added"])
        self.assertFalse(boundary["performance_claim_authorized"])
        self.assertFalse(boundary["release_authorized"])

    def test_current_benchmark_radii_are_separate_from_stress_radius(self) -> None:
        rows = self.artifact["rows"]
        current = {
            row["profile"]: row
            for row in rows
            if row["purpose"] == "current_benchmark_default_radius"
        }
        self.assertEqual(set(current), {"clustered3d", "road3d", "ngsim_dense"})
        self.assertAlmostEqual(current["clustered3d"]["radius"], 0.055)
        self.assertAlmostEqual(current["road3d"]["radius"], 0.030)
        self.assertAlmostEqual(current["ngsim_dense"]["radius"], 0.012)

        stress_rows = [row for row in rows if row["purpose"] == "stress_radius_not_current_benchmark_default"]
        self.assertEqual(len(stress_rows), 1)
        self.assertEqual(stress_rows[0]["profile"], "clustered3d")
        self.assertAlmostEqual(stress_rows[0]["radius"], 0.5)

    def test_partition_accounting_is_consistent(self) -> None:
        for row in self.artifact["rows"]:
            for cell_row in row["cell_factor_rows"]:
                total = int(cell_row["total_pair_upper"])
                partition_sum = (
                    int(cell_row["safe_full_pair_upper"])
                    + int(cell_row["safe_skip_pair_upper"])
                    + int(cell_row["ambiguous_pair_upper"])
                )
                self.assertEqual(partition_sum, total)
                self.assertGreaterEqual(cell_row["decided_pair_ratio"], 0.0)
                self.assertLessEqual(cell_row["decided_pair_ratio"], 1.0)
                near = int(cell_row["near_pair_upper"])
                self.assertEqual(
                    near,
                    int(cell_row["safe_full_pair_upper"]) + int(cell_row["ambiguous_pair_upper"]),
                )

    def test_results_show_hybrid_not_plain_partition_direction(self) -> None:
        current_rows = [
            row for row in self.artifact["rows"]
            if row["purpose"] == "current_benchmark_default_radius"
        ]
        for row in current_rows:
            best = row["best_ambiguous_pair_ratio"]
            self.assertEqual(best["cell_size_label"], "radius_x_0.25")
            self.assertGreater(best["ambiguous_of_near_pair_ratio"], 0.50)
        stress = next(
            row for row in self.artifact["rows"]
            if row["purpose"] == "stress_radius_not_current_benchmark_default"
        )
        self.assertGreater(stress["best_ambiguous_pair_ratio"]["ambiguous_pair_ratio"], 0.40)

    def test_report_records_boundary_and_next_generic_direction(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "`needs-more-evidence`",
            "stress-only",
            "hybrid primitive",
            "not a plain grid rewrite",
            "device-resident partition",
            "DBSCAN, clusters, epsilon/min-points",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
