import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2518_partner_resident_fused_sum_count_timing_2026-05-23.md"
POD_SCRIPT = ROOT / "scripts/goal2518_partner_resident_fused_sum_count_timing_pod.py"
POD_ARTIFACT = ROOT / "docs/reports/goal2518_partner_resident_fused_sum_count_timing_pod_2026-05-23.json"


class Goal2518PartnerResidentFusedSumCountTimingTest(unittest.TestCase):
    def test_runner_compares_two_launch_and_fused_paths(self) -> None:
        source = POD_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("run_optix_partner_resident_columnar_grouped_sum_count_i64", source)
        self.assertIn("run_optix_partner_resident_columnar_grouped_sum_i64", source)
        self.assertIn("run_optix_partner_resident_columnar_grouped_count_i64", source)
        self.assertIn("two_launch_native_launch_count", source)
        self.assertIn("fused_native_launch_count", source)
        self.assertIn("public_speedup_claim_authorized", source)

    def test_report_records_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2518", text)
        self.assertIn("two native launches", text)
        self.assertIn("one generic fused", text)
        self.assertIn("No public speedup claim", text)
        self.assertIn("No true zero-copy claim", text)

    def test_pod_artifact_records_internal_timing_evidence(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertIs(payload["cuda_available"], True)
        self.assertIs(payload["rows_match_two_launch_reference"], True)
        self.assertEqual(payload["two_launch_native_launch_count"], 2)
        self.assertEqual(payload["fused_native_launch_count"], 1)
        self.assertGreater(payload["row_count"], 0)
        self.assertGreater(payload["result_group_count"], 0)
        self.assertGreater(payload["two_launch_timings_sec"]["mean"], 0.0)
        self.assertGreater(payload["fused_timings_sec"]["mean"], 0.0)
        self.assertGreater(payload["internal_fused_speedup_ratio_mean"], 0.0)
        self.assertIs(payload["public_speedup_claim_authorized"], False)
        self.assertIs(payload["true_zero_copy_claim_authorized"], False)
        self.assertIs(payload["native_avg_abi_added"], False)


if __name__ == "__main__":
    unittest.main()
