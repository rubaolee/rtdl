from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4150_direct_status_single_pass_scale_sweep_factor025_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4150_direct_status_single_pass_scale_sweep_2026-06-09.md"


class Goal4150DirectStatusSinglePassScaleSweepTest(unittest.TestCase):
    def test_scale_sweep_matches_stable_and_is_faster(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual("Goal4150", data["goal"])
        self.assertEqual([65536, 131072, 262144, 524288], data["point_counts"])
        self.assertEqual(["clustered3d", "road3d", "ngsim_dense"], data["profiles"])
        self.assertEqual(0.25, data["partition_cell_factor"])
        self.assertTrue(data["all_signatures_match_until_stable"])
        self.assertGreater(data["minimum_replay_speedup"], 1.8)
        self.assertGreater(data["minimum_total_speedup"], 1.1)
        self.assertFalse(data["single_pass_promoted"])
        self.assertFalse(data["release_authorized"])
        self.assertFalse(data["public_speedup_claim_authorized"])
        self.assertFalse(data["automatic_partner_selection_authorized"])
        self.assertFalse(data["automatic_partition_cell_factor_selection_authorized"])

        self.assertEqual(12, len(data["rows"]))
        for row in data["rows"]:
            self.assertTrue(row["same_signature_vs_until_stable"], row)
            self.assertEqual(2, row["stable_union_iterations"])
            self.assertEqual(1, row["candidate_union_iterations"])
            self.assertEqual(1, row["candidate_final_changed_flag"])
            self.assertFalse(row["candidate_convergence_proven"])
            self.assertGreater(row["replay_speedup"], 1.8)
            self.assertGreater(row["total_speedup"], 1.1)

    def test_report_blocks_default_or_hidden_selection(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "accept-with-boundary",
            "not a universal theorem",
            "does not make it the default",
            "does not hide the",
            "does not authorize release",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
