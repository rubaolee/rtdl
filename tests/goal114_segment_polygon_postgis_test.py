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


class Goal114SegmentPolygonPostgisTest(unittest.TestCase):
    def test_segment_polygon_large_dataset_name(self) -> None:
        self.assertEqual(
            rt.segment_polygon_large_dataset_name(copies=64),
            "derived/br_county_subset_segment_polygon_tiled_x64",
        )

    def test_baseline_runner_supports_generic_segment_polygon_tiled_dataset(self) -> None:
        case = load_representative_case(
            "segment_polygon_hitcount",
            "derived/br_county_subset_segment_polygon_tiled_x16",
        )
        self.assertEqual(len(case.inputs["segments"]), 160)
        self.assertEqual(len(case.inputs["polygons"]), 32)

    def test_write_goal114_artifacts(self) -> None:
        payload = {
            "generated_at": "2026-04-05T23:59:00",
            "dataset": "derived/br_county_subset_segment_polygon_tiled_x64",
            "segment_count": 640,
            "polygon_count": 128,
            "host": {"platform": "test-host"},
            "postgis": {"sec": 1.25, "row_count": 640, "sha256": "abc"},
            "records": [
                {
                    "backend": "embree",
                    "sec": 0.5,
                    "row_count": 640,
                    "parity_vs_postgis": True,
                    "hash": {"sha256": "abc"},
                }
            ],
        }
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            artifacts = rt.write_goal114_artifacts(payload, tmpdir)
            self.assertTrue(artifacts["json"].exists())
            self.assertTrue(artifacts["markdown"].exists())
            self.assertEqual(
                json.loads(artifacts["json"].read_text(encoding="utf-8"))["segment_count"],
                640,
            )
            self.assertIn(
                "Goal 114 Segment/Polygon PostGIS Validation Summary",
                artifacts["markdown"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
