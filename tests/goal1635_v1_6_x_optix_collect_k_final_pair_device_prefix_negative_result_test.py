import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1635_v1_6_x_optix_collect_k_final_pair_device_prefix_negative_result_2026-05-09.md"
CONTROL = ROOT / "docs" / "reports" / "goal1635_final_pair_device_prefix_control_262144_repeats5.json"
CANDIDATE = ROOT / "docs" / "reports" / "goal1635_final_pair_device_prefix_candidate_262144_repeats5.json"


class Goal1635OptixCollectKFinalPairDevicePrefixNegativeResultTest(unittest.TestCase):
    def test_candidate_preserves_parity_but_is_slower_than_control(self) -> None:
        control = json.loads(CONTROL.read_text(encoding="utf-8"))["cases"][0]
        candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))["cases"][0]
        control_stage = control["stage_profile"]["stage_median_ms"]
        candidate_stage = candidate["stage_profile"]["stage_median_ms"]

        self.assertTrue(control["same_candidate_rows"])
        self.assertTrue(candidate["same_candidate_rows"])
        self.assertTrue(control["same_valid_count"])
        self.assertTrue(candidate["same_valid_count"])
        self.assertLess(control_stage["total_ms"], candidate_stage["total_ms"])
        self.assertGreater(candidate_stage["final_pair_final_sync_ms"], 0.3)
        self.assertEqual(candidate_stage["final_pair_prefix_host_ms"], 0.0)
        self.assertGreater(candidate_stage["final_pair_prefix_device_ms"], 0.0)

    def test_rejected_runtime_flag_is_not_retained(self) -> None:
        text = API.read_text(encoding="utf-8")

        self.assertNotIn("RTDL_OPTIX_COLLECT_K_FINAL_PAIR_DEVICE_PREFIX_DIAGNOSTIC", text)
        self.assertNotIn("collect_k_use_final_pair_device_prefix_diagnostic", text)
        self.assertNotIn("final_pair_prefix_device_ms", text)
        self.assertNotIn("final_pair_final_sync_ms", text)

    def test_report_records_rejection_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`final_pair_device_prefix_rejected`", text)
        self.assertIn("prototype runtime flag is intentionally not retained", text)
        self.assertIn("host-side block-prefix scan/upload is not the main bottleneck", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("release action", text)


if __name__ == "__main__":
    unittest.main()
