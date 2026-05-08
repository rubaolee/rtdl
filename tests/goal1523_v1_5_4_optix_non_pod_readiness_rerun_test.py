from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1523_v1_5_4_optix_non_pod_readiness_rerun_2026-05-08.md"


class Goal1523V154OptixNonPodReadinessRerunTest(unittest.TestCase):
    def test_report_records_green_windows_and_linux_reruns(self):
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Ran 35 tests", text)
        self.assertIn("Host: `192.168.1.20`", text)
        self.assertIn("Goal1508 tiled preflight guard", text)

    def test_report_blocks_performance_and_release_claims(self):
        text = " ".join(REPORT.read_text(encoding="utf-8").split())
        self.assertIn("does not prove accepted NVIDIA performance", text)
        self.assertIn("does not authorize public", text)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("or release action", text)


if __name__ == "__main__":
    unittest.main()
