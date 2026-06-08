from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4014_compressed_partition_enumeration_accounting.json"
REPORT = ROOT / "docs" / "reports" / "goal4014_compressed_partition_enumeration_accounting_2026-06-08.md"
SCRIPT = ROOT / "scripts" / "goal3999_grouped_union_partition_feasibility_probe.py"


class Goal4014CompressedPartitionEnumerationAccountingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_artifact_is_non_authorizing_goal4014_evidence(self) -> None:
        self.assertEqual(self.payload["goal"], "Goal4014")
        self.assertEqual(self.payload["status"], "pass")
        boundary = self.payload["interpretation_boundary"]
        self.assertTrue(boundary["cpu_feasibility_probe_only"])
        self.assertFalse(boundary["native_abi_added"])
        self.assertFalse(boundary["performance_claim_authorized"])
        self.assertFalse(boundary["release_authorized"])

    def test_radius_one_eighth_rows_expose_compressed_enumeration_accounting(self) -> None:
        rows = {row["profile"]: row for row in self.payload["rows"]}
        self.assertEqual(set(rows), {"clustered3d", "road3d", "ngsim_dense"})
        for profile, row in rows.items():
            self.assertEqual(len(row["cell_factor_rows"]), 1, profile)
            factor = row["cell_factor_rows"][0]
            self.assertEqual(factor["cell_size_label"], "radius_x_0.125")
            self.assertEqual(factor["enumeration_strategy"], "compressed_occupied_key_bounded_offsets")
            self.assertFalse(factor["dense_cell_pair_matrix_materialized"])
            self.assertGreater(factor["bounded_offset_count"], 0)
            self.assertGreater(factor["total_cell_pairs"], factor["enumerated_cell_pairs"])
            self.assertLess(factor["enumerated_cell_pair_ratio"], 1.0)
            self.assertGreater(factor["far_safe_skip_pair_upper"], 0)
            self.assertGreater(factor["far_safe_skip_pair_ratio"], 0.0)
            accounted = (
                int(factor["safe_full_pair_upper"])
                + int(factor["safe_skip_pair_upper"])
                + int(factor["ambiguous_pair_upper"])
            )
            self.assertEqual(accounted, int(factor["total_pair_upper"]))

    def test_ngsim_dense_gets_largest_dense_matrix_avoidance_signal(self) -> None:
        rows = {row["profile"]: row for row in self.payload["rows"]}
        ngsim = rows["ngsim_dense"]["cell_factor_rows"][0]
        self.assertGreater(ngsim["total_cell_pairs"], 1_800_000_000)
        self.assertLess(ngsim["enumerated_cell_pair_ratio"], 0.02)
        self.assertLess(ngsim["ambiguous_of_near_pair_ratio"], 0.07)

    def test_script_and_report_record_no_dense_matrix_boundary(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "compressed_occupied_key_bounded_offsets",
            "dense_cell_pair_matrix_materialized",
            "far_safe_skip_pair_upper",
            "no dense cell-pair matrix",
            "does not authorize public speedup wording",
            "does not add a native ABI",
        ):
            self.assertIn(fragment, script + "\n" + report)


if __name__ == "__main__":
    unittest.main()
