from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "docs" / "release_reports" / "v1_0"


class Goal1248V10ReleaseCandidatePackageTest(unittest.TestCase):
    def test_release_package_files_exist_and_are_released(self) -> None:
        for name in [
            "README.md",
            "release_statement.md",
            "support_matrix.md",
            "audit_report.md",
            "tag_preparation.md",
        ]:
            with self.subTest(name=name):
                text = (PACKAGE_DIR / name).read_text(encoding="utf-8")
                self.assertIn("Status: released as `v1.0`", text)
                self.assertNotIn("Status: draft release candidate for `v1.0`; not released.", text)

    def test_package_preserves_current_release_marker_boundary(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        package_readme = (PACKAGE_DIR / "README.md").read_text(encoding="utf-8")
        self.assertEqual(version, "v2.3")
        self.assertIn("The current released version is `v1.0`", package_readme)
        self.assertIn("current released version is `v2.3`", docs_index)
        self.assertIn("Release Reports", docs_index)

    def test_package_records_v1_0_scope_and_claim_boundaries(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in PACKAGE_DIR.glob("*.md"))
        self.assertIn("`18` app rows", combined)
        self.assertIn("`12` reviewed bounded NVIDIA RTX public wording rows", combined)
        self.assertIn("broad whole-app speedup claim", combined)
        self.assertIn("app-specific native continuations", combined)
        self.assertIn("v1.5", combined)
        self.assertIn("v2.0", combined)
        self.assertIn("No immediate pod is required", combined)
        self.assertNotIn("all-app NVIDIA RT-core speedup claim is allowed", combined)

    def test_support_matrix_lists_reviewed_and_blocked_rows(self) -> None:
        support = (PACKAGE_DIR / "support_matrix.md").read_text(encoding="utf-8")
        for token in [
            "service_coverage_gaps / prepared_gap_summary",
            "event_hotspot_screening / prepared_count_summary",
            "facility_knn_assignment / coverage_threshold_prepared_recentered",
            "outlier_detection / prepared_fixed_radius_density_summary",
            "dbscan_clustering / prepared_fixed_radius_core_flags",
            "robot_collision_screening / prepared_pose_flags",
            "barnes_hut_force_app / node_coverage_prepared_rich",
            "hausdorff_distance / directed_threshold_prepared",
            "ann_candidate_search / candidate_threshold_prepared",
            "`graph_analytics` | blocked",
            "`polygon_pair_overlap_area_rows` | blocked",
            "`database_analytics` | not reviewed",
            "`polygon_set_jaccard` | not reviewed",
            "`apple_rt_demo` | non-NVIDIA target",
            "`hiprt_ray_triangle_hitcount` | non-NVIDIA target",
        ]:
            with self.subTest(token=token):
                self.assertIn(token, support)


if __name__ == "__main__":
    unittest.main()
