from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal4074_rt_dbscan_grouped_stream_bottleneck_refresh.py"
REPORT = ROOT / "docs" / "reports" / "goal4074_rt_dbscan_grouped_stream_bottleneck_refresh_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4074_rt_dbscan_grouped_stream_bottleneck_refresh_pod.json"


class Goal4074RtDbscanGroupedStreamBottleneckRefreshSourceTest(unittest.TestCase):
    def test_script_and_report_define_bottleneck_refresh_without_claims(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8") + "\n" + REPORT.read_text(encoding="utf-8")
        for fragment in (
            "Goal4074",
            "recommended_unblocked",
            "direct_side_effect",
            "blocked_32768",
            "no_same_root_culling",
            "native_elapsed_sec",
            "count_native_elapsed_sec",
            "benchmark_timing_breakdown",
            "same_component_size_signature_as_recommended",
            "does not authorize release",
            "true-zero-copy",
        ):
            self.assertIn(fragment, text)


class Goal4074RtDbscanGroupedStreamBottleneckRefreshArtifactTest(unittest.TestCase):
    def test_pod_artifact_keeps_claims_closed_and_variants_correct(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal4074 pod artifact has not been produced yet")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4074")
        self.assertEqual(payload["schema"], "rtdl.goal4074.rt_dbscan_grouped_stream_bottleneck_refresh.v1")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["paper_speedup_claim_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["native_abi_added"])
        variants = {row["variant"] for row in payload["rows"]}
        self.assertEqual(
            variants,
            {"recommended_unblocked", "direct_side_effect", "blocked_32768", "no_same_root_culling"},
        )
        for row in payload["rows"]:
            self.assertTrue(row["same_component_size_signature_as_recommended"])
            self.assertTrue(row["rt_core_accelerated"])
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["rt_core_speedup_claim_authorized"])
            self.assertFalse(row["whole_app_speedup_claim_authorized"])
            self.assertFalse(row["true_zero_copy_claim_authorized"])
            self.assertIn("elapsed_sec", row)
            self.assertIn("host_observed_sec", row)
            self.assertIn("derived_sec", row)


if __name__ == "__main__":
    unittest.main()
