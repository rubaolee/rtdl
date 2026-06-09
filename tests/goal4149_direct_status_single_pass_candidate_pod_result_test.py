from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4149_direct_status_single_pass_1m_factor025_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4149_direct_status_single_pass_candidate_pod_result_2026-06-09.md"


class Goal4149DirectStatusSinglePassCandidatePodResultTest(unittest.TestCase):
    def test_single_pass_matches_stable_and_improves_replay(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual("Goal4149", data["goal"])
        self.assertEqual(1048576, data["point_count"])
        self.assertEqual(0.25, data["partition_cell_factor"])
        self.assertTrue(data["all_signatures_match_until_stable"])
        self.assertFalse(data["single_pass_promoted"])
        self.assertFalse(data["release_authorized"])
        self.assertFalse(data["public_speedup_claim_authorized"])

        self.assertEqual({"clustered3d", "road3d", "ngsim_dense"}, {row["profile"] for row in data["rows"]})
        for row in data["rows"]:
            self.assertTrue(row["same_signature_vs_until_stable"], row["profile"])
            self.assertEqual(2, row["stable_union_iterations"])
            self.assertEqual(1, row["candidate_union_iterations"])
            self.assertEqual(1, row["candidate_final_changed_flag"])
            self.assertFalse(row["candidate_convergence_proven"])
            self.assertFalse(row["candidate_single_pass_promoted"])
            self.assertGreater(row["component_signature_speedup"], 1.9, row["profile"])
            self.assertGreater(row["total_speedup"], 1.3, row["profile"])

    def test_report_keeps_candidate_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "accept-with-boundary",
            "same-signature",
            "prove general",
            "universal default",
            "does not authorize release",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
