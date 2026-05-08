import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "docs" / "reports" / "goal1503_v1_5_4_optix_collect_k_scaling_probe_2026-05-08.json"
BLACKWELL_REPORT_JSON = (
    ROOT / "docs" / "reports" / "goal1503_v1_5_4_optix_collect_k_scaling_probe_blackwell_2026-05-08.json"
)


class Goal1503V154OptixCollectKScalingEvidenceTest(unittest.TestCase):
    def load_report(self) -> dict:
        return json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    def test_final_scaling_report_is_parity_clean_and_claim_conservative(self) -> None:
        report = self.load_report()

        self.assertEqual(report["goal"], "Goal1503")
        self.assertEqual(report["status"], "goal1503_optix_collect_k_scaling_probe_recorded")
        self.assertTrue(report["measured_on_real_nvidia"])
        self.assertTrue(report["all_parity_passed"])
        self.assertIn("NVIDIA", report["device_name"])
        self.assertIn("COLLECT_K_BOUNDED", report["claim_boundary"])
        self.assertIn("not a speedup claim", report["claim_boundary"])
        for flag, value in report["claim_flags"].items():
            with self.subTest(flag=flag):
                self.assertFalse(value)

    def test_final_scaling_report_covers_bounded_128k_row_width2_scope(self) -> None:
        report = self.load_report()
        cases = {case["candidate_count"]: case for case in report["cases"]}

        required_counts = {
            4096,
            4097,
            32768,
            32769,
            65536,
            65537,
            131072,
        }
        self.assertTrue(required_counts.issubset(cases))
        for count in required_counts:
            with self.subTest(count=count):
                case = cases[count]
                self.assertEqual(case["row_width"], 2)
                self.assertEqual(case["repeats"], 9)
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertGreater(case["median_ms"], 0.0)
                transfer = case["transfer_accounting"]
                self.assertEqual(transfer["host_to_device_transfers_before_backend_execution"], 0)
                self.assertTrue(transfer["allocation_only_transfers_distinguished_from_content_transfers"])

        for count in (4097, 32769, 65537, 131072):
            with self.subTest(tiled_count=count):
                self.assertEqual(cases[count]["expected_native_path"], "row_width2_bounded_multi_tile_sort_merge")

    def test_final_scaling_report_does_not_look_like_fallback_cliff(self) -> None:
        report = self.load_report()
        cases = {case["candidate_count"]: case for case in report["cases"]}

        # This is an internal evidence-shape guard, not public speedup wording.
        # The former fallback cliffs were measured in seconds; the final bounded
        # tiled artifact should stay far below that shape for these sizes.
        self.assertLess(cases[65537]["median_ms"], 1000.0)
        self.assertLess(cases[131072]["median_ms"], 1000.0)

    def test_blackwell_scaling_subset_is_parity_clean_and_claim_conservative(self) -> None:
        report = json.loads(BLACKWELL_REPORT_JSON.read_text(encoding="utf-8"))

        self.assertEqual(report["goal"], "Goal1503")
        self.assertTrue(report["measured_on_real_nvidia"])
        self.assertTrue(report["all_parity_passed"])
        self.assertIn("Blackwell", report["device_name"])
        for flag, value in report["claim_flags"].items():
            with self.subTest(flag=flag):
                self.assertFalse(value)

        cases = {case["candidate_count"]: case for case in report["cases"]}
        self.assertEqual(set(cases), {4097, 65537, 131072})
        for count in (4097, 65537, 131072):
            with self.subTest(count=count):
                case = cases[count]
                self.assertEqual(case["expected_native_path"], "row_width2_bounded_multi_tile_sort_merge")
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertLess(case["median_ms"], 1000.0)


if __name__ == "__main__":
    unittest.main()
