from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal506PublicEntryV08AlignmentTest(unittest.TestCase):
    def test_readme_names_v0_8_app_building_without_release_overclaim(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("accepted `v0.8` app-building work", readme)
        self.assertIn("docs/tutorials/v0_8_app_building.md", readme)
        self.assertIn("examples/rtdl_hausdorff_distance_app.py", readme)
        self.assertIn("examples/rtdl_robot_collision_screening_app.py", readme)
        self.assertIn("examples/rtdl_barnes_hut_force_app.py", readme)
        self.assertIn("without claiming a new released language/backend line yet", readme)
        self.assertIn('not a new released\n    backend/language surface', readme)

    def test_docs_index_routes_new_users_to_v0_8_app_building(self) -> None:
        docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

        self.assertIn("[v0.8 App Building](tutorials/v0_8_app_building.md)", docs_index)
        self.assertIn("current `main` carries the released bounded `v0.7.0` DB line plus accepted", docs_index)
        self.assertIn("Hausdorff distance app using `knn_rows(k=1)`", docs_index)
        self.assertIn("robot collision screening app using `ray_triangle_hit_count`", docs_index)
        self.assertIn("Barnes-Hut force approximation app using `fixed_radius_neighbors`", docs_index)
        self.assertIn("without\n    claiming new backend or language internals", docs_index)

    def test_architecture_links_v0_8_app_pattern_and_boundaries(self) -> None:
        architecture = (REPO_ROOT / "docs" / "current_architecture.md").read_text(encoding="utf-8")

        self.assertIn("released `v0.7.0` design plus the accepted `v0.8` app-building direction", architecture)
        self.assertIn("Hausdorff distance over `knn_rows`", architecture)
        self.assertIn("robot collision screening over `ray_triangle_hit_count`", architecture)
        self.assertIn("Barnes-Hut force\napproximation over `fixed_radius_neighbors`", architecture)
        self.assertIn("[v0.8 App Building](tutorials/v0_8_app_building.md)", architecture)


if __name__ == "__main__":
    unittest.main()
