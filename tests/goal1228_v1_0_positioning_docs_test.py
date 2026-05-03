from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_DOCS = (
    "README.md",
    "docs/README.md",
    "docs/application_catalog.md",
    "docs/rtdl_feature_guide.md",
    "docs/release_facing_examples.md",
    "docs/app_engine_support_matrix.md",
)


class Goal1228V10PositioningDocsTest(unittest.TestCase):
    def test_public_docs_do_not_reintroduce_stale_goal1208_counts(self) -> None:
        stale_phrases = (
            "11 reviewed RTX app rows",
            "11 reviewed sub-path rows",
            "Current reviewed public wording rows after Goal1208",
            "road-hazard detection as the only newly promoted",
            "bounded public RTX sub-path wording after Goal1146 and Goal1208",
        )
        for relative in PUBLIC_DOCS:
            text = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(relative=relative):
                for phrase in stale_phrases:
                    self.assertNotIn(phrase, text)

    def test_v1_0_positioning_is_explicit_on_front_page(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## v1.0 Direction", readme)
        self.assertIn("v1.0 proof machinery, not the final architecture", readme)
        self.assertIn("v1.5 is planned to replace", readme)
        self.assertIn("app-specific engine customization", readme)
        self.assertIn("v2.0 targets broader end-to-end performance", readme)
        self.assertIn("12 reviewed", readme)

    def test_goal1228_plan_records_custom_engine_inventory(self) -> None:
        plan = (
            ROOT
            / "docs/reports/goal1228_v1_0_positioning_and_engine_customization_plan_2026-05-03.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engine Customization Inventory", plan)
        self.assertIn("v1.0 implementation uses app-driven native customization", plan)
        self.assertIn("v1.5 removes app-specific engine customization", plan)
        self.assertIn("v2.0 targets broader end-to-end performance", plan)


if __name__ == "__main__":
    unittest.main()
