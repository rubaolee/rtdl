import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2865_current_head_packet_after_front_doors_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2866_gemini_review_goal2865_current_head_packet_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2866_goal2865_current_head_packet_consensus_2026-05-31.md"
SUMMARY = ROOT / "docs" / "reports" / "goal2865_current_packet_after_front_doors_pod" / "goal2855_summary.json"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2865_current_packet_after_front_doors_pod"


class Goal2865CurrentHeadPacketAfterFrontDoorsTest(unittest.TestCase):
    def test_preserved_packet_summary_is_clean_and_current_head(self) -> None:
        data = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual("pass", data["status"])
        self.assertTrue(data["all_pass"])
        self.assertEqual(7, data["artifact_count"])
        self.assertEqual(7, data["expected_artifact_count"])
        self.assertTrue(data["source_commit_consistent"])
        self.assertEqual("3c5efc3130829aced34abb34f5863d3f3b652ad5", data["source_commit"])
        self.assertEqual([], data["runner_metadata"]["source_dirty"])
        self.assertEqual({}, data["dirty_artifacts"])
        self.assertEqual({}, data["claim_boundary_violations"])
        self.assertTrue(data["claim_boundary"]["compact_child_output_safe_to_use"])
        self.assertFalse(data["claim_boundary"]["v2_5_release_authorized"])

    def test_all_child_artifacts_are_preserved_and_bounded(self) -> None:
        data = json.loads(SUMMARY.read_text(encoding="utf-8"))
        expected = {
            "goal2797_triangle_counting.json",
            "goal2798_librts.json",
            "goal2799_spatial_rayjoin.json",
            "goal2800_rtnn.json",
            "goal2801_hausdorff_xhd.json",
            "goal2802_rt_dbscan.json",
            "goal2803_barnes_hut.json",
        }

        self.assertEqual(expected, set(data["artifacts"]))
        for name in expected:
            with self.subTest(name=name):
                artifact_path = ARTIFACT_DIR / name
                self.assertTrue(artifact_path.exists(), name)
                artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
                self.assertEqual("pass", artifact["status"])
                self.assertEqual("3c5efc3130829aced34abb34f5863d3f3b652ad5", artifact["source_commit"])
                self.assertEqual([], artifact["source_dirty"])

    def test_readiness_packet_preserves_goal2865_but_points_to_newer_runner_summary(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2866_goal2865_current_head_packet_consensus_2026-05-31.md"
            ]
        )
        self.assertTrue(
            packet["external_review_presence"][
                "docs/reviews/goal2866_gemini_review_goal2865_current_head_packet_2026-05-31.md"
            ]
        )
        self.assertIn("goal2876_current_packet_after_conformance_pod", packet["current_canonical_runner"]["summary_path"])
        self.assertEqual("cb9345bea472ac1167e8c289050146cc4fae30aa", packet["current_canonical_runner"]["source_commit"])
        self.assertEqual(7, packet["current_canonical_runner"]["artifact_count"])

    def test_report_review_and_consensus_record_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        for phrase in (
            "Goal2865",
            "source commit",
            "3c5efc3130829aced34abb34f5863d3f3b652ad5",
            "artifact_count: 7",
            "claim_boundary_violations: {}",
            "not a v2.5 release authorization",
        ):
            self.assertIn(phrase, text)
        self.assertIn("Verdict:** `accept`", review)
        self.assertIn("Consensus verdict: `accept-with-boundary`", consensus)


if __name__ == "__main__":
    unittest.main()
