import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal112SegmentPolygonPerfTest(unittest.TestCase):
    def test_render_goal112_markdown_includes_prepared_columns(self) -> None:
        payload = {
            "generated_at": "2026-04-05T23:59:00",
            "iterations": 2,
            "host": {"platform": "test-host"},
            "records": [
                {
                    "dataset": "authored_segment_polygon_minimal",
                    "backend": "cpu",
                    "available": True,
                    "parity": True,
                    "current": {"mean_sec": 0.1},
                },
                {
                    "dataset": "authored_segment_polygon_minimal",
                    "backend": "embree",
                    "available": True,
                    "parity": True,
                    "current": {"mean_sec": 0.05},
                    "prepared_bind_and_run": {"mean_sec": 0.04},
                    "prepared_reuse": {"mean_sec": 0.02},
                },
            ],
        }
        markdown = rt.render_goal112_markdown(payload)
        self.assertIn("Prepared Bind+Run Mean", markdown)
        self.assertIn("authored_segment_polygon_minimal", markdown)
        self.assertIn("embree", markdown)

    def test_write_goal112_artifacts_writes_json_and_markdown(self) -> None:
        payload = {
            "generated_at": "2026-04-05T23:59:00",
            "iterations": 1,
            "host": {"platform": "test-host"},
            "records": [],
        }
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            artifacts = rt.write_goal112_artifacts(payload, tmpdir)
            self.assertTrue(artifacts["json"].exists())
            self.assertTrue(artifacts["markdown"].exists())
            self.assertEqual(json.loads(artifacts["json"].read_text(encoding="utf-8"))["iterations"], 1)
            self.assertIn("Goal 112 Segment/Polygon Performance Summary", artifacts["markdown"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
