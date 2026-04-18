from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal511FeatureGuideV08RefreshTest(unittest.TestCase):
    def test_feature_guide_carries_v08_app_building_state(self) -> None:
        text = (REPO_ROOT / "docs" / "rtdl_feature_guide.md").read_text(encoding="utf-8")

        self.assertIn("accepted `v0.8` app-building work", text)
        self.assertIn("not a released support-matrix line yet", text)
        self.assertIn("rtdl_hausdorff_distance_app.py", text)
        self.assertIn("rtdl_robot_collision_screening_app.py", text)
        self.assertIn("rtdl_barnes_hut_force_app.py", text)

    def test_feature_guide_preserves_goal507_goal509_boundaries(self) -> None:
        text = (REPO_ROOT / "docs" / "rtdl_feature_guide.md").read_text(encoding="utf-8")

        self.assertIn("Goal507 Hausdorff Linux Performance Report", text)
        self.assertIn("Goal509 Robot/Barnes-Hut Linux Performance Report", text)
        self.assertIn("Vulkan\n  is not exposed for that app", text)
        self.assertIn("This is not a full N-body acceleration claim", text)
        self.assertIn("RT-core hardware speedup from the GTX 1070 Linux app evidence", text)

    def test_docs_index_links_feature_guide_in_live_path(self) -> None:
        text = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

        self.assertIn("[Feature Guide](rtdl_feature_guide.md)", text)
        self.assertIn("[Capability Boundaries](capability_boundaries.md)", text)
        self.assertLess(
            text.index("[Feature Guide](rtdl_feature_guide.md)"),
            text.index("[Capability Boundaries](capability_boundaries.md)"),
        )


if __name__ == "__main__":
    unittest.main()
