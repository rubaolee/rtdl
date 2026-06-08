from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4011_grouped_union_partition_factor_sweep.json"
REPORT = ROOT / "docs" / "reports" / "goal4011_grouped_union_partition_factor_sweep_2026-06-08.md"
SCRIPT = ROOT / "scripts" / "goal3999_grouped_union_partition_feasibility_probe.py"


class Goal4011GroupedUnionPartitionFactorSweepTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_artifact_uses_reusable_goal_id_and_closed_boundaries(self) -> None:
        self.assertEqual(self.payload["goal"], "Goal4011")
        self.assertEqual(self.payload["status"], "pass")
        self.assertEqual(self.payload["source_commit"][:8], "743567c2")
        boundary = self.payload["interpretation_boundary"]
        self.assertTrue(boundary["cpu_feasibility_probe_only"])
        self.assertFalse(boundary["native_abi_added"])
        self.assertFalse(boundary["performance_claim_authorized"])
        self.assertFalse(boundary["release_authorized"])

    def test_script_remains_backward_compatible_for_goal3999(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('parser.add_argument("--goal", default="Goal3999")', script)
        self.assertIn('"goal": args.goal', script)

    def test_radius_one_eighth_is_best_tested_factor(self) -> None:
        rows = {row["profile"]: row for row in self.payload["rows"]}
        self.assertEqual(set(rows), {"clustered3d", "road3d", "ngsim_dense"})
        for profile, row in rows.items():
            best = row["best_ambiguous_pair_ratio"]
            self.assertEqual(best["cell_size_label"], "radius_x_0.125", profile)
            self.assertLess(best["ambiguous_pair_ratio"], 0.06 if profile != "ngsim_dense" else 0.001)
            self.assertGreater(best["safe_full_of_near_pair_ratio"], 0.60 if profile != "ngsim_dense" else 0.90)

    def test_finer_partition_signal_does_not_allow_dense_cell_pair_matrix(self) -> None:
        rows = {row["profile"]: row for row in self.payload["rows"]}
        ngsim_best = rows["ngsim_dense"]["best_ambiguous_pair_ratio"]
        self.assertGreater(ngsim_best["occupied_cells"], 60_000 - 1)
        self.assertGreater(ngsim_best["total_cell_pairs"], 1_800_000_000)
        for row in rows.values():
            factor_quarter = next(
                entry for entry in row["cell_factor_rows"]
                if entry["cell_size_label"] == "radius_x_0.25"
            )
            factor_eighth = row["best_ambiguous_pair_ratio"]
            self.assertLess(
                factor_eighth["ambiguous_pair_upper"],
                factor_quarter["ambiguous_pair_upper"],
            )

    def test_report_names_next_generic_native_columns_without_app_abi(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "`accept-with-boundary`",
            "not a performance optimization",
            "compressed occupied-cell structure",
            "bounded near-offset enumeration",
            "partition id per point",
            "partition AABBs",
            "not a DBSCAN native ABI",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
