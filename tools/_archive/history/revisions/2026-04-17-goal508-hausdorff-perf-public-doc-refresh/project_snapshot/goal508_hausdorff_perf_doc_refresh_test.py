from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal508HausdorffPerfDocRefreshTest(unittest.TestCase):
    def test_release_examples_mentions_hausdorff_gpu_path_and_boundary(self) -> None:
        text = (REPO_ROOT / "docs" / "release_facing_examples.md").read_text(encoding="utf-8")

        self.assertIn("examples/rtdl_hausdorff_distance_app.py --backend optix", text)
        self.assertIn("examples/rtdl_hausdorff_distance_app.py --backend vulkan", text)
        self.assertIn("Goal507 Hausdorff Linux Performance Report", text)
        self.assertIn("does not show RTDL\nbeating mature exact 2D nearest-neighbor baselines", text)
        self.assertIn("do not generalize the Hausdorff app's GPU CLI support", text)

    def test_nearest_neighbor_tutorial_links_goal507(self) -> None:
        text = (REPO_ROOT / "docs" / "tutorials" / "nearest_neighbor_workloads.md").read_text(encoding="utf-8")

        self.assertIn("examples/rtdl_hausdorff_distance_app.py --backend embree", text)
        self.assertIn("examples/rtdl_hausdorff_distance_app.py --backend optix", text)
        self.assertIn("examples/rtdl_hausdorff_distance_app.py --backend vulkan", text)
        self.assertIn("../reports/goal507_hausdorff_linux_perf_report_2026-04-17.md", text)
        self.assertIn("SciPy `cKDTree` and FAISS `IndexFlatL2` remain faster", text)

    def test_front_page_and_cookbook_point_to_goal507(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        cookbook = (REPO_ROOT / "docs" / "tutorials" / "feature_quickstart_cookbook.md").read_text(encoding="utf-8")
        app_building = (REPO_ROOT / "docs" / "tutorials" / "v0_8_app_building.md").read_text(encoding="utf-8")

        self.assertIn("Hausdorff Linux Performance Evidence", readme)
        self.assertIn("goal507_hausdorff_linux_perf_report_2026-04-17.md", readme)
        self.assertIn("Goal507 covers Embree, OptiX, Vulkan, SciPy", cookbook)
        self.assertIn("do not beat the\n  strongest mature nearest-neighbor library baselines", cookbook)
        self.assertIn("Goal507 Hausdorff Linux Performance Report", app_building)
        self.assertIn("SciPy `cKDTree` and FAISS `IndexFlatL2` remain\n  stronger", app_building)


if __name__ == "__main__":
    unittest.main()
