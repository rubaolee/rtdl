from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1521_v1_5_4_collect_reduced_copy_local_regression_2026-05-08.md"


class Goal1521V154CollectReducedCopyLocalRegressionTest(unittest.TestCase):
    def test_report_records_green_regression_slice(self):
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Ran 62 tests", text)
        self.assertIn("OK", text)
        self.assertIn("Goal1520 emitted-count guard", text)

    def test_report_keeps_claim_boundary_narrow(self):
        text = " ".join(REPORT.read_text(encoding="utf-8").split())
        self.assertIn("does not authorize stable `COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("does not prove true zero-copy", text)
        self.assertIn("does not change release status", text)


if __name__ == "__main__":
    unittest.main()
