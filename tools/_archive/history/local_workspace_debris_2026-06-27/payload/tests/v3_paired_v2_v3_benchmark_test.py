import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "v2_14_vs_v3_same_rt_hardware_paired_20260620_140120"
SUMMARY = ARTIFACT / "paired_v2_v3_summary.json"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md"


class V3PairedV2V3BenchmarkTest(unittest.TestCase):
    def payload(self):
        return json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_artifact_records_mixed_timing_and_v3_runability_win(self):
        payload = self.payload()
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(payload["same_metric_comparison_count"], 46)
        self.assertEqual(payload["v3_faster_count_gt_5pct"], 10)
        self.assertEqual(payload["similar_count_within_5pct"], 32)
        self.assertEqual(payload["v3_slower_count_gt_5pct"], 4)
        self.assertAlmostEqual(payload["v3_geomean_speedup_vs_v2"], 1.012314056248152)

        status = payload["suite_status"]
        self.assertEqual(status["v2_14_goal2626_standard"], {"rows": 22, "ok": 20, "failed": 2})
        self.assertEqual(status["v3_current_goal2626_standard"], {"rows": 22, "ok": 22, "failed": 0})
        self.assertEqual(status["v2_14_goal2636_standard"], {"rows": 28, "ok": 26, "failed": 2})
        self.assertEqual(status["v3_current_goal2636_standard"], {"rows": 28, "ok": 28, "failed": 0})
        self.assertFalse(status["v2_14_goal3828_full"]["all_pass"])
        self.assertTrue(status["v3_current_goal3828_full"]["all_pass"])

    def test_report_keeps_claim_boundary_visible(self):
        text = REPORT.read_text(encoding="utf-8")
        for needle in [
            "V3 is clearly stronger on runability",
            "not proven broadly faster than V2.14",
            "Geomean V3 speedup vs V2.14: 1.012x",
            "broad_v3_faster_than_v2_claim_authorized: false",
            "Barnes-Hut OptiX 32768",
        ]:
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
