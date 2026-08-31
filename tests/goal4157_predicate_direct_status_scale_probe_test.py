from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4157_predicate_direct_status_scale_factor025_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4157_predicate_direct_status_scale_probe_2026-06-09.md"


class Goal4157PredicateDirectStatusScaleProbeTest(unittest.TestCase):
    def test_scale_artifact_preserves_same_contract_and_boundary(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        comparisons = artifact["comparisons"]
        self.assertEqual(len(comparisons), 18)
        self.assertTrue(all(row["same_signature"] for row in comparisons))
        self.assertTrue(any(row["speedup_current_over_candidate"] > 1.0 for row in comparisons))
        self.assertTrue(any(row["speedup_current_over_candidate"] < 1.0 for row in comparisons))

        single_pass = [row for row in comparisons if row["candidate"] == "predicate_direct_status_single_pass"]
        self.assertTrue(single_pass)
        self.assertTrue(all(row["candidate_convergence_proven"] is False for row in single_pass))
        self.assertTrue(all(row["candidate_final_changed_flag"] == 1 for row in single_pass))

        boundary = artifact["claim_boundary"]
        for key in (
            "route_promotion_authorized",
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "whole_app_claim_authorized",
        ):
            self.assertIs(boundary[key], False)

    def test_report_states_mixed_performance_not_promotion(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "same-contract-achieved-performance-mixed",
            "All 18 comparisons matched",
            "no route promotion is authorized",
            "right contract, not yet fast enough everywhere",
            "reduce safe-full partition border-candidate work",
            "does not authorize route promotion",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
