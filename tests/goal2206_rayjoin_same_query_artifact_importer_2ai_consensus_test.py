from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2206_rayjoin_same_query_artifact_importer_2ai_consensus_2026-05-17.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2205_gemini_review_goal2204_rayjoin_artifact_importer_2026-05-17.md"
SCRIPT = ROOT / "scripts" / "goal2204_rayjoin_same_query_artifact_import.py"


class Goal2206RayJoinSameQueryArtifactImporterConsensusTest(unittest.TestCase):
    def test_consensus_references_gemini_review_and_boundary(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Codex and Gemini agree", text)
        self.assertIn(str(REVIEW.relative_to(ROOT)).replace("\\", "/"), text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("tooling only", text)
        self.assertIn("does not authorize", text)
        self.assertIn("v2.0 release readiness", text)

    def test_consensus_records_stream_policy(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("hashes full RayJoin query streams", text)
        self.assertIn("--include-streams", text)
        self.assertIn("include_streams", script)
        self.assertIn("sha256", script)

    def test_gemini_review_exists(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Goal2205 Gemini Review", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("No concrete code fixes", text)


if __name__ == "__main__":
    unittest.main()
