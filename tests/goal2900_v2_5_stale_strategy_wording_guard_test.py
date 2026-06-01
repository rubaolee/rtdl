import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN_REPORT = ROOT / "docs" / "reports" / "v2_5_partner_choice_and_multi_partner_composition_design_2026-05-29.md"
REPORT = ROOT / "docs" / "reports" / "goal2900_v2_5_stale_strategy_wording_guard_after_raydb_perf_gate_2026-05-31.md"


class Goal2900V25StaleStrategyWordingGuardTest(unittest.TestCase):
    def test_partner_choice_report_has_post_goal2896_correction(self) -> None:
        text = DESIGN_REPORT.read_text(encoding="utf-8")

        self.assertIn("Post-Goal2896 correction", text)
        self.assertIn("RayDB is no longer evidence that Triton should be the chosen partner", text)
        self.assertIn("primitive-first", text)
        self.assertIn("unfused continuations", text)

    def test_stale_tier_a_triton_parity_phrase_is_removed(self) -> None:
        text = DESIGN_REPORT.read_text(encoding="utf-8")
        normalized = " ".join(text.split())

        self.assertNotIn("Triton-as-chosen-partner is demonstrated at parity", text)
        self.assertIn("not a blanket \"Triton chosen at parity\" bucket", text)
        self.assertIn("RayDB scalar grouped reductions are now explicitly primitive-first", normalized)

    def test_goal2900_report_records_narrow_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2900", text)
        self.assertIn("not a release authorization", text)
        self.assertIn("not a public performance claim", text)
        self.assertIn("does not rewrite older historical reports wholesale", text)


if __name__ == "__main__":
    unittest.main()
