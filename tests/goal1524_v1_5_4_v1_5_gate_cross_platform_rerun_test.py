from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1524_v1_5_4_v1_5_gate_cross_platform_rerun_2026-05-08.md"


class Goal1524V154V15GateCrossPlatformRerunTest(unittest.TestCase):
    def test_report_records_green_windows_and_linux_v1_5_gate_batch(self):
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Ran 138 tests", text)
        self.assertIn("Host: `192.168.1.20`", text)
        self.assertIn("Goal1274 through Goal1408", text)

    def test_report_keeps_claim_boundary_narrow(self):
        text = " ".join(REPORT.read_text(encoding="utf-8").split())
        self.assertIn("does not prove new OptiX pod performance", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("does not promote `COLLECT_K_BOUNDED`", text)
        self.assertIn("does not authorize release action", text)


if __name__ == "__main__":
    unittest.main()
