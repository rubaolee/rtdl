from __future__ import annotations

import unittest

from scripts.goal1100_post_pod_baseline_gap_audit import build_audit
from scripts.goal1100_post_pod_baseline_gap_audit import to_markdown


class Goal1100PostPodBaselineGapAuditTest(unittest.TestCase):
    def test_audit_is_valid_but_authorizes_no_public_claims(self) -> None:
        payload = build_audit()

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["row_count"], 2)
        self.assertEqual(payload["summary"]["rtx_correct_count"], 2)
        self.assertEqual(payload["summary"]["baseline_missing_or_partial_count"], 2)
        self.assertEqual(payload["summary"]["public_speedup_claim_ready_count"], 0)
        self.assertIn("does not authorize public RTX speedup claims", payload["boundary"])

    def test_facility_has_partial_cpu_oracle_but_not_public_wording_baseline(self) -> None:
        rows = {row["app"]: row for row in build_audit()["rows"]}
        facility = rows["facility_knn_assignment"]

        self.assertTrue(facility["rtx_correctness"])
        self.assertEqual(
            facility["baseline_status"],
            "partial_cpu_oracle_present_needs_fastest_non_optix_phase_baseline",
        )
        self.assertFalse(facility["public_speedup_claim_ready"])
        self.assertIn("recentered", facility["path_name"])
        self.assertIn("fastest non-OptiX phase-separated baseline", facility["next_action"])
        self.assertIsInstance(facility["rtx_query_median_sec"], float)

    def test_barnes_has_current_contract_baseline_gap(self) -> None:
        rows = {row["app"]: row for row in build_audit()["rows"]}
        barnes = rows["barnes_hut_force_app"]

        self.assertTrue(barnes["rtx_correctness"])
        self.assertFalse(barnes["rtx_timing_has_validation"])
        self.assertEqual(barnes["baseline_status"], "current_contract_baseline_missing")
        self.assertFalse(barnes["public_speedup_claim_ready"])
        self.assertIn("20M timing contract", barnes["next_action"])
        self.assertIsInstance(barnes["rtx_validation_query_median_sec"], float)
        self.assertIsInstance(barnes["rtx_timing_query_median_sec"], float)

    def test_markdown_exposes_gap_rows(self) -> None:
        markdown = to_markdown(build_audit())

        self.assertIn("Goal1100 Post-Pod Baseline Gap Audit", markdown)
        self.assertIn("partial_cpu_oracle_present", markdown)
        self.assertIn("current_contract_baseline_missing", markdown)
        self.assertIn("same-current-contract baseline review", markdown)


if __name__ == "__main__":
    unittest.main()
