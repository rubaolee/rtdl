from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DOCS_README = ROOT / "docs" / "README.md"
LEARN_README = ROOT / "docs" / "learn" / "README.md"
TUTORIAL_README = ROOT / "tutorials" / "current" / "README.md"
KERNEL_TUTORIAL = ROOT / "tutorials" / "current" / "02_kernel_shape_and_backends.md"
PROGRAMMING_GUIDE = ROOT / "docs" / "rtdl" / "programming_guide.md"
SURFACES = ROOT / "docs" / "learn" / "programming_surfaces.md"
REPORT = ROOT / "docs" / "reports" / "goal4320_programming_surface_truthfulness_2026-06-11.md"


def _normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class Goal4320ProgrammingSurfaceTruthfulnessTest(unittest.TestCase):
    def test_canonical_programming_surface_page_names_three_surfaces(self) -> None:
        text = SURFACES.read_text(encoding="utf-8")

        for phrase in (
            "Kernel DSL",
            "Primitive and prepared front doors",
            "Partner continuation",
            "not yet the only route to performance",
            "Benchmark apps are reference compositions",
        ):
            self.assertIn(phrase, text)

    def test_public_front_doors_link_to_programming_surface_boundary(self) -> None:
        for path in (README, DOCS_README, LEARN_README, TUTORIAL_README, PROGRAMMING_GUIDE):
            text = path.read_text(encoding="utf-8")
            self.assertIn("programming_surfaces.md", text)

    def test_front_page_no_longer_claims_kernel_is_the_whole_rt_path(self) -> None:
        text = _normalized(README)

        self.assertNotIn("describe the traversal-heavy part as an RTDL kernel", text)
        self.assertIn("promoted performance paths usually start from primitive discovery or prepared front doors", text)
        self.assertIn("three public programming surfaces", text)

    def test_kernel_tutorial_marks_kernel_shape_as_mental_model(self) -> None:
        text = _normalized(KERNEL_TUTORIAL)

        self.assertIn("kernel shape is the mental model, not the only performance entry point", text)
        self.assertIn("primitive discovery and prepared front doors", text)

    def test_report_documents_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal4320",
            "programming surface truthfulness",
            "does not implement a new lowering bridge",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
