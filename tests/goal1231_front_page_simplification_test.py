from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1231FrontPageSimplificationTest(unittest.TestCase):
    def test_root_readme_is_a_product_landing_page(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertLessEqual(len(text.splitlines()), 180)
        for phrase in (
            "## Start Fast",
            "## What You Write",
            "## What RTDL Contains",
            "## Performance Boundary",
            "## Read Next",
            "## History And Audit Trail",
            "[Public Documentation Map](docs/public_documentation_map.md)",
            "[Docs Index](docs/README.md)",
            "[Quick Tutorial](docs/quick_tutorial.md)",
            "[Performance Model](docs/performance_model.md)",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_front_page_does_not_embed_project_evolution(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        forbidden = (
            "v1.0 is for proving",
            "v1.1 through",
            "v1.5 is the released",
            "v1.7-v2.0",
            "Goal748",
            "Goal1177",
            "candidate docs",
            "roadmap boundary",
            "foundation proof",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)

    def test_front_page_keeps_claim_boundary(self) -> None:
        compact = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())

        self.assertIn("`--backend optix` means the OptiX backend is selected", compact)
        self.assertIn("not by itself a claim that every app", compact)
        self.assertIn("selected long RT-heavy workloads", compact)
        self.assertIn("Use exact benchmark artifacts before publishing performance wording", compact)


if __name__ == "__main__":
    unittest.main()
