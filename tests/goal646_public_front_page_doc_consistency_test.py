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

        self.assertIn("current released version: `v1.5`", combined)
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
        self.assertIn("RTDL v1.5 is used directly from the source tree", text)
        self.assertIn("PYTHONPATH=src:. python examples/rtdl_hello_world.py", text)

    def test_docs_new_user_path_is_concise(self) -> None:
        text = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        section = text.split("## New User Path", 1)[1].split("## Evaluate RTDL", 1)[0]
        numbered = re.findall(r"^\d+\. ", section, flags=re.MULTILINE)

        self.assertGreaterEqual(len(numbered), 8)
        self.assertLessEqual(len(numbered), 15)
        self.assertIn("[v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md)", section)
        self.assertIn("[v1.5 Release Package](release_reports/v1_5/README.md)", section)
        self.assertIn("Older release packages remain linked below", section)


if __name__ == "__main__":
    unittest.main()
