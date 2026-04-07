import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal138PolygonOverlapPostgisTest(unittest.TestCase):
    def test_postgis_artifact_writer(self) -> None:
        payload = {
            "generated_at": "2026-04-06T23:59:00",
            "host": {"platform": "linux-test"},
            "postgis_sec": 0.01,
            "postgis_rows": (
                {
                    "left_polygon_id": 1,
                    "right_polygon_id": 10,
                    "intersection_area": 4,
                    "left_area": 9,
                    "right_area": 9,
                    "union_area": 14,
                },
            ),
            "python_rows": (),
            "cpu_rows": (),
            "python_parity_vs_postgis": True,
            "cpu_parity_vs_postgis": True,
        }
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            artifacts = rt.write_goal138_artifacts(payload, tmpdir)
            self.assertTrue(artifacts["json"].exists())
            self.assertTrue(artifacts["markdown"].exists())
            self.assertEqual(
                json.loads(artifacts["json"].read_text(encoding="utf-8"))["postgis_rows"][0]["union_area"],
                14,
            )
            self.assertIn(
                "Goal 138 Polygon Pair Overlap Area Rows Summary",
                artifacts["markdown"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
