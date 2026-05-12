import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1732_v1_6_11_final_release_decision_note_2026-05-12.md"


class Goal1732V1611FinalReleaseDecisionNoteTest(unittest.TestCase):
    def test_note_is_ready_for_user_decision_not_release_action(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("ready_for_explicit_user_release_decision", text)
        self.assertIn("No release action has been performed", text)
        self.assertIn("requires explicit user authorization", text)

    def test_conservative_release_option_blocks_speedup_wording(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("No public speedup wording is authorized", text)
        self.assertIn("No broad RTX/GPU acceleration wording is authorized", text)
        self.assertIn("No whole-app speedup wording is authorized", text)
        self.assertIn("No Python+partner+RTDL v2.0 claim is authorized", text)

    def test_decision_note_names_comparison_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal1660 comparable artifact evidence is limited to 16 real v1.0/current pairs", text)
        self.assertIn("Unsupported v1.0 Embree rows are excluded/current-only", text)
        self.assertIn("not failed/slower/faster baselines", text)

    def test_recommendation_names_only_procedural_blocker(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("no known remaining evidence blocker", text)
        self.assertIn("The only remaining blocker is procedural", text)


if __name__ == "__main__":
    unittest.main()
