import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.baseline_runner import load_representative_case


ROOT = Path(__file__).resolve().parents[1]


class Goal128SegmentPolygonAnyhitPostgisTest(unittest.TestCase):
    def test_large_dataset_name_helper_reuses_segment_polygon_shape(self) -> None:
        self.assertEqual(
            rt.segment_polygon_large_dataset_name(copies=64),
            "derived/br_county_subset_segment_polygon_tiled_x64",
        )

    def test_baseline_runner_supports_anyhit_generic_tiled_dataset(self) -> None:
        case = load_representative_case(
            "segment_polygon_anyhit_rows",
            "derived/br_county_subset_segment_polygon_tiled_x16",
        )
        self.assertEqual(len(case.inputs["segments"]), 160)
        self.assertEqual(len(case.inputs["polygons"]), 32)
        self.assertEqual(case.workload, "segment_polygon_anyhit_rows")

    def test_write_goal128_postgis_artifacts(self) -> None:
        payload = {
            "generated_at": "2026-04-06T23:59:00",
            "dataset": "derived/br_county_subset_segment_polygon_tiled_x64",
            "segment_count": 640,
            "polygon_count": 128,
            "host": {"platform": "test-host"},
            "postgis": {"sec": 1.25, "row_count": 800, "sha256": "abc"},
            "records": [
                {
                    "backend": "embree",
                    "sec": 0.5,
                    "row_count": 800,
                    "parity_vs_postgis": True,
                    "hash": {"sha256": "abc"},
                }
            ],
        }
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            artifacts = rt.write_goal128_postgis_artifacts(payload, tmpdir)
            self.assertTrue(artifacts["json"].exists())
            self.assertTrue(artifacts["markdown"].exists())
            self.assertEqual(
                json.loads(artifacts["json"].read_text(encoding="utf-8"))["polygon_count"],
                128,
            )
            self.assertIn(
                "Goal 128 Segment/Polygon Any-Hit Rows PostGIS Validation Summary",
                artifacts["markdown"].read_text(encoding="utf-8"),
            )

    def test_write_goal128_linux_artifacts(self) -> None:
        payload = {
            "generated_at": "2026-04-06T23:59:00",
            "host": {"platform": "linux-test"},
            "versions": {"oracle": "o", "embree": "e", "optix": "x", "vulkan": "v"},
            "copies": (64,),
            "prepared_copies": (64,),
            "perf_iterations": 3,
            "postgis_rows": [],
            "performance_rows": [
                {
                    "dataset": "derived/br_county_subset_segment_polygon_tiled_x64",
                    "backend": "cpu",
                    "mean_sec": 0.2,
                },
                {
                    "dataset": "derived/br_county_subset_segment_polygon_tiled_x64",
                    "backend": "embree",
                    "mean_sec": 0.3,
                    "prepared_bind_and_run": {"mean_sec": 0.28},
                    "prepared_reuse": {"mean_sec": 0.15},
                },
            ],
        }
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            artifacts = rt.write_goal128_linux_artifacts(payload, tmpdir)
            self.assertTrue(artifacts["json"].exists())
            self.assertTrue(artifacts["markdown"].exists())
            self.assertEqual(
                json.loads(artifacts["json"].read_text(encoding="utf-8"))["perf_iterations"],
                3,
            )
            self.assertIn(
                "Goal 128 Segment/Polygon Any-Hit Rows Linux Large-Scale Performance",
                artifacts["markdown"].read_text(encoding="utf-8"),
            )
            self.assertIn(
                "| `derived/br_county_subset_segment_polygon_tiled_x64` | `cpu` | 0.200000 | n/a | n/a |",
                artifacts["markdown"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
