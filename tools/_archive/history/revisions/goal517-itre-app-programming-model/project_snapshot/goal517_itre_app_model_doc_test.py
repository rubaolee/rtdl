from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal517ItreAppModelDocTest(unittest.TestCase):
    def test_itre_doc_records_bounded_app_model(self) -> None:
        text = (REPO_ROOT / "docs" / "rtdl" / "itre_app_model.md").read_text(encoding="utf-8")

        self.assertIn("ITRE means", text)
        self.assertIn("Input", text)
        self.assertIn("Traverse", text)
        self.assertIn("Refine", text)
        self.assertIn("Emit", text)
        self.assertIn("RTDL does **not** claim that ITRE alone is a complete application language", text)
        self.assertIn("Python owns the app", text)
        self.assertIn("Hausdorff distance", text)
        self.assertIn("Robot collision screening", text)
        self.assertIn("Barnes-Hut force approximation", text)
        self.assertIn("tree-node input types", text)
        self.assertIn("grouped vector reductions", text)

    def test_public_docs_link_itre_app_model(self) -> None:
        docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        language_index = (REPO_ROOT / "docs" / "rtdl" / "README.md").read_text(encoding="utf-8")
        architecture = (REPO_ROOT / "docs" / "current_architecture.md").read_text(encoding="utf-8")
        tutorial = (REPO_ROOT / "docs" / "tutorials" / "v0_8_app_building.md").read_text(encoding="utf-8")

        self.assertIn("rtdl/itre_app_model.md", docs_index)
        self.assertIn("itre_app_model.md", language_index)
        self.assertIn("ITRE App Programming Model", architecture)
        self.assertIn("ITRE App Programming Model", tutorial)


if __name__ == "__main__":
    unittest.main()
