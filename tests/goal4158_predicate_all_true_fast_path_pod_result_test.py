from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4158_predicate_all_true_fast_path_scale_factor025_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4158_predicate_all_true_fast_path_pod_result_2026-06-09.md"


class Goal4158PredicateAllTrueFastPathPodResultTest(unittest.TestCase):
    def test_artifact_proves_fast_path_without_promotion(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal4158")
        self.assertEqual(artifact["git_commit"], "b1d220ed")

        comparisons = artifact["comparisons"]
        self.assertEqual(len(comparisons), 18)
        self.assertTrue(all(row["same_signature"] for row in comparisons))
        self.assertTrue(all(row["candidate_all_predicate_fast_path"] is True for row in comparisons))
        self.assertTrue(all(row["candidate_border_candidate_updates"] == 0 for row in comparisons))

        stable = [row for row in comparisons if row["candidate"] == "predicate_direct_status_until_stable"]
        single_pass = [row for row in comparisons if row["candidate"] == "predicate_direct_status_single_pass"]
        self.assertEqual(len(stable), 9)
        self.assertEqual(len(single_pass), 9)
        self.assertEqual(sum(row["speedup_current_over_candidate"] > 1.0 for row in stable), 8)
        self.assertEqual(sum(row["speedup_current_over_candidate"] > 1.0 for row in single_pass), 9)
        self.assertLess(min(row["speedup_current_over_candidate"] for row in stable), 1.0)
        self.assertGreater(min(row["speedup_current_over_candidate"] for row in single_pass), 1.0)

        for row in stable:
            self.assertIs(row["candidate_convergence_proven"], True)
            self.assertEqual(row["candidate_final_changed_flag"], 0)
        for row in single_pass:
            self.assertIs(row["candidate_convergence_proven"], False)
            self.assertEqual(row["candidate_final_changed_flag"], 1)

        boundary = artifact["claim_boundary"]
        for key in (
            "route_promotion_authorized",
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "whole_app_claim_authorized",
        ):
            self.assertIs(boundary[key], False)

    def test_report_states_scope_and_next_step(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted as a candidate-route improvement, not promoted as a default route",
            "moved it into `_run_predicate_direct_status_union_signature_from_prepared_columns_cupy_3d`",
            "Same-contract correctness: 18/18 matched",
            "Fast path observed: 18/18 candidate rows",
            "Until-stable route: faster on 8/9 rows",
            "Single-pass candidate route: faster on 9/9 rows",
            "does not authorize route promotion yet",
            "mixed-predicate scale packet",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
