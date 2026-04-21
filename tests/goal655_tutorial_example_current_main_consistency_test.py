from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal655TutorialExampleCurrentMainConsistencyTest(unittest.TestCase):
    def test_release_facing_examples_use_v096_release_boundary(self) -> None:
        text = (REPO_ROOT / "docs" / "release_facing_examples.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("At the released `v0.9.6` tag boundary", text)
        self.assertIn("native early-exit exists for OptiX", text)
        self.assertIn("Embree, HIPRT, and Vulkan", text)
        self.assertIn("Apple RT 2D may use MPS prism traversal", text)
        self.assertIn("Current Main Support Matrix](current_main_support_matrix.md)", text)

    def test_examples_index_no_longer_calls_vulkan_apple_anyhit_compat_only(self) -> None:
        text = (REPO_ROOT / "examples" / "README.md").read_text(encoding="utf-8")

        self.assertIn("Current v0.9.6 example boundary", text)
        self.assertIn("OptiX, Embree, HIPRT, and Vulkan", text)
        self.assertIn("Apple RT 3D uses MPS RT nearest-intersection existence", text)
        self.assertIn("Apple RT 2D uses", text)
        self.assertIn("../docs/current_main_support_matrix.md", text)
        self.assertNotIn(
            "Vulkan and Apple RT use\n  compatibility projection when exposed for this feature",
            text,
        )

    def test_quick_tutorial_points_to_current_main_matrix(self) -> None:
        text = (REPO_ROOT / "docs" / "quick_tutorial.md").read_text(encoding="utf-8")

        self.assertIn("RTDL Current Main Support Matrix", text)
        self.assertIn("current_main_support_matrix.md", text)


if __name__ == "__main__":
    unittest.main()
