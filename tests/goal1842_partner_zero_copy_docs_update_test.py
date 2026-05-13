from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "docs" / "tutorials" / "partner_optix_zero_copy_anyhit.md"
TUTORIALS_INDEX = ROOT / "docs" / "tutorials" / "README.md"
DOCS_INDEX = ROOT / "docs" / "README.md"
README = ROOT / "README.md"
APP_QUICKSTART = ROOT / "docs" / "app_example_quickstart.md"


class Goal1842PartnerZeroCopyDocsUpdateTest(unittest.TestCase):
    def test_zero_copy_tutorial_teaches_exact_api_and_boundary(self) -> None:
        tutorial = TUTORIAL.read_text(encoding="utf-8")

        self.assertIn("prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene", tutorial)
        self.assertIn("write_device_any_hit_flags", tutorial)
        self.assertIn("--output-flags", tutorial)
        self.assertIn("Torch/CuPy CUDA input-plus-output", tutorial)
        self.assertIn("zero-copy slice", tutorial)
        self.assertIn("v2.0 release readiness", tutorial)
        self.assertIn("broad RT-core speedup", tutorial)
        self.assertIn("OptiX still creates native GAS state", tutorial)

    def test_public_indexes_link_advanced_preview_without_release_claim(self) -> None:
        tutorials_index = TUTORIALS_INDEX.read_text(encoding="utf-8")
        docs_index = DOCS_INDEX.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        app_quickstart = APP_QUICKSTART.read_text(encoding="utf-8")

        self.assertIn("partner_optix_zero_copy_anyhit.md", tutorials_index)
        self.assertIn("partner_optix_zero_copy_anyhit.md", docs_index)
        self.assertIn("not a finished v2.0 release", readme)
        self.assertIn("one measured primitive path", readme)
        self.assertIn("Goal1838 --output-flags", app_quickstart)
        self.assertIn("v2.0 release readiness or broad acceleration", app_quickstart)


if __name__ == "__main__":
    unittest.main()
