from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EMBREE_RUNTIME = ROOT / "src/rtdsl/embree_runtime.py"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
REPORT = ROOT / "docs/reports/goal2557_python_columnar_internal_routing_2026-05-23.md"


class Goal2557PythonColumnarInternalRoutingTest(unittest.TestCase):
    def test_prepared_kernel_routing_uses_columnar_internal_names(self) -> None:
        embree_text = EMBREE_RUNTIME.read_text(encoding="utf-8")
        optix_text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("return _prepare_columnar_embree_execution", embree_text)
        self.assertIn("return _prepare_columnar_optix_execution", optix_text)
        self.assertNotIn("return _prepare_db_embree_execution", embree_text)
        self.assertNotIn("return _prepare_db_optix_execution", optix_text)
        self.assertNotIn("def _prepare_db_embree_execution", embree_text)
        self.assertNotIn("def _prepare_db_optix_execution", optix_text)

    def test_low_level_prepared_payload_internals_have_columnar_primary_names(self) -> None:
        embree_text = EMBREE_RUNTIME.read_text(encoding="utf-8")
        optix_text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        for token in (
            "class PreparedEmbreeColumnarExecution",
            "class EmbreePreparedColumnarPayload",
            "EmbreePreparedDbDataset = EmbreePreparedColumnarPayload",
        ):
            with self.subTest(token=token):
                self.assertIn(token, embree_text)
        for token in (
            "class PreparedOptixColumnarExecution",
            "class OptixPreparedColumnarPayload",
            "OptixPreparedDbDataset = OptixPreparedColumnarPayload",
        ):
            with self.subTest(token=token):
                self.assertIn(token, optix_text)

    def test_report_records_remaining_low_level_compatibility_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2557", text)
        self.assertIn("internal Python routing", text)
        self.assertIn("compatibility aliases", text)
        self.assertIn("ctypes layout wrappers remain unchanged", text)


if __name__ == "__main__":
    unittest.main()
