from __future__ import annotations

import importlib
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3523_v2_8_vs_v2_3_same_contract_comparison_protocol_2026-06-05.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal3523_v2_8_vs_v2_3_same_contract_comparison_protocol_3ai_consensus_2026-06-05.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal3523_claude_review_v2_8_vs_v2_3_comparison_protocol_2026-06-05.md"
GEMINI_REREVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal3523_gemini_rereview_v2_8_vs_v2_3_comparison_protocol_after_corrections_2026-06-05.md"
)


class Goal3523V28VsV23SameContractComparisonTest(unittest.TestCase):
    def setUp(self) -> None:
        self.module = importlib.import_module("rtdsl.v2_8_vs_v2_3_benchmark_comparison")

    def test_all_v2_8_benchmark_apps_are_represented(self) -> None:
        rows = self.module.v2_8_vs_v2_3_benchmark_comparison()
        apps = {row["app"] for row in rows}
        self.assertEqual(
            apps,
            {
                "hausdorff_xhd",
                "spatial_rayjoin",
                "rt_dbscan",
                "robot_collision",
                "contact_manifold",
                "raydb_style",
                "barnes_hut",
                "librts_spatial_index",
                "rtnn",
                "triangle_counting",
            },
        )
        self.assertEqual(len(rows), 10)

    def test_contact_manifold_records_v2_3_tag_current_report_drift(self) -> None:
        rows = {row["app"]: row for row in self.module.v2_8_vs_v2_3_benchmark_comparison()}
        contact = rows["contact_manifold"]
        self.assertTrue(contact["v2_3_promoted"])
        self.assertEqual(contact["comparison_class"], "fresh_same_contract_pod_required")
        self.assertEqual(contact["v2_3_optix_sec"], 0.0184764)
        self.assertIn("tag text listed nine apps", contact["boundary"])
        self.assertIn("same AABB broadphase collect-k contract", contact["required_next_action"])

    def test_most_rows_require_fresh_same_contract_pod_run(self) -> None:
        rows = self.module.v2_8_vs_v2_3_benchmark_comparison()
        blocked = [row for row in rows if row["comparison_class"] == "fresh_same_contract_pod_required"]
        self.assertGreaterEqual(len(blocked), 6)
        for row in blocked:
            self.assertFalse(row["ratio_authorized_from_existing_artifacts"], row["app"])
            self.assertIsNone(row["v2_8_speedup_vs_v2_3"], row["app"])
            self.assertIn("run", row["required_next_action"].lower())

    def test_only_explicit_rows_have_existing_artifact_ratios(self) -> None:
        rows = self.module.v2_8_vs_v2_3_benchmark_comparison()
        authorized = [row for row in rows if row["ratio_authorized_from_existing_artifacts"]]
        self.assertEqual({row["app"] for row in authorized}, {"rt_dbscan", "triangle_counting"})
        ratios = {row["app"]: row["v2_8_speedup_vs_v2_3"] for row in authorized}
        self.assertGreater(ratios["rt_dbscan"], 5.0)
        self.assertLess(ratios["triangle_counting"], 1.0)
        rt_dbscan = next(row for row in authorized if row["app"] == "rt_dbscan")
        self.assertIn("total-run figure", rt_dbscan["boundary"])
        self.assertIn("tail median", rt_dbscan["boundary"])

    def test_summary_and_validation_keep_claims_blocked(self) -> None:
        summary = self.module.summarize_v2_8_vs_v2_3_benchmark_comparison()
        validation = self.module.validate_v2_8_vs_v2_3_benchmark_comparison()
        self.assertEqual(validation["status"], "accept", validation["errors"])
        self.assertTrue(summary["pod_required_before_final_all_app_table"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_claim_authorized"])
        self.assertEqual(summary["app_count"], 10)
        self.assertEqual(summary["authorized_existing_artifact_ratio_count"], 2)

    def test_report_states_protocol_not_final_results(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("protocol ready; fresh RTX pod evidence required", text)
        self.assertIn("The final comparison packet must say which one each row uses.", text)
        self.assertIn("tag/current-report drift", text)
        self.assertIn("Goal3523 is ready for pod execution", text)
        self.assertIn("not yet the final all-app comparison", text)
        forbidden = (
            "public v2.8 release " + "authorized",
            "public speedup claim " + "authorized",
            "whole-app speedup claim " + "authorized",
            "true zero-copy claim " + "authorized",
        )
        lowered = text.lower()
        for phrase in forbidden:
            self.assertNotIn(phrase, lowered)

    def test_external_reviews_and_consensus_record_corrections(self) -> None:
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8").lower()
        gemini = GEMINI_REREVIEW.read_text(encoding="utf-8").lower()
        consensus = CONSENSUS.read_text(encoding="utf-8").lower()
        self.assertIn("accept-with-boundary", claude)
        self.assertIn("contact_manifold promotion boundary is factually wrong", claude)
        self.assertIn("accept-with-boundary", gemini)
        self.assertIn("contact_manifold", gemini)
        self.assertIn("tag/current-report drift", consensus)
        self.assertIn("ready for pod execution", consensus)
        self.assertIn("not the final performance comparison", consensus)


if __name__ == "__main__":
    unittest.main()
