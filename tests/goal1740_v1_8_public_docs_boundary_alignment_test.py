import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1740_v1_8_public_docs_boundary_alignment_2026-05-12.md"


class Goal1740V18PublicDocsBoundaryAlignmentTest(unittest.TestCase):
    def test_current_architecture_states_current_v2_release_boundary(self) -> None:
        text = (ROOT / "docs" / "current_architecture.md").read_text(encoding="utf-8")
        self.assertIn("RTDL v2.3 is the current source-tree", text)
        self.assertIn("Python application", text)
        self.assertIn("Partner adapter", text)
        self.assertIn("Native engines must remain app-agnostic", text)
        self.assertIn("not a public performance claim", text)

    def test_current_support_matrix_preserves_release_boundary(self) -> None:
        text = (ROOT / "docs" / "current_main_support_matrix.md").read_text(encoding="utf-8")
        self.assertIn("Current public docs target: v2.3 release", text)
        self.assertIn("Active release engines: Embree for CPU RT, OptiX for NVIDIA RT", text)
        self.assertIn("Engine ABI rule: native backends stay app-agnostic", text)
        self.assertIn("Performance rule: a backend flag is not a speedup claim", text)

    def test_performance_model_blocks_overclaims(self) -> None:
        text = (ROOT / "docs" / "performance_model.md").read_text(encoding="utf-8")
        self.assertIn("selecting a\nbackend", text)
        self.assertIn("Whole app", text)
        self.assertIn("partner", text)
        self.assertIn("artifact", text)

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

    def test_front_door_docs_name_current_released_boundary(self) -> None:
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        public_map = (ROOT / "docs" / "public_documentation_map.md").read_text(encoding="utf-8")
        for text in (root_readme, docs_readme, public_map):
            self.assertIn("v2.3", text)
            self.assertIn("Python+partner+RTDL", text)
        self.assertIn("current released version is `v2.3`", root_readme)
        self.assertIn("current released version is `v2.3`", docs_readme)
        self.assertIn("completed release-package boundary", public_map)


if __name__ == "__main__":
    unittest.main()
