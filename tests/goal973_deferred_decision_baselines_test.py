from __future__ import annotations

import unittest


class Goal973DeferredDecisionBaselinesTest(unittest.TestCase):
    def test_deferred_decision_rows_have_valid_local_baselines(self) -> None:
        module = __import__("scripts.goal836_rtx_baseline_readiness_gate", fromlist=["analyze_plan"])
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.analyze_plan()["rows"]
        }
        for key in (
            ("facility_knn_assignment", "coverage_threshold_prepared"),
            ("hausdorff_distance", "directed_threshold_prepared"),
            ("ann_candidate_search", "candidate_threshold_prepared"),
            ("barnes_hut_force_app", "node_coverage_prepared"),
        ):
            with self.subTest(app=key[0], path=key[1]):
                row = rows[key]
                self.assertEqual(row["row_status"], "ok")
                self.assertTrue(row["artifact_checks"])
                self.assertTrue(all(check["status"] == "valid" for check in row["artifact_checks"]))

    def test_goal971_counts_reflect_new_valid_baselines_without_speedup_claims(self) -> None:
        module = __import__(
            "scripts.goal971_post_goal969_baseline_speedup_review_package",
            fromlist=["build_package"],
        )
        payload = module.build_package()
        self.assertEqual(payload["same_semantics_baselines_complete_count"], 17)
        self.assertEqual(payload["active_gate_limited_count"], 0)
        self.assertEqual(payload["baseline_pending_count"], 0)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)


if __name__ == "__main__":
    unittest.main()
