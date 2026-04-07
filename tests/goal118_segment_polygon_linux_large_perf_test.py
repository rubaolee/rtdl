import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal118SegmentPolygonLinuxLargePerfTest(unittest.TestCase):
    def test_render_goal118_markdown_mentions_postgis_and_vulkan_boundary(self) -> None:
        payload = {
            "generated_at": "2026-04-06T10:00:00",
            "host": {"platform": "linux-test"},
            "versions": {
                "oracle": "oracle",
                "embree": "embree",
                "optix": "optix",
                "vulkan": "vulkan",
            },
            "prepared_copies": (64,),
            "postgis_rows": [
                {
                    "dataset": "derived/br_county_subset_segment_polygon_tiled_x64",
                    "segment_count": 640,
                    "polygon_count": 128,
                    "postgis": {"sec": 0.1},
                    "records": [
                        {"backend": "cpu", "sec": 0.2, "parity_vs_postgis": True},
                        {"backend": "embree", "sec": 0.3, "parity_vs_postgis": True},
                        {"backend": "optix", "sec": 0.05, "parity_vs_postgis": True},
                        {"backend": "vulkan", "sec": 0.25, "parity_vs_postgis": True},
                    ],
                }
            ],
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
                {
                    "dataset": "derived/br_county_subset_segment_polygon_tiled_x64",
                    "backend": "optix",
                    "mean_sec": 0.05,
                    "prepared_bind_and_run": {"mean_sec": 0.04},
                    "prepared_reuse": {"mean_sec": 0.03},
                },
                {
                    "dataset": "derived/br_county_subset_segment_polygon_tiled_x64",
                    "backend": "vulkan",
                    "mean_sec": 0.25,
                },
            ],
        }
        markdown = rt.render_goal118_markdown(payload)
        self.assertIn("PostGIS-Backed Large-Scale Results", markdown)
        self.assertIn("accepted correctness-first runtime boundary", markdown)
        self.assertIn("derived/br_county_subset_segment_polygon_tiled_x64", markdown)
        self.assertIn("| `derived/br_county_subset_segment_polygon_tiled_x64` | `cpu` | 0.200000 | n/a | n/a |", markdown)
        self.assertIn("| `derived/br_county_subset_segment_polygon_tiled_x64` | `vulkan` | 0.250000 | n/a | n/a |", markdown)

    def test_write_goal118_artifacts_writes_json_and_markdown(self) -> None:
        payload = {
            "generated_at": "2026-04-06T10:00:00",
            "host": {"platform": "linux-test"},
            "versions": {"oracle": "o", "embree": "e", "optix": "x", "vulkan": "v"},
            "copies": (64,),
            "prepared_copies": (64,),
            "perf_iterations": 3,
            "postgis_rows": [],
            "performance_rows": [],
        }
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            artifacts = rt.write_goal118_artifacts(payload, tmpdir)
            self.assertTrue(artifacts["json"].exists())
            self.assertTrue(artifacts["markdown"].exists())
            self.assertEqual(json.loads(artifacts["json"].read_text(encoding="utf-8"))["perf_iterations"], 3)
            self.assertIn(
                "Goal 118 Segment/Polygon Linux Large-Scale Performance",
                artifacts["markdown"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
