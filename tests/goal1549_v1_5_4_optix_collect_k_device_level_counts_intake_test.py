from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1549_v1_5_4_optix_collect_k_device_level_counts_intake_2026-05-08.md"
CANDIDATE_JSON = ROOT / "docs" / "reports" / "goal1549_v1_5_4_optix_collect_k_device_level_counts_candidate_probe_2026-05-08.json"
CONTROL_JSON = ROOT / "docs" / "reports" / "goal1549_v1_5_4_optix_collect_k_device_level_counts_control_probe_2026-05-08.json"


class Goal1549V154OptixCollectKDeviceLevelCountsIntakeTest(unittest.TestCase):
    def test_candidate_keeps_parity_and_reduces_long_case_transfers(self) -> None:
        control = {
            case["candidate_count"]: case
            for case in json.loads(CONTROL_JSON.read_text(encoding="utf-8"))["cases"]
        }
        candidate_data = json.loads(CANDIDATE_JSON.read_text(encoding="utf-8"))
        candidate = {
            case["candidate_count"]: case
            for case in candidate_data["cases"]
        }

        self.assertIs(candidate_data["accepted_goal1506_evidence"], True)
        self.assertEqual(candidate_data["device_name"], "NVIDIA RTX 4000 Ada Generation")
        for count in (4097, 65537, 131072):
            with self.subTest(candidate_count=count):
                case = candidate[count]
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertTrue(case["profile_topology_matches_expected"])
                self.assertLess(
                    case["stage_profile"]["stage_median_ms"]["total_ms"],
                    control[count]["stage_profile"]["stage_median_ms"]["total_ms"],
                )

        self.assertEqual(
            candidate[131072]["transfer_accounting"]["host_to_device_transfers_before_backend_execution"],
            1,
        )
        self.assertLess(
            candidate[131072]["transfer_accounting"]["device_to_host_transfers_after_backend_execution"],
            control[131072]["transfer_accounting"]["device_to_host_transfers_after_backend_execution"],
        )

    def test_report_bounds_claim_and_names_env_gate(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1", text)
        self.assertIn("downloads the final two segment counts", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("0.406921", text)
        self.assertIn("0.320287", text)


if __name__ == "__main__":
    unittest.main()
