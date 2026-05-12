import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1740_v1_8_public_docs_boundary_alignment_2026-05-12.md"


class Goal1740V18PublicDocsBoundaryAlignmentTest(unittest.TestCase):
    def test_current_architecture_separates_v1_6_history_from_v1_8_release(self) -> None:
        text = (ROOT / "docs" / "current_architecture.md").read_text(encoding="utf-8")
        self.assertIn("Current Main Lens", text)
        self.assertIn("v1.8 is the current released source-tree Python+RTDL language boundary", text)
        self.assertIn("v1.6 remains the earlier Python+RTDL architecture milestone", text)
        self.assertIn("not a partner-readiness claim", text)
        self.assertIn("not a universal", text)
        self.assertIn("zero-copy claim", text)

    def test_current_support_matrix_preserves_release_boundary(self) -> None:
        text = (ROOT / "docs" / "current_main_support_matrix.md").read_text(encoding="utf-8")
        self.assertIn("Current public release: `v1.8`", text)
        self.assertIn("tracked release native surface", text)
        self.assertIn("Goal1769", text)
        self.assertIn("This page is not a speedup claim", text)

    def test_performance_model_blocks_overclaims(self) -> None:
        text = (ROOT / "docs" / "performance_model.md").read_text(encoding="utf-8")
        self.assertIn("released\nv1.8 source-tree Python+RTDL language boundary", text)
        self.assertIn("v1.8 finishes Python+RTDL productization", text)
        self.assertIn("v2.0 finishes Python+partner+RTDL", text)
        self.assertIn("They\nshould not claim universal whole-app speedup", text)
        self.assertIn("arbitrary RTX acceleration", text)
        self.assertIn("universal partner zero-copy", text)

    def test_report_records_boundary_and_remaining_docs_work(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("docs_boundary_aligned_for_v1_8_preparation", text)
        self.assertIn("not a v1.8 release packet", text)
        self.assertIn("not a tag authorization", text)
        self.assertIn("not a packaging/install decision", text)
        self.assertIn("root `README.md`", text)
        self.assertIn("`docs/README.md`", text)
        self.assertIn("`docs/public_documentation_map.md`", text)
        self.assertIn("final documentation sweep should still cover any v1.8 release package files", text)

    def test_front_door_docs_name_v1_8_released_boundary(self) -> None:
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        public_map = (ROOT / "docs" / "public_documentation_map.md").read_text(encoding="utf-8")
        for text in (root_readme, docs_readme, public_map):
            self.assertIn("v1.8", text)
            self.assertIn("current released version is `v1.8`", text)
        self.assertIn("source-tree Python+RTDL\nlanguage release", root_readme)
        self.assertIn("source-tree Python+RTDL\nlanguage release", docs_readme)
        self.assertIn("Partner-framework readiness and universal zero-copy remain v2.0 work", public_map)


if __name__ == "__main__":
    unittest.main()
