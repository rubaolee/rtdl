from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4144_direct_status_workspace_reuse_pod_result_2026-06-09.md"
BASELINE = ROOT / "docs" / "reports" / "goal4138_tuned_direct_status_warm_one_shot_1m_factor025_pod.json"
CANDIDATE = ROOT / "docs" / "reports" / "goal4144_direct_status_workspace_reuse_1m_factor025_pod.json"


class Goal4144DirectStatusWorkspaceReusePodResultTest(unittest.TestCase):
    def test_candidate_preserves_signatures_but_is_not_a_default_win(self) -> None:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))

        self.assertEqual(1048576, candidate["point_count"])
        self.assertEqual([0.25], candidate["partition_cell_factors"])
        self.assertFalse(candidate["release_authorized"])
        self.assertFalse(candidate["public_speedup_claim_authorized"])
        self.assertFalse(candidate["automatic_partner_selection_authorized"])

        by_profile = {row["profile"]: row for row in candidate["rows"]}
        base_by_profile = {row["profile"]: row for row in baseline["rows"]}
        self.assertEqual({"clustered3d", "road3d", "ngsim_dense"}, set(by_profile))
        for profile, row in by_profile.items():
            factor = row["factor_rows"][0]
            base_factor = base_by_profile[profile]["factor_rows"][0]
            self.assertTrue(row["all_factors_match_current_signature"])
            self.assertTrue(factor["same_signature"])
            self.assertLessEqual(
                base_factor["amortized_sec"] / factor["amortized_sec"],
                1.0,
                f"{profile} workspace candidate should not be treated as a one-shot win",
            )

    def test_report_rejects_candidate_as_performance_default(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "reject-as-performance-default",
            "not a meaningful performance win",
            "per-replay parent/counter allocation is not the dominant",
            "Do not promote workspace reuse as the default performance route.",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
