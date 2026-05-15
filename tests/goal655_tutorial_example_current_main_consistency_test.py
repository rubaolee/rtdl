from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal655TutorialExampleCurrentMainConsistencyTest(unittest.TestCase):
    def test_release_facing_examples_preserve_v096_backend_feature_boundary(self) -> None:
        text = (REPO_ROOT / "docs" / "release_facing_examples.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("v2.0", text)
        self.assertIn("source-tree", text)
        self.assertIn("App Engine Support Matrix", text)
        self.assertIn("current_main_support_matrix.md", text)

    def test_examples_index_no_longer_calls_vulkan_apple_anyhit_compat_only(self) -> None:
        text = (REPO_ROOT / "examples" / "README.md").read_text(encoding="utf-8")

        self.assertIn("v2.0", text)
        self.assertIn("OptiX", text)
        self.assertIn("Embree", text)
        self.assertIn("../docs/current_main_support_matrix.md", text)
        self.assertNotIn(
            "Vulkan and Apple RT use\n  compatibility projection when exposed for this feature",
            text,
        )

    def test_quick_tutorial_points_to_current_main_matrix(self) -> None:
        text = (REPO_ROOT / "docs" / "quick_tutorial.md").read_text(encoding="utf-8")

        self.assertIn("RTDL Support Matrix", text)
        self.assertIn("current_main_support_matrix.md", text)


if __name__ == "__main__":
    unittest.main()
