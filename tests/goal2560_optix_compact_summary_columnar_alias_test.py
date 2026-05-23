from __future__ import annotations

from pathlib import Path
import unittest

from rtdsl import optix_runtime


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
REPORT = ROOT / "docs/reports/goal2560_optix_compact_summary_columnar_alias_2026-05-23.md"


class Goal2560OptixCompactSummaryColumnarAliasTest(unittest.TestCase):
    def test_optix_only_grouped_row_aliases_exist(self) -> None:
        for generic_name, legacy_name in (
            ("_RtdlGroupedSumRow", "_RtdlDbGroupedSumRow"),
            ("_RtdlGroupedSumCountRow", "_RtdlDbGroupedSumCountRow"),
            ("_RtdlGroupedStatsRow", "_RtdlDbGroupedStatsRow"),
        ):
            with self.subTest(generic_name=generic_name):
                self.assertIs(getattr(optix_runtime, generic_name), getattr(optix_runtime, legacy_name))

    def test_compact_summary_columnar_aliases_exist(self) -> None:
        self.assertIs(
            optix_runtime._RtdlColumnCompactSummaryRequest,
            optix_runtime._RtdlDbCompactSummaryRequest,
        )
        self.assertIs(
            optix_runtime._RtdlColumnCompactSummaryResult,
            optix_runtime._RtdlDbCompactSummaryResult,
        )
        self.assertEqual(
            optix_runtime._COLUMN_COMPACT_SUMMARY_OP_SCAN_COUNT,
            optix_runtime._DB_COMPACT_SUMMARY_OP_SCAN_COUNT,
        )
        self.assertEqual(
            optix_runtime._COLUMN_COMPACT_SUMMARY_OP_GROUPED_COUNT,
            optix_runtime._DB_COMPACT_SUMMARY_OP_GROUPED_COUNT,
        )
        self.assertEqual(
            optix_runtime._COLUMN_COMPACT_SUMMARY_OP_GROUPED_SUM,
            optix_runtime._DB_COMPACT_SUMMARY_OP_GROUPED_SUM,
        )

    def test_legacy_compact_summary_class_definitions_remain_for_historical_tests(self) -> None:
        text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("class _RtdlDbCompactSummaryRequest", text)
        self.assertIn("class _RtdlDbCompactSummaryResult", text)
        self.assertIn("_RtdlColumnCompactSummaryRequest = _RtdlDbCompactSummaryRequest", text)
        self.assertIn("_RtdlColumnCompactSummaryResult = _RtdlDbCompactSummaryResult", text)

    def test_active_compact_summary_path_uses_columnar_aliases(self) -> None:
        text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("ctypes.POINTER(_RtdlColumnCompactSummaryRequest)", text)
        self.assertIn("ctypes.POINTER(ctypes.POINTER(_RtdlColumnCompactSummaryResult))", text)
        self.assertIn("ctypes.POINTER(_RtdlColumnCompactSummaryResult)", text)
        self.assertIn("_COLUMN_COMPACT_SUMMARY_OP_SCAN_COUNT", text)
        self.assertIn("_COLUMN_COMPACT_SUMMARY_OP_GROUPED_COUNT", text)
        self.assertIn("_COLUMN_COMPACT_SUMMARY_OP_GROUPED_SUM", text)
        self.assertNotIn("ctypes.POINTER(_RtdlDbCompactSummaryRequest)", text)
        self.assertNotIn("ctypes.POINTER(ctypes.POINTER(_RtdlDbCompactSummaryResult))", text)
        self.assertNotIn("ctypes.POINTER(_RtdlDbCompactSummaryResult)", text)
        self.assertNotIn("_DB_COMPACT_SUMMARY_OP_SCAN_COUNT,", text)
        self.assertNotIn("_DB_COMPACT_SUMMARY_OP_GROUPED_COUNT,", text)
        self.assertNotIn("_DB_COMPACT_SUMMARY_OP_GROUPED_SUM,", text)

    def test_active_optix_only_grouped_row_paths_use_generic_aliases(self) -> None:
        text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("ctypes.POINTER(_RtdlGroupedSumRow)", text)
        self.assertIn("ctypes.POINTER(ctypes.POINTER(_RtdlGroupedSumRow))", text)
        self.assertIn("ctypes.POINTER(ctypes.POINTER(_RtdlGroupedSumCountRow))", text)
        self.assertIn("ctypes.POINTER(ctypes.POINTER(_RtdlGroupedStatsRow))", text)
        self.assertNotIn("ctypes.POINTER(_RtdlDbGroupedSumRow)", text)
        self.assertNotIn("ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedSumRow))", text)
        self.assertNotIn("ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedSumCountRow))", text)
        self.assertNotIn("ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedStatsRow))", text)

    def test_report_records_compact_summary_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2560", text)
        self.assertIn("OptiX-only compact-summary aliases", text)
        self.assertIn("active python wrapper\npaths now use the generic aliases", text.lower())
        self.assertIn("legacy class definitions remain", text)
        self.assertIn("No native ABI changes", text)


if __name__ == "__main__":
    unittest.main()
