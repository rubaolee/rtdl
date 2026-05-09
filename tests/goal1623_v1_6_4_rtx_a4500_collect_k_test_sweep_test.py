from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal1623_v1_6_4_rtx_a4500_collect_k_test_sweep_2026-05-09.md"
TRANSCRIPT = ROOT / "docs/reports/goal1623_v1_6_4_rtx_a4500_collect_k_test_sweep_2026-05-09.txt"


class Goal1623RtxA4500CollectKTestSweepTest(unittest.TestCase):
    def test_transcript_records_green_rtx_collect_k_sweep(self) -> None:
        text = TRANSCRIPT.read_text(encoding="utf-8")

        self.assertIn("commit f4e28bf259021e431150172ed494ab7e3592057c", text)
        self.assertIn("nvidia NVIDIA RTX A4500, 550.127.05, 20470 MiB", text)
        self.assertIn("collect_k_test_module_count 100", text)
        self.assertIn("Ran 390 tests", text)
        self.assertIn("\nOK\n", text)
        self.assertIn("end_unittest_returncode 0", text)

    def test_report_records_scope_and_blocks_overclaiming(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("ACCEPTED as latest-main RTX A4500 collect-k test-sweep evidence", text)
        self.assertIn("100", text)
        self.assertIn("390", text)
        self.assertIn("not public speedup evidence", text)
        self.assertIn("not true zero-copy evidence", text)
        self.assertIn("not stable\n`COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("Stable promotion remains blocked", text)

    def test_external_reviews_and_consensus_accept_sweep_only(self) -> None:
        review_paths = (
            ROOT / "docs/reviews/goal1623_v1_6_4_rtx_a4500_collect_k_test_sweep_claude_review_2026-05-09.md",
            ROOT / "docs/reviews/goal1623_v1_6_4_rtx_a4500_collect_k_test_sweep_gemini_review_2026-05-09.md",
            ROOT / "docs/reviews/goal1623_v1_6_4_rtx_a4500_collect_k_test_sweep_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPT", text.upper())
                self.assertIn("COLLECT_K_BOUNDED", text)

        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("not a stable-promotion consensus", consensus)
        self.assertIn("Stable promotion still requires a separate", consensus)


if __name__ == "__main__":
    unittest.main()
