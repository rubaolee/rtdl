import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl.goal228_v0_4_nearest_neighbor_perf as goal228
from rtdsl.reference import Point


class Goal228NearestNeighborPerfHarnessTest(unittest.TestCase):
    def test_tile_points_assigns_unique_ids(self) -> None:
        tiled = goal228.tile_points(
            (
                Point(id=10, x=1.0, y=2.0),
                Point(id=20, x=3.0, y=4.0),
            ),
            copies=3,
            step_x=10.0,
            step_y=5.0,
        )
        self.assertEqual(len(tiled), 6)
        self.assertEqual(tuple(point.id for point in tiled), (1, 2, 3, 4, 5, 6))
        self.assertEqual((tiled[2].x, tiled[2].y), (11.0, 7.0))

    def test_build_real_world_case_applies_query_stride(self) -> None:
        base = tuple(Point(id=index + 1, x=float(index), y=float(index)) for index in range(4))
        case = goal228.build_real_world_case(base, copies=2, query_stride=3)
        self.assertEqual(len(case["search_points"]), 8)
        self.assertEqual(len(case["query_points"]), 3)

    def test_ensure_natural_earth_populated_places_downloads_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "places.geojson"
            response = mock.Mock()
            response.read.return_value = b'{"type":"FeatureCollection","features":[]}'
            response.__enter__ = mock.Mock(return_value=response)
            response.__exit__ = mock.Mock(return_value=False)
            with mock.patch.object(goal228, "urlopen", return_value=response) as patched:
                result = goal228.ensure_natural_earth_populated_places(target)
                self.assertEqual(result, target)
                self.assertTrue(target.exists())
                patched.assert_called_once()
            with mock.patch.object(goal228, "urlopen") as patched:
                goal228.ensure_natural_earth_populated_places(target)
                patched.assert_not_called()

    def test_render_markdown_includes_all_backends(self) -> None:
        payload = {
            "dataset_url": "https://example.invalid/data.geojson",
            "base_point_count": 100,
            "min_seconds_per_backend": 10.0,
            "workload_configs": {
                "fixed_radius_neighbors": {"copies": 16, "query_stride": 4},
                "knn_rows": {"copies": 1, "query_stride": 16},
            },
            "cases": [
                {
                    "workload": "fixed_radius_neighbors",
                    "case": "natural_earth_tiled",
                    "query_count": 50,
                    "search_count": 200,
                    "postgis_ground_truth_rows": 123,
                    "results": [
                        {"backend": "postgis", "parity_ok": True, "row_count": 123, "iterations": 2, "median_ms": 10.0, "min_ms": 9.0, "max_ms": 11.0, "total_ms": 20.0},
                        {"backend": "cpu", "parity_ok": True, "row_count": 123, "iterations": 2, "median_ms": 8.0, "min_ms": 7.0, "max_ms": 9.0, "total_ms": 16.0},
                        {"backend": "embree", "parity_ok": True, "row_count": 123, "iterations": 2, "median_ms": 4.0, "min_ms": 3.0, "max_ms": 5.0, "total_ms": 8.0},
                        {"backend": "optix", "parity_ok": True, "row_count": 123, "iterations": 2, "median_ms": 2.0, "min_ms": 2.0, "max_ms": 2.0, "total_ms": 4.0},
                        {"backend": "vulkan", "parity_ok": True, "row_count": 123, "iterations": 2, "median_ms": 3.0, "min_ms": 3.0, "max_ms": 3.0, "total_ms": 6.0},
                    ],
                }
            ],
        }
        markdown = goal228.render_markdown(payload)
        self.assertIn("| postgis | True |", markdown)
        self.assertIn("| cpu | True |", markdown)
        self.assertIn("| embree | True |", markdown)
        self.assertIn("| optix | True |", markdown)
        self.assertIn("| vulkan | True |", markdown)


if __name__ == "__main__":
    unittest.main()
