import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1636_v1_6_x_optix_collect_k_next_direction_after_final_pair_negatives_2026-05-09.md"
CLAUDE = ROOT / "docs" / "reviews" / "claude_goal1636_collect_k_next_direction_review_2026-05-09.md"
GEMINI = ROOT / "docs" / "reviews" / "gemini_goal1636_collect_k_next_direction_review_2026-05-09.md"


class Goal1636OptixCollectKNextDirectionTest(unittest.TestCase):
    def test_external_reviews_support_pivot_away_from_blind_fusion(self) -> None:
        claude = CLAUDE.read_text(encoding="utf-8")
        gemini = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Direction is coherent", claude)
        self.assertIn("CUDA event bracket", claude)
        self.assertIn("synchronization trap", gemini)
        self.assertIn("CUDA Graphs", gemini)

    def test_report_selects_cuda_event_mark_timing_probe(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`cuda_event_mark_timing_probe_selected`", text)
        self.assertIn("final_pair_mark_gpu_event_ms", text)
        self.assertIn("final_pair_mark_stream_wait_ms", text)
        self.assertIn("Do not continue materialize+mark fusion", text)
        self.assertIn("Host prefix scan/upload is not the main bottleneck", text)

    def test_report_preserves_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("true zero-copy wording", text)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("release action", text)


if __name__ == "__main__":
    unittest.main()
