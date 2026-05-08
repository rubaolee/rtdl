from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1522_v1_5_4_targeted_cross_platform_regression_2026-05-08.md"


class Goal1522V154TargetedCrossPlatformRegressionTest(unittest.TestCase):
    def test_report_records_windows_and_linux_green_slices(self):
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Ran 26 tests", text)
        self.assertIn("Ran 36 tests", text)
        self.assertIn("Host: `192.168.1.20`", text)

    def test_report_does_not_claim_full_discovery_success(self):
        text = " ".join(REPORT.read_text(encoding="utf-8").split())
        self.assertIn("does not claim full-suite discovery success", text)
        self.assertIn("Timed out after 604033 ms", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", text)


if __name__ == "__main__":
    unittest.main()
