from __future__ import annotations

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


PUBLIC_FRONT_PAGES = (
    Path("README.md"),
    Path("docs/README.md"),
    Path("docs/current_architecture.md"),
    Path("docs/capability_boundaries.md"),
    Path("docs/rtdl_feature_guide.md"),
    Path("docs/release_facing_examples.md"),
    Path("docs/tutorials/README.md"),
    Path("examples/README.md"),
    Path("docs/quick_tutorial.md"),
    Path("docs/backend_maturity.md"),
)


class Goal646PublicFrontPageDocConsistencyTest(unittest.TestCase):
    def test_public_front_pages_have_current_release_and_core_boundaries(self) -> None:
        combined = "\n".join(
            (REPO_ROOT / path).read_text(encoding="utf-8") for path in PUBLIC_FRONT_PAGES
        )

        self.assertIn("current released version is `v1.8`", combined)
        self.assertIn("ray_triangle_any_hit", combined)
        self.assertIn("visibility_rows", combined)
        self.assertIn("reduce_rows", combined)
        self.assertIn("OptiX, Embree, and HIPRT", combined)
        self.assertIn("Vulkan and Apple RT", combined)
        self.assertIn("not a native", combined)

    def test_public_front_pages_do_not_use_stale_release_control_wording(self) -> None:
        combined = "\n".join(
            (REPO_ROOT / path).read_text(encoding="utf-8") for path in PUBLIC_FRONT_PAGES
        )

        stale_phrases = (
            "release-candidate package",
            "tag not yet created",
            "user-controlled release action",
            "release-prepared",
            "current released version remains",
            "current `v0.9.4`",
            "current v0.9.4",
        )
        for phrase in stale_phrases:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, combined)

    def test_root_quickstart_matches_source_tree_usage_contract(self) -> None:
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertNotIn("python3 -m pip install -e .", text)
        self.assertIn("RTDL is used directly from the source", text)
        self.assertIn("PYTHONPATH=src:. python examples/rtdl_hello_world.py", text)

    def test_video_demo_has_what_why_how_intro(self) -> None:
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        demo = text.split("## Demo", 1)[1].split("## Repository Layout", 1)[0]

        self.assertIn("The video is a visual tour of the RTDL idea", demo)
        self.assertIn("Why this demo exists", demo)
        self.assertIn("How to reproduce the demo locally", demo)
        self.assertIn("Python owns scene setup and presentation", demo)
        self.assertIn("RTDL owns the traversal/refinement", demo)
        self.assertIn("examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py", demo)

    def test_docs_new_user_path_is_concise(self) -> None:
        text = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        section = text.split("## New User Path", 1)[1].split("## Read By Task", 1)[0]
        numbered = re.findall(r"^\d+\. ", section, flags=re.MULTILINE)

        self.assertGreaterEqual(len(numbered), 8)
        self.assertLessEqual(len(numbered), 16)
        self.assertIn("[Project Front Page](../README.md)", section)
        self.assertIn("[Quick Tutorial](quick_tutorial.md)", section)
        self.assertIn("[IR And Lowering](rtdl/ir_and_lowering.md)", section)


if __name__ == "__main__":
    unittest.main()
