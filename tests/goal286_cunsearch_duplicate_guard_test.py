import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal286CuNSearchDuplicateGuardTest(unittest.TestCase):
    def test_duplicate_guard_flags_exact_cross_package_duplicates(self) -> None:
        query_points = (rt.Point3D(id=1, x=1.0, y=2.0, z=3.0),)
        search_points = (
            rt.Point3D(id=10, x=1.0, y=2.0, z=3.0),
            rt.Point3D(id=11, x=1.1, y=2.0, z=3.0),
        )
        result = rt.assess_cunsearch_duplicate_point_guard(query_points, search_points)
        self.assertFalse(result.strict_comparison_allowed)
        self.assertEqual(result.duplicate_match_count, 1)
        self.assertEqual(result.first_duplicate.query_id, 1)
        self.assertEqual(result.first_duplicate.search_id, 10)

    def test_duplicate_guard_allows_nonduplicate_packages(self) -> None:
        query_points = (rt.Point3D(id=1, x=1.0, y=2.0, z=3.0),)
        search_points = (rt.Point3D(id=10, x=4.0, y=5.0, z=6.0),)
        result = rt.assess_cunsearch_duplicate_point_guard(query_points, search_points)
        self.assertTrue(result.strict_comparison_allowed)
        self.assertEqual(result.duplicate_match_count, 0)
        self.assertIsNone(result.first_duplicate)

    def test_live_comparison_returns_blocked_note_for_duplicate_packages(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            query_package = root / "query.json"
            search_package = root / "search.json"
            query_payload = {
                "package_kind": "kitti_bounded_point_package_v1",
                "selected_frame_count": 1,
                "selected_point_count": 1,
                "max_points_per_frame": 1,
                "max_total_points": 1,
                "point_id_start": 1,
                "points": [{"id": 1, "x": 1.0, "y": 2.0, "z": 3.0}],
            }
            search_payload = {
                "package_kind": "kitti_bounded_point_package_v1",
                "selected_frame_count": 1,
                "selected_point_count": 2,
                "max_points_per_frame": 2,
                "max_total_points": 2,
                "point_id_start": 10,
                "points": [
                    {"id": 10, "x": 1.0, "y": 2.0, "z": 3.0},
                    {"id": 11, "x": 1.1, "y": 2.0, "z": 3.0},
                ],
            }
            query_package.write_text(json.dumps(query_payload), encoding="utf-8")
            search_package.write_text(json.dumps(search_payload), encoding="utf-8")
            result = rt.compare_bounded_fixed_radius_live_cunsearch(
                query_package_path=query_package,
                search_package_path=search_package,
                request_path=root / "request.json",
                response_path=root / "response.json",
                radius=1.0,
                k_max=1,
                cunsearch_source_root=root / "missing_src",
                cunsearch_build_root=root / "missing_build",
            )
            self.assertFalse(result.parity_ok)
            self.assertIn("blocked", result.notes.lower())
            self.assertIn("duplicate", result.notes.lower())


if __name__ == "__main__":
    unittest.main()
