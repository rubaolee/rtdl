import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal140PolygonSetJaccardPostgisTest(unittest.TestCase):
    def test_postgis_artifact_writer(self) -> None:
        payload = {
            "generated_at": "2026-04-06T23:59:00",
            "host": {"platform": "linux-test"},
            "postgis_sec": 0.01,
            "postgis_rows": (
                {
                    "intersection_area": 5,
                    "left_area": 13,
                    "right_area": 11,
                    "union_area": 19,
                    "jaccard_similarity": 5.0 / 19.0,
                },
            ),
            "python_rows": (),
            "cpu_rows": (),
            "python_parity_vs_postgis": True,
            "cpu_parity_vs_postgis": True,
        }
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            artifacts = rt.write_goal140_artifacts(payload, tmpdir)
            self.assertTrue(artifacts["json"].exists())
            self.assertTrue(artifacts["markdown"].exists())
            self.assertAlmostEqual(
                json.loads(artifacts["json"].read_text(encoding="utf-8"))["postgis_rows"][0]["jaccard_similarity"],
                5.0 / 19.0,
            )
            self.assertIn(
                "Goal 140 Polygon Set Jaccard Summary",
                artifacts["markdown"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
