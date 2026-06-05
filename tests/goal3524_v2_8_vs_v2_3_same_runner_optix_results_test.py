from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3524_pod_artifacts" / "goal3524_compact_results.json"
REPORT = ROOT / "docs" / "reports" / "goal3524_v2_8_vs_v2_3_same_runner_optix_results_2026-06-05.md"
REVIEW_STATUS = ROOT / "docs" / "reports" / "goal3524_external_review_status_2026-06-05.md"
GEMINI_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal3526_gemini_review_goal3524_v2_8_vs_v2_3_same_runner_optix_results_2026-06-05.md"
)


class Goal3524V28VsV23SameRunnerOptixResultsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.report = REPORT.read_text(encoding="utf-8")

    def test_artifact_records_expected_scope_and_commits(self) -> None:
        self.assertEqual(
            self.artifact["schema"],
            "rtdl.goal3524.v2_8_vs_v2_3_same_runner_optix.v1",
        )
        self.assertEqual(
            self.artifact["status"],
            "internal_same_runner_optix_results_not_public_claims",
        )
        self.assertIn("OptiX", self.artifact["comparison_scope"])
        self.assertEqual(
            self.artifact["v23_evidence_commit"],
            "2a28365d0246d51f3e3322b546f8a68c58632db4",
        )
        self.assertEqual(
            self.artifact["v28_commit"],
            "d266b0370bcbcd4cbc24006ce9de2dfe783c1d2e",
        )
        self.assertIn("RTX A5000", self.artifact["gpu"])

    def test_all_standard_rows_completed_and_summary_is_pinned(self) -> None:
        rows = self.artifact["rows"]
        self.assertEqual(len(rows), 11)
        self.assertEqual({row["v23_status"] for row in rows}, {"ok"})
        self.assertEqual({row["v28_status"] for row in rows}, {"ok"})
        summary = self.artifact["summary"]
        self.assertEqual(summary["row_count"], 11)
        self.assertEqual(summary["ok_pair_count"], 11)
        self.assertEqual(summary["v28_win_count"], 6)
        self.assertEqual(summary["v28_loss_count"], 5)
        self.assertGreater(summary["geomean_speedup"], 1.13)
        self.assertLess(summary["geomean_speedup"], 1.15)
        self.assertGreater(summary["median_speedup"], 0.99)
        self.assertLess(summary["median_speedup"], 1.02)

    def test_strong_win_and_real_regression_remain_visible(self) -> None:
        rows = {row["case_id"]: row for row in self.artifact["rows"]}
        raydb_sum = rows["raydb_optix_partner_resident_sum"]
        self.assertGreater(raydb_sum["v28_speedup_vs_v23"], 7.0)
        self.assertLess(raydb_sum["v28_sec"], raydb_sum["v23_sec"])

        barnes = rows["barnes_hut_optix_node_coverage"]
        self.assertLess(barnes["v28_speedup_vs_v23"], 0.41)
        self.assertGreater(barnes["v28_sec"], barnes["v23_sec"])

    def test_weak_rerun_confirms_barnes_hut_and_bounds_noise_rows(self) -> None:
        weak = {row["case_id"]: row for row in self.artifact["weak_rerun_rows"]}
        self.assertEqual(
            set(weak),
            {
                "barnes_hut_optix_node_coverage",
                "contact_manifold_optix_aabb_broadphase_collect_k",
                "raydb_optix_partner_resident_count",
                "robot_collision_optix_prepared_device_buffers",
                "triangle_counting_optix_rt_graph_2a1_partner",
            },
        )
        self.assertLess(weak["barnes_hut_optix_node_coverage"]["v28_speedup_vs_v23"], 0.51)
        self.assertLess(weak["robot_collision_optix_prepared_device_buffers"]["v28_speedup_vs_v23"], 0.98)
        self.assertGreater(weak["contact_manifold_optix_aabb_broadphase_collect_k"]["v28_speedup_vs_v23"], 1.0)
        self.assertGreater(weak["triangle_counting_optix_rt_graph_2a1_partner"]["v28_speedup_vs_v23"], 1.0)

    def test_claim_boundary_authorizes_nothing(self) -> None:
        boundary = self.artifact["claim_boundary"]
        self.assertTrue(boundary["internal_results_only"])
        for key, value in boundary.items():
            if key == "internal_results_only":
                continue
            self.assertIs(value, False, key)

    def test_report_states_scope_and_refuses_public_claims(self) -> None:
        text = self.report
        self.assertIn("same `scripts/goal2626_benchmark_embree_optix_baseline.py`", text)
        self.assertIn("not the literal", text)
        self.assertIn("root@69.30.85.203 -p 22057", text)
        self.assertIn("id_ed25519_rtdl_codex", text)
        self.assertIn("v2.8 is not uniformly faster", text)
        self.assertIn("Barnes-Hut node coverage is the real regression", text)
        self.assertIn("Goal3524 does not authorize", text)
        forbidden = (
            "public v2.8 release " + "authorized",
            "public speedup claim " + "authorized",
            "whole-app speedup claim " + "authorized",
            "true zero-copy claim " + "authorized",
        )
        lowered = text.lower()
        for phrase in forbidden:
            self.assertNotIn(phrase, lowered)

    def test_external_review_status_is_honest_about_consensus(self) -> None:
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        status = REVIEW_STATUS.read_text(encoding="utf-8")
        self.assertIn("accept-with-boundary", gemini)
        self.assertIn("6-win/5-loss", status)
        self.assertIn("Claude review pending", status)
        self.assertIn("claim 3-AI consensus", status)
        self.assertIn("must not be used as a final v2.8 public comparison", status)


if __name__ == "__main__":
    unittest.main()
