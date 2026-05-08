from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1548_v1_5_4_optix_collect_k_derived_descriptors_intake_2026-05-08.md"
CANDIDATE_JSON = ROOT / "docs" / "reports" / "goal1548_v1_5_4_optix_collect_k_derived_descriptors_candidate_probe_2026-05-08.json"
CONTROL_JSON = ROOT / "docs" / "reports" / "goal1548_v1_5_4_optix_collect_k_derived_descriptors_control_probe_2026-05-08.json"


class Goal1548V154OptixCollectKDerivedDescriptorsIntakeTest(unittest.TestCase):
    def test_candidate_probe_preserves_parity_and_reduces_h2d_transfers(self) -> None:
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
                    case["transfer_accounting"]["host_to_device_transfers_before_backend_execution"],
                    control[count]["transfer_accounting"]["host_to_device_transfers_before_backend_execution"],
                )
                self.assertLess(
                    case["stage_profile"]["stage_median_ms"]["total_ms"],
                    control[count]["stage_profile"]["stage_median_ms"]["total_ms"],
                )

    def test_report_bounds_claim_and_names_env_gate(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1", text)
        self.assertIn("reduced descriptor upload, not true zero-copy", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("0.479449", text)
        self.assertIn("0.409456", text)


if __name__ == "__main__":
    unittest.main()
