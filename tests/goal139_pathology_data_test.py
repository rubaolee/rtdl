import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal139PathologyDataTest(unittest.TestCase):
    def test_public_dataset_registry_contains_nuinsseg_and_monuseg(self) -> None:
        datasets = {dataset.key: dataset for dataset in rt.public_pathology_datasets()}
        self.assertIn("nuinsseg", datasets)
        self.assertIn("monuseg", datasets)
        self.assertEqual(datasets["nuinsseg"].size_bytes, 1627427342)
        self.assertIn("google", datasets["monuseg"].access_kind)

    def test_parse_monuseg_xml_annotations(self) -> None:
        sample = (ROOT / "tests" / "fixtures" / "pathology" / "monuseg_sample.xml").read_text(encoding="utf-8")
        polygons = rt.parse_monuseg_xml_annotations(sample)
        self.assertEqual(len(polygons), 2)
        self.assertEqual(polygons[0].id, 101)
        self.assertEqual(polygons[0].vertices[0], (10.0, 10.0))
        self.assertEqual(polygons[1].id, 102)

    def test_load_monuseg_xml_annotations(self) -> None:
        polygons = rt.load_monuseg_xml_annotations(
            ROOT / "tests" / "fixtures" / "pathology" / "monuseg_sample.xml"
        )
        self.assertEqual(len(polygons), 2)

    def test_write_goal139_artifacts(self) -> None:
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            artifacts = rt.write_goal139_artifacts(tmpdir)
            self.assertTrue(artifacts["manifest"].exists())
            self.assertTrue(artifacts["markdown"].exists())
            payload = json.loads(artifacts["manifest"].read_text(encoding="utf-8"))
            keys = {entry["key"] for entry in payload["datasets"]}
            self.assertEqual(keys, {"nuinsseg", "monuseg"})
            self.assertIn("Public datasets", artifacts["markdown"].read_text(encoding="utf-8"))

    def test_download_boundary_descriptions(self) -> None:
        self.assertIn("GiB", rt.describe_download_boundary("nuinsseg"))
        self.assertIn("external", rt.describe_download_boundary("monuseg"))


if __name__ == "__main__":
    unittest.main()
