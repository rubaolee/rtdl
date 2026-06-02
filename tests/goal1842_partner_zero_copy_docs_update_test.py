from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "docs" / "tutorials" / "partner_optix_column_anyhit.md"
TUTORIALS_INDEX = ROOT / "docs" / "tutorials" / "README.md"
DOCS_INDEX = ROOT / "docs" / "README.md"
README = ROOT / "README.md"
APP_QUICKSTART = ROOT / "docs" / "app_example_quickstart.md"


class Goal1842PartnerZeroCopyDocsUpdateTest(unittest.TestCase):
    def test_partner_column_tutorial_teaches_exact_boundary(self) -> None:
        tutorial = TUTORIAL.read_text(encoding="utf-8")

        self.assertIn("prepared OptiX any-hit primitive", tutorial)
        self.assertIn("CuPy or PyTorch owns input columns", tutorial)
        self.assertIn("documented output columns", tutorial)
        self.assertIn("general true-zero-copy product guarantee", tutorial)
        self.assertIn("broad RT-core speedup", tutorial)
        self.assertIn("Choosing A Partner For Custom Logic", tutorial)

    def test_public_indexes_link_advanced_preview_without_release_claim(self) -> None:
        tutorials_index = TUTORIALS_INDEX.read_text(encoding="utf-8")
        docs_index = DOCS_INDEX.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        app_quickstart = APP_QUICKSTART.read_text(encoding="utf-8")

        self.assertIn("partner_optix_column_anyhit.md", tutorials_index)
        self.assertIn("Partner Acceleration Boundaries", docs_index)
        self.assertIn("active internal pre-release lane is `v2.6`", readme)
        self.assertIn("OptiX Partner Column Any-Hit", app_quickstart)
        self.assertIn("true-zero-copy, or broad acceleration", app_quickstart)


if __name__ == "__main__":
    unittest.main()
