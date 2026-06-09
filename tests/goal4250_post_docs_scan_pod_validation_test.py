import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4250_post_docs_scan_pod_validation_2026-06-09.md"


class Goal4250PostDocsScanPodValidationTest(unittest.TestCase):
    def test_report_records_current_head_and_gpu(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Source commit | `14dbb8e0`", text)
        self.assertIn("NVIDIA RTX 4000 Ada Generation", text)
        self.assertIn("driver 550.127.08", text)

    def test_report_records_release_prep_validation_slice(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("tests.goal4219_major_performance_target_map_test", text)
        self.assertIn("tests.goal4248_current_public_docs_claim_boundary_scan_test", text)
        self.assertIn("tests.goal4235_current_head_rehearsal_after_measurement_closure_test", text)
        self.assertIn("tests.goal4239_rayjoin_dedicated_long_repeat_profile_test", text)
        self.assertIn("tests.goal4243_short_row_long_repeat_refresh_test", text)
        self.assertIn("Ran 22 tests", text)
        self.assertIn("OK", text)

    def test_report_keeps_claim_boundaries_closed(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "does not authorize release",
            "public speedup wording",
            "broad RT-core wording",
            "paper reproduction",
            "true zero-copy wording",
            "automatic partner selection",
            "AMD performance",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
