import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal116SegmentPolygonBackendAuditTest(unittest.TestCase):
    def test_render_goal116_markdown_mentions_postgis(self) -> None:
        payload = {
            "generated_at": "2026-04-06T00:00:00",
            "host": {"platform": "test-host"},
            "oracle_records": [
                {
                    "dataset": "authored_segment_polygon_minimal",
                    "backend": "cpu",
                    "available": True,
                    "parity_vs_cpu_python_reference": True,
                    "row_count": 2,
                }
            ],
            "performance_records": [
                {
                    "dataset": "authored_segment_polygon_minimal",
                    "backend": "cpu",
                    "available": True,
                    "parity": True,
                    "current": {"mean_sec": 0.1},
                }
            ],
            "postgis_validation": {
                "dataset": "derived/br_county_subset_segment_polygon_tiled_x64",
                "postgis": {"sha256": "abc"},
            },
            "postgis_large_validation": {
                "dataset": "derived/br_county_subset_segment_polygon_tiled_x256",
                "postgis": {"sha256": "def"},
            },
        }
        markdown = rt.render_goal116_markdown(payload)
        self.assertIn("Goal 116 Segment/Polygon Full Backend Audit", markdown)
        self.assertIn("PostGIS Validation", markdown)
        self.assertIn("derived/br_county_subset_segment_polygon_tiled_x256", markdown)

    def test_write_goal116_artifacts_writes_json_and_markdown(self) -> None:
        payload = {
            "generated_at": "2026-04-06T00:00:00",
            "host": {"platform": "test-host"},
            "oracle_records": [],
            "performance_records": [],
            "postgis_validation": {"dataset": "x64", "postgis": {"sha256": "abc"}},
            "postgis_large_validation": {"dataset": "x256", "postgis": {"sha256": "def"}},
        }
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            artifacts = rt.write_goal116_artifacts(payload, tmpdir)
            self.assertTrue(artifacts["json"].exists())
            self.assertTrue(artifacts["markdown"].exists())
            self.assertEqual(
                json.loads(artifacts["json"].read_text(encoding="utf-8"))["generated_at"],
                "2026-04-06T00:00:00",
            )
            self.assertIn(
                "Goal 116 Segment/Polygon Full Backend Audit",
                artifacts["markdown"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
