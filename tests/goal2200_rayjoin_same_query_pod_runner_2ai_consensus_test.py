from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2200_rayjoin_same_query_pod_runner_2ai_consensus_2026-05-17.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2199_gemini_review_goal2198_rayjoin_same_query_pod_runner_2026-05-17.md"
SCRIPT = ROOT / "scripts" / "goal2198_rayjoin_same_query_pod_runner.sh"


class Goal2200RayJoinSameQueryPodRunnerConsensusTest(unittest.TestCase):
    def test_consensus_references_distinct_review_and_boundary(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Codex and Gemini agree", text)
        self.assertIn(str(REVIEW.relative_to(ROOT)).replace("\\", "/"), text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("not RayJoin performance evidence yet", text)
        self.assertIn("does not authorize", text)
        self.assertIn("RTDL-beats-RayJoin", text)
        self.assertIn("v2.0 release", text)

    def test_consensus_records_cuda_cupy_review_fix(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("cupy-cuda12x", text)
        self.assertIn("detect_cuda_major", text)
        self.assertIn("require_cuda12_for_cupy_package", text)
        self.assertIn("ALLOW_NON_CUDA12=0", text)
        self.assertIn("detect_cuda_major", script)
        self.assertIn("require_cuda12_for_cupy_package", script)

    def test_gemini_review_exists_with_expected_verdict(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Reviewer:** Gemini", text)
        self.assertIn("Verdict:** accept-with-boundary", text)
        self.assertIn("RayJoin query-stream export", text)


if __name__ == "__main__":
    unittest.main()
