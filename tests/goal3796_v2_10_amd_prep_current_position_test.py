from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3796_v2_10_amd_prep_current_position_2026-06-07.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal3793_gemini_review_goal3783_3792_v2_10_hiprt_amd_prep_2026-06-07.md"


class Goal3796V210AmdPrepCurrentPositionTest(unittest.TestCase):
    def test_report_states_current_position_and_amd_command(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "10 promoted benchmark apps",
            "0 apps remain blocked on missing Numba reference coverage",
            "Goal3785 AMD runner rejects non-AMD hardware",
            "34 modules, 185 tests",
            "commit `a7a10228`",
            "python3 scripts/goal3785_amd_hiprt_functional_pod_runner.py",
            "goal3784_amd_hiprt_functional_pod_validation.json",
        ):
            self.assertIn(phrase, text)

    def test_report_keeps_a5000_and_amd_boundaries_separate(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("The current NVIDIA A5000 pod can continue to provide", text)
        self.assertIn("It cannot provide:", text)
        for phrase in (
            "AMD functional evidence",
            "AMD performance evidence",
            "AMD release authorization",
            "broad cross-vendor RT-core claims",
            "does not authorize release action",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)

    def test_report_records_review_state_without_claiming_claude_done(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        self.assertIn("Gemini has reviewed Goals3783-3792 with verdict `accept`", text)
        self.assertIn("Claude review remains intentionally deferred", text)
        self.assertIn("**Verdict:** accept", gemini)


if __name__ == "__main__":
    unittest.main()
