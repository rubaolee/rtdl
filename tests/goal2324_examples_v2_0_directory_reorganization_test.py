from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


class Goal2324ExamplesV20DirectoryReorganizationTest(unittest.TestCase):
    def test_examples_root_is_not_a_flat_script_dump(self) -> None:
        root_scripts = sorted(path.name for path in EXAMPLES.glob("rtdl_*.py"))
        self.assertEqual(root_scripts, [])
        for dirname in [
            "v2_0",
            "legacy_or_backend_proofs",
            "reference",
            "generated",
            "internal",
            "visual_demo",
        ]:
            self.assertTrue((EXAMPLES / dirname).exists(), dirname)

    def test_v2_0_has_versioned_purpose_directories(self) -> None:
        for rel in [
            "v2_0/getting_started/rtdl_hello_world.py",
            "v2_0/getting_started/rtdl_feature_quickstart_cookbook.py",
            "v2_0/features/ray_queries/rtdl_ray_triangle_any_hit.py",
            "v2_0/features/neighbors/rtdl_fixed_radius_neighbors.py",
            "v2_0/features/database/rtdl_db_conjunctive_scan.py",
            "v2_0/features/graph/rtdl_graph_bfs.py",
            "v2_0/features/spatial/rtdl_segment_polygon_hitcount.py",
            "v2_0/apps/ml/rtdl_outlier_detection_app.py",
            "v2_0/partners/rtdl_partner_anyhit.py",
            "v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py",
            "v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py",
        ]:
            self.assertTrue((EXAMPLES / rel).exists(), rel)

    def test_root_readme_names_audience_and_research_benchmark_dirs(self) -> None:
        text = (EXAMPLES / "README.md").read_text(encoding="utf-8")
        for phrase in [
            "RTDL v2.0 users first",
            "v2_0/getting_started/",
            "v2_0/features/",
            "v2_0/apps/",
            "v2_0/partners/",
            "v2_0/research_benchmarks/hausdorff_xhd/",
            "v2_0/research_benchmarks/spatial_rayjoin/",
            "legacy_or_backend_proofs/",
        ]:
            self.assertIn(phrase, text)

    def test_current_public_docs_do_not_use_old_flat_entrypoints(self) -> None:
        old_paths = [
            "examples/rtdl_hello_world.py",
            "examples/rtdl_feature_quickstart_cookbook.py",
            "examples/rtdl_partner_anyhit.py",
            "examples/rtdl_hausdorff_distance_app.py",
            "examples/rtdl_rayjoin_v2_spatial_join_app.py",
            "examples/rtdl_segment_polygon_hitcount.py",
            "examples/rtdl_polygon_pair_overlap_area_rows.py",
            "examples/rtdl_db_conjunctive_scan.py",
            "examples/rtdl_graph_bfs.py",
        ]
        docs = [
            ROOT / "README.md",
            ROOT / "docs" / "README.md",
            ROOT / "docs" / "quick_tutorial.md",
            ROOT / "docs" / "app_example_quickstart.md",
            ROOT / "docs" / "application_catalog.md",
            ROOT / "docs" / "app_engine_support_matrix.md",
            ROOT / "docs" / "release_facing_examples.md",
            ROOT / "docs" / "release_reports" / "v2_0" / "README.md",
            EXAMPLES / "README.md",
        ]
        docs.extend((ROOT / "docs" / "tutorials").glob("*.md"))
        docs.extend((ROOT / "docs" / "features").glob("**/*.md"))
        for path in docs:
            text = path.read_text(encoding="utf-8")
            for old_path in old_paths:
                self.assertNotIn(old_path, text, str(path))


if __name__ == "__main__":
    unittest.main()
