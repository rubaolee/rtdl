from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1921_v2_post_pod_performance_report_2026-05-13.md"


class Goal1921V2PostPodPerformanceReportTest(unittest.TestCase):
    def test_report_summarizes_exact_positive_and_mixed_rows(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("NVIDIA RTX 2000 Ada Generation", text)
        self.assertIn("Goal1905 post-pod acceptance: `pass`", text)
        self.assertIn("Goal1916 post-pod manifest: `pass`", text)
        self.assertIn("Fixed-radius is the strongest current v2 result", text)
        self.assertIn("0.027x", text)
        self.assertIn("0.002x", text)
        self.assertIn("At 512 rows", text)
        self.assertIn("not meaningfully faster", text)
        self.assertIn("At 2048 rows", text)
        self.assertIn("0.365x", text)
        self.assertIn("0.247x", text)

    def test_report_preserves_claim_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Unsupported Claims", text)
        self.assertIn("v2.0 release readiness", text)
        self.assertIn("Package-install support", text)
        self.assertIn("Whole-application speedup", text)
        self.assertIn("Broad RT-core speedup", text)
        self.assertIn("Fixed-radius true-zero-copy support", text)
        self.assertIn("not a release authorization", text)


if __name__ == "__main__":
    unittest.main()
