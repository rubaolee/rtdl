from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EMBREE_RUNTIME = ROOT / "src/rtdsl/embree_runtime.py"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
REPORT = ROOT / "docs/reports/goal2559_python_wrapper_columnar_ctypes_usage_2026-05-23.md"


class Goal2559PythonWrapperColumnarCtypesUsageTest(unittest.TestCase):
    def test_embree_and_optix_wrappers_use_columnar_ctypes_aliases_for_common_layouts(self) -> None:
        for path in (EMBREE_RUNTIME, OPTIX_RUNTIME):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("from .oracle_runtime import _RtdlColumnField", text)
                self.assertIn("from .oracle_runtime import _RtdlColumnRowIdRow", text)
                self.assertIn("from .oracle_runtime import _RtdlGroupedCountRow", text)
                self.assertIn("ctypes.POINTER(_RtdlColumnField)", text)
                self.assertIn("ctypes.POINTER(ctypes.POINTER(_RtdlColumnRowIdRow))", text)
                self.assertIn("ctypes.POINTER(ctypes.POINTER(_RtdlGroupedCountRow))", text)

    def test_legacy_import_markers_remain_for_python_compatibility_boundary(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (EMBREE_RUNTIME, OPTIX_RUNTIME))
        for token in (
            "_RtdlDbField",
            "_RtdlDbRowIdRow",
            "_RtdlDbGroupedCountRow",
        ):
            with self.subTest(token=token):
                self.assertIn(token, combined)

    def test_report_records_partial_usage_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2559", text)
        self.assertIn("common ctypes layouts", text)
        self.assertIn("legacy compatibility markers", text)
        self.assertIn("OptiX-only compact-summary layouts remain", text)


if __name__ == "__main__":
    unittest.main()
