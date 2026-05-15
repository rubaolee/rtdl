import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2043_v2_0_clean_powerful_traceable_plan_2026-05-14.md"


class Goal2043PlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = REPORT.read_text(encoding="utf-8")

    def test_names_required_unsolved_rich_contracts(self):
        required = [
            "exact K=3 facility fallback ranking",
            "exact ANN ranking",
            "exact Hausdorff distance with witness extraction",
            "broad general polygon overlay",
        ]
        for phrase in required:
            self.assertIn(phrase, self.text)

    def test_keeps_engine_app_agnostic_and_partner_owned(self):
        required = [
            "native engine should emit generic",
            "It should not know app names",
            "The partner layer should own continuation policies",
            "CuPy RawKernel is allowed as a partner capability",
        ]
        for phrase in required:
            self.assertIn(phrase, self.text)

    def test_defines_traceability_and_release_boundaries(self):
        required = [
            "Every performance row must include",
            "pod evidence is required for release performance claims",
            "local GTX 1070 evidence is smoke only",
            "This plan does not authorize v2.0 release",
        ]
        for phrase in required:
            self.assertIn(phrase, self.text)

    def test_recommends_next_goal_with_generic_primitives(self):
        required = [
            "Goal2044 should implement Phase A",
            "NumPy reference operators",
            "segmented reductions",
            "group top-K",
            "witness-carrying reductions",
        ]
        for phrase in required:
            self.assertIn(phrase, self.text)


if __name__ == "__main__":
    unittest.main()
