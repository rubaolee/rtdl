from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
EMBREE_RUNTIME = ROOT / "src/rtdsl/embree_runtime.py"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
REPORT = ROOT / "docs/reports/goal2556_python_columnar_public_api_boundary_2026-05-23.md"


class Goal2556PythonColumnarPublicApiBoundaryTest(unittest.TestCase):
    def test_generic_columnar_payload_api_is_public_for_embree_and_optix(self) -> None:
        for name in (
            "PreparedEmbreeColumnarPayload",
            "PreparedOptixColumnarPayload",
            "prepare_embree_columnar_payload",
            "prepare_optix_columnar_payload",
        ):
            with self.subTest(name=name):
                self.assertTrue(hasattr(rt, name))
                self.assertIn(name, rt.__all__)

    def test_legacy_db_dataset_api_remains_available_as_compatibility_surface(self) -> None:
        self.assertTrue(issubclass(rt.PreparedEmbreeColumnarPayload, rt.PreparedEmbreeDbDataset))
        self.assertTrue(issubclass(rt.PreparedOptixColumnarPayload, rt.PreparedOptixDbDataset))
        for name in (
            "PreparedEmbreeDbDataset",
            "PreparedOptixDbDataset",
            "prepare_embree_db_dataset",
            "prepare_optix_db_dataset",
        ):
            with self.subTest(name=name):
                self.assertTrue(hasattr(rt, name))
                self.assertIn(name, rt.__all__)

    def test_direct_columnar_record_set_helpers_route_through_generic_names(self) -> None:
        embree_text = EMBREE_RUNTIME.read_text(encoding="utf-8")
        optix_text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("return PreparedEmbreeColumnarPayload.from_columnar_record_set", embree_text)
        self.assertIn("return PreparedOptixColumnarPayload.from_columnar_record_set", optix_text)
        self.assertNotIn("return PreparedEmbreeDbDataset.from_columnar_record_set", embree_text)
        self.assertNotIn("return PreparedOptixDbDataset.from_columnar_record_set", optix_text)

    def test_report_records_compatibility_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2556", text)
        self.assertIn("generic Python public API", text)
        self.assertIn("legacy DB names remain compatibility aliases", text)
        self.assertIn("No native symbol is changed", text)


if __name__ == "__main__":
    unittest.main()
