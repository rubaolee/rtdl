from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal510AppPerfDocRefreshTest(unittest.TestCase):
    def test_front_page_links_goal509_and_states_backend_boundaries(self) -> None:
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Robot/Barnes-Hut Linux Performance Evidence", text)
        self.assertIn("goal509_robot_barnes_linux_perf_report_2026-04-17.md", text)
        self.assertIn("robot collision screening now has bounded Linux CPU/Embree/OptiX", text)
        self.assertIn("Vulkan is not exposed for that app because it fails", text)
        self.assertIn("Barnes-Hut now has bounded Linux CPU/Embree/OptiX/Vulkan", text)

    def test_release_examples_explain_goal509_and_cli_boundaries(self) -> None:
        text = (REPO_ROOT / "docs" / "release_facing_examples.md").read_text(encoding="utf-8")

        self.assertIn("Goal509 Robot/Barnes-Hut Linux Performance Report", text)
        self.assertIn("rejects robot Vulkan because it\nfails per-edge hit-count parity", text)
        self.assertIn("examples/rtdl_robot_collision_screening_app.py --backend optix", text)
        self.assertIn("Vulkan is not a supported public backend for this app yet", text)
        self.assertIn("examples/rtdl_barnes_hut_force_app.py --backend vulkan", text)
        self.assertIn("candidate-generation timing separately from\n  Python force-reduction timing", text)

    def test_tutorials_and_examples_index_carry_goal509_boundaries(self) -> None:
        app_tutorial = (REPO_ROOT / "docs" / "tutorials" / "v0_8_app_building.md").read_text(encoding="utf-8")
        cookbook = (REPO_ROOT / "docs" / "tutorials" / "feature_quickstart_cookbook.md").read_text(encoding="utf-8")
        examples = (REPO_ROOT / "examples" / "README.md").read_text(encoding="utf-8")

        for text in (app_tutorial, cookbook):
            self.assertIn("Goal509 Robot/Barnes-Hut Linux Performance Report", text)
            self.assertIn("Vulkan", text)
            self.assertTrue("force-reduction" in text or "force\n  reduction" in text)

        self.assertIn("vulkan` is intentionally not exposed", examples)
        self.assertIn("candidate-generation timing\n  separately from Python force-reduction timing", examples)


if __name__ == "__main__":
    unittest.main()
