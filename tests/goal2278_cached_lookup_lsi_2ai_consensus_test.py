from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2278_cached_lookup_lsi_2ai_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2277_gemini_review_goal2275_2276_cached_lookup_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2276_cached_lookup_rayjoin_lsi_probe_pod_2026-05-17.json"
REPORT = ROOT / "docs" / "reports" / "goal2276_cached_lookup_rayjoin_lsi_probe_2026-05-17.md"


class Goal2278CachedLookupLsi2AiConsensusTest(unittest.TestCase):
    def test_consensus_references_review_and_artifact(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn(str(GEMINI.relative_to(ROOT)).replace("\\", "/"), text)
        self.assertIn("Codex + Gemini consensus", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("5c41ade112fb7ebbcdd6ed593eea96eb806db75f", text)

    def test_gemini_review_accepts(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Verdict:** accept", text)
        self.assertIn("generic", text)
        self.assertIn("avoid overclaiming", text)

    def test_artifact_and_report_remain_present(self) -> None:
        self.assertTrue(ARTIFACT.exists())
        self.assertTrue(REPORT.exists())

    def test_consensus_keeps_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Still not allowed", text)
        self.assertIn("whole RayJoin application speedup", text)
        self.assertIn("true zero-copy", text)
        self.assertIn("not app-specific engine customization", text)


if __name__ == "__main__":
    unittest.main()
