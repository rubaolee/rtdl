from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2194_rayjoin_same_query_adapter_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2193_gemini_review_goal2192_rayjoin_same_query_adapter_2026-05-17.md"


class Goal2194RayjoinSameQueryAdapter2AiConsensusTest(unittest.TestCase):
    def test_consensus_records_two_ai_accept_with_boundary(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("2-AI consensus complete", text)
        self.assertIn("Codex", text)
        self.assertIn("Gemini", text)
        self.assertEqual(text.count("`accept-with-boundary`"), 2)

    def test_consensus_preserves_demo_stream_boundary(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("rtdl_demo_generator_not_rayjoin_cpp", text)
        self.assertIn("same_contract_with_rayjoin_query_exec: false", text)
        self.assertIn("does not authorize", text)
        self.assertIn("treating demo-generated streams as RayJoin `query_exec` streams", text)

    def test_gemini_review_exists_and_matches_scope(self) -> None:
        review = GEMINI.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", review)
        self.assertIn("rtdl.rayjoin.same_query_stream.v1", review)
        self.assertIn("not be treated as RayJoin paper reproduction", review)


if __name__ == "__main__":
    unittest.main()
