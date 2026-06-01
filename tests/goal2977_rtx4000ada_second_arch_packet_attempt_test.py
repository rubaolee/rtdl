from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2977_rtx4000ada_second_arch_packet_attempt_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2977_rtx4000ada_second_arch_packet_pod"


class Goal2977Rtx4000AdaSecondArchAttemptTest(unittest.TestCase):
    def test_report_preserves_release_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not release-authorizing", text)
        self.assertIn("six app harnesses passed", text)
        self.assertIn("canonical second-architecture packet is not 7/7 green", text)
        self.assertIn("OptiX error: Unsupported ABI version", text)
        self.assertIn("OPTIX_VERSION 80100", text)
        self.assertIn("accept-with-boundary", text)

    def test_canonical_attempt_is_clean_partial_packet(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "goal2855_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "fail")
        self.assertFalse(summary["all_pass"])
        self.assertEqual(summary["artifact_count"], 6)
        self.assertEqual(summary["expected_artifact_count"], 7)
        self.assertEqual(summary["source_commit"], "b353be863887fa3b826fc639ea5811d939e93dff")
        self.assertEqual(summary["dirty_artifacts"], {})
        self.assertEqual(summary["claim_boundary_violations"], {})

        passing = [
            "goal2797_triangle_counting.json",
            "goal2798_librts.json",
            "goal2799_spatial_rayjoin.json",
            "goal2800_rtnn.json",
            "goal2801_hausdorff_xhd.json",
            "goal2802_rt_dbscan.json",
        ]
        for name in passing:
            with self.subTest(name=name):
                payload = json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["source_dirty"], [])

    def test_bounded_barnes_hut_followup_records_real_second_arch_evidence(self) -> None:
        payload = json.loads(
            (ARTIFACT_DIR / "goal2977_barnes_hut_bounded_512_2048.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["status"], "pass")
        self.assertIn("RTX 4000 Ada", payload["gpu"])
        self.assertEqual(payload["source_commit"], "b353be863887fa3b826fc639ea5811d939e93dff")
        self.assertGreater(payload["min_optix_membership_speedup_vs_embree"], 100.0)
        self.assertGreater(payload["max_optix_membership_speedup_vs_embree"], 500.0)
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["paper_reproduction_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["native_engine_customization"])
        for row in payload["membership_rows"]:
            self.assertTrue(row["rows_match_between_backends"])
            self.assertTrue(row["optix_rt_core_accelerated"])


if __name__ == "__main__":
    unittest.main()
