from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal1433V151OptixRegressionPodTest(unittest.TestCase):
    def test_summary_records_clean_optix_pod_rerun(self) -> None:
        summary = (
            ROOT / "docs/reports/goal1433_v1_5_1_optix_regression_pod_2026-05-07.md"
        ).read_text(encoding="utf-8")

        self.assertIn("ACCEPTED for the measured RTX A5000 OptiX regression package", summary)
        self.assertIn("93f4259b74cb7570497827e4b36789fd554ed7ed", summary)
        self.assertIn("NVIDIA RTX A5000", summary)
        self.assertIn("Ran 47 tests", summary)
        self.assertIn("Ran 309 tests", summary)
        self.assertIn("does not authorize stable `COLLECT_K_BOUNDED` promotion", summary)
        self.assertIn("release action", summary)

    def test_focused_and_broad_transcripts_are_green(self) -> None:
        focused = (
            ROOT / "docs/reports/goal1433_v1_5_1_optix_regression_focused_slice_2026-05-07.txt"
        ).read_text(encoding="utf-8")
        broad = (
            ROOT / "docs/reports/goal1433_v1_5_1_optix_regression_broad_discover_2026-05-07.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("Ran 47 tests", focused)
        self.assertIn("OK", focused)
        self.assertIn("Ran 309 tests", broad)
        self.assertIn("OK", broad)
        self.assertNotIn("FAILED", focused)
        self.assertNotIn("FAILED", broad)

    def test_build_log_records_optix_library_rebuild(self) -> None:
        build = (
            ROOT / "docs/reports/goal1433_v1_5_1_optix_regression_build_optix_2026-05-07.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("build/librtdl_optix.so", build)
        self.assertIn("src/native/rtdl_optix.cpp", build)

    def test_gemini_review_and_consensus_accept_narrow_regression_scope(self) -> None:
        gemini = (
            ROOT / "docs/reports/gemini_goal1433_v1_5_1_optix_regression_pod_review_2026-05-07.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT / "docs/reports/two_ai_goal1433_v1_5_1_optix_regression_pod_consensus_2026-05-07.md"
        ).read_text(encoding="utf-8")

        self.assertIn("ACCEPT", gemini)
        self.assertIn("2-AI Consensus", consensus)
        self.assertIn("Ran 309 tests", consensus)
        self.assertIn("Stable promotion and public claims remain blocked", consensus)


if __name__ == "__main__":
    unittest.main()
