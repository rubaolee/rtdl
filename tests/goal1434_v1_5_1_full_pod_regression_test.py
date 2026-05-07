from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal1434V151FullPodRegressionTest(unittest.TestCase):
    def test_summary_records_clean_full_pod_discovery(self) -> None:
        summary = (
            ROOT / "docs/reports/goal1434_v1_5_1_full_pod_regression_2026-05-07.md"
        ).read_text(encoding="utf-8")

        self.assertIn("ACCEPTED for the measured full Linux GPU-pod source-tree regression package", summary)
        self.assertIn("bb3fbb317725c0602b7b4313d64162edad0db48c", summary)
        self.assertIn("NVIDIA RTX A5000", summary)
        self.assertIn("Ran 2818 tests", summary)
        self.assertIn("OK (skipped=221)", summary)
        self.assertIn("does not authorize stable `COLLECT_K_BOUNDED` promotion", summary)

    def test_full_discover_transcript_is_green(self) -> None:
        transcript = (
            ROOT / "docs/reports/goal1434_v1_5_1_full_pod_unittest_discover_2026-05-07.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("Ran 2818 tests", transcript)
        self.assertIn("OK (skipped=221)", transcript)
        self.assertNotIn("FAILED", transcript)

    def test_rebuild_logs_record_embree_and_optix_rebuilds(self) -> None:
        embree = (
            ROOT / "docs/reports/goal1434_v1_5_1_full_pod_rebuild_embree_2026-05-07.txt"
        ).read_text(encoding="utf-8")
        optix = (
            ROOT / "docs/reports/goal1434_v1_5_1_full_pod_rebuild_optix_2026-05-07.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("Embree", embree)
        self.assertIn("build/librtdl_optix.so", optix)
        self.assertIn("src/native/rtdl_optix.cpp", optix)

    def test_external_reviews_and_consensus_accept_narrow_scope(self) -> None:
        gemini = (
            ROOT / "docs/reports/gemini_goal1434_v1_5_1_full_pod_regression_review_2026-05-07.md"
        ).read_text(encoding="utf-8")
        claude = (
            ROOT / "docs/reports/claude_goal1434_v1_5_1_full_pod_regression_review_2026-05-07.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT / "docs/reports/three_ai_goal1434_v1_5_1_full_pod_regression_consensus_2026-05-07.md"
        ).read_text(encoding="utf-8")

        self.assertIn("ACCEPT", gemini)
        self.assertIn("ACCEPT", claude)
        self.assertIn("3-AI Consensus", consensus)
        self.assertIn("Ran 2818 tests", consensus)
        self.assertIn("Stable promotion and public claims remain blocked", consensus)


if __name__ == "__main__":
    unittest.main()
