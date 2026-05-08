from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1526_v1_5_4_collect_reduced_copy_cumulative_rerun_2026-05-08.md"


class Goal1526V154CollectReducedCopyCumulativeRerunTest(unittest.TestCase):
    def test_report_records_green_windows_and_linux_cumulative_slice(self) -> None:
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Ran 199 tests", text)
        self.assertIn("Host: `192.168.1.20`", text)
        self.assertIn("v1.5.1 through v1.5.4", text)
        self.assertIn("typed-host zero-capacity guard", text)

    def test_report_keeps_non_pod_claim_boundary_closed(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())
        self.assertIn("targeted local/non-pod regression checkpoint only", text)
        self.assertIn("does not prove new NVIDIA pod performance", text)
        self.assertIn("true zero-copy", text)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("release readiness", text)


if __name__ == "__main__":
    unittest.main()
