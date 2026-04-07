import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_XML = ROOT / "tests" / "fixtures" / "pathology" / "monuseg_sample.xml"


class Goal141PublicJaccardAuditTest(unittest.TestCase):
    def test_fixture_xml_converts_to_unit_square_polygons(self) -> None:
        polygons = rt.load_monuseg_xml_annotations(FIXTURE_XML)
        unit_square_polygons = rt.monuseg_polygons_to_unit_square_polygons(polygons)
        self.assertEqual(len(polygons), 2)
        self.assertEqual(len(unit_square_polygons), 32)

    def test_build_public_case_from_zip_fixture(self) -> None:
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            zip_path = Path(tmpdir) / "fixture_monuseg.zip"
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.write(FIXTURE_XML, arcname="MoNuSeg 2018 Training Data/Annotations/TCGA-38-6178-01Z-00-DX1.xml")
            case = rt.build_goal141_public_case(zip_path, polygon_limit=2)
            self.assertEqual(case.raw_polygon_count, 2)
            self.assertEqual(case.selected_polygon_count, 2)
            self.assertEqual(len(case.left_polygons), 32)
            self.assertEqual(len(case.right_polygons), 32)
            self.assertEqual(case.right_polygons[0].vertices[0][0], case.left_polygons[0].vertices[0][0] + 1.0)

    def test_artifact_writer(self) -> None:
        payload = {
            "generated_at": "2026-04-06T23:59:00",
            "host": {"platform": "linux-test"},
            "dataset": {
                "source": "MoNuSeg 2018 Training Data",
                "xml_name": "sample.xml",
                "raw_polygon_count": 2,
                "selected_polygon_count": 2,
                "base_left_polygon_count": 32,
                "base_right_polygon_count": 32,
                "pair_derivation": "shifted by +1 x",
            },
            "rows": [
                {
                    "copies": 1,
                    "left_polygon_count": 32,
                    "right_polygon_count": 32,
                    "python_sec": 0.1,
                    "cpu_sec": 0.05,
                    "postgis_sec": 0.02,
                    "python_parity_vs_postgis": True,
                    "cpu_parity_vs_postgis": True,
                    "postgis_rows": (
                        {
                            "intersection_area": 24,
                            "left_area": 32,
                            "right_area": 32,
                            "union_area": 40,
                            "jaccard_similarity": 0.6,
                        },
                    ),
                }
            ],
        }
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            artifacts = rt.write_goal141_artifacts(payload, tmpdir)
            self.assertTrue(artifacts["json"].exists())
            self.assertTrue(artifacts["markdown"].exists())
            self.assertAlmostEqual(
                json.loads(artifacts["json"].read_text(encoding="utf-8"))["rows"][0]["postgis_rows"][0]["jaccard_similarity"],
                0.6,
            )
            self.assertIn("Goal 141 Public Jaccard Audit", artifacts["markdown"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
