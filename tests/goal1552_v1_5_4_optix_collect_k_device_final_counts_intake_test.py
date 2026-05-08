from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1552_v1_5_4_optix_collect_k_device_final_counts_intake_2026-05-08.md"
CANDIDATE_JSON = ROOT / "docs" / "reports" / "goal1552_v1_5_4_optix_collect_k_device_final_counts_candidate_probe_2026-05-08.json"
CONTROL_JSON = ROOT / "docs" / "reports" / "goal1552_v1_5_4_optix_collect_k_device_final_counts_control_probe_2026-05-08.json"


class Goal1552V154OptixCollectKDeviceFinalCountsIntakeTest(unittest.TestCase):
    def test_candidate_preserves_parity_and_reduces_final_metadata(self) -> None:
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
        for count in (4097, 65537, 131072):
            with self.subTest(candidate_count=count):
                case = candidate[count]
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertTrue(case["profile_topology_matches_expected"])
                self.assertLess(
                    case["stage_profile"]["topology"]["metadata_fields_downloaded"],
                    control[count]["stage_profile"]["topology"]["metadata_fields_downloaded"],
                )
                self.assertLess(
                    case["stage_profile"]["stage_median_ms"]["total_ms"],
                    control[count]["stage_profile"]["stage_median_ms"]["total_ms"],
                )

        self.assertEqual(candidate[131072]["stage_profile"]["topology"]["metadata_fields_downloaded"], 65)

    def test_report_bounds_claim_and_names_env_gate(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1", text)
        self.assertIn("reduced metadata transfer, not true zero-copy", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("0.312833", text)
        self.assertIn("0.306882", text)


if __name__ == "__main__":
    unittest.main()
