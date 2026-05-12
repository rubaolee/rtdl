import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1735_v1_6_11_final_release_consensus_2026-05-12.md"


class Goal1735V1611FinalReleaseConsensusTest(unittest.TestCase):
    def test_consensus_names_codex_claude_and_gemini_inputs(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Codex", text)
        self.assertIn("Claude", text)
        self.assertIn("Gemini", text)
        for goal in ("goal1729", "goal1730", "goal1731", "goal1732", "goal1733", "goal1734"):
            self.assertIn(goal, text)

    def test_consensus_accepts_only_conservative_python_rtdl_release_decision(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("accept-with-boundary", text)
        self.assertIn("conservative Python+RTDL-only release decision", text)
        self.assertIn("No public speedup wording is authorized", text)
        self.assertIn("No broad RTX/GPU acceleration wording is authorized", text)
        self.assertIn("No whole-app speedup wording is authorized", text)
        self.assertIn("No Python+partner+RTDL v2.0 claim is authorized", text)

    def test_consensus_keeps_release_action_procedural(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("only remaining blocker", text)
        self.assertIn("procedural", text)
        self.assertIn("user must explicitly authorize", text)
        self.assertIn("not a release action", text)


if __name__ == "__main__":
    unittest.main()
