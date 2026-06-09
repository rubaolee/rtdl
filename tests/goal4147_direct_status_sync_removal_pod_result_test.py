from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4147_direct_status_sync_removal_pod_result_2026-06-09.md"
BASELINE = ROOT / "docs" / "reports" / "goal4138_tuned_direct_status_warm_one_shot_1m_factor025_pod.json"
CANDIDATE = ROOT / "docs" / "reports" / "goal4147_direct_status_sync_removal_1m_factor025_pod.json"


class Goal4147DirectStatusSyncRemovalPodResultTest(unittest.TestCase):
    def test_sync_removal_is_replay_cleanup_not_one_shot_promotion(self) -> None:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))

        self.assertEqual(1048576, candidate["point_count"])
        self.assertEqual([0.25], candidate["partition_cell_factors"])
        self.assertFalse(candidate["release_authorized"])
        self.assertFalse(candidate["public_speedup_claim_authorized"])
        self.assertFalse(candidate["automatic_partner_selection_authorized"])

        by_profile = {row["profile"]: row for row in candidate["rows"]}
        base_by_profile = {row["profile"]: row for row in baseline["rows"]}
        for profile, row in by_profile.items():
            factor = row["factor_rows"][0]
            base_factor = base_by_profile[profile]["factor_rows"][0]
            replay_ratio = base_factor["replay_sec"] / factor["replay_sec"]
            total_ratio = base_factor["amortized_sec"] / factor["amortized_sec"]
            self.assertTrue(row["all_factors_match_current_signature"])
            self.assertTrue(factor["same_signature"])
            self.assertGreater(replay_ratio, 1.0, f"{profile} replay should be slightly faster")
            self.assertLess(total_ratio, 1.0, f"{profile} one-shot total should not be promoted")

    def test_report_blocks_claim_expansion(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "accept-with-boundary",
            "valid replay-path cleanup",
            "should not be marketed as a benchmark win",
            "promote a one-shot route claim",
            "does not authorize public speedup wording",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
