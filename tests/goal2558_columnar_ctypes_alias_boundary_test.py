from __future__ import annotations

from pathlib import Path
import unittest

from rtdsl import oracle_runtime


ROOT = Path(__file__).resolve().parents[1]
ORACLE_RUNTIME = ROOT / "src/rtdsl/oracle_runtime.py"
REPORT = ROOT / "docs/reports/goal2558_columnar_ctypes_alias_boundary_2026-05-23.md"


class Goal2558ColumnarCtypesAliasBoundaryTest(unittest.TestCase):
    def test_generic_columnar_ctypes_layout_aliases_exist(self) -> None:
        alias_pairs = (
            ("_RtdlColumnField", "_RtdlDbField"),
            ("_RtdlColumnScalar", "_RtdlDbScalar"),
            ("_RtdlColumnClause", "_RtdlDbClause"),
            ("_RtdlColumnRowIdRow", "_RtdlDbRowIdRow"),
            ("_RtdlGroupedCountRow", "_RtdlDbGroupedCountRow"),
            ("_RtdlGroupedSumRow", "_RtdlDbGroupedSumRow"),
        )
        for generic_name, legacy_name in alias_pairs:
            with self.subTest(generic_name=generic_name):
                self.assertIs(getattr(oracle_runtime, generic_name), getattr(oracle_runtime, legacy_name))

    def test_generic_columnar_constant_aliases_exist(self) -> None:
        for generic_name, legacy_name in (
            ("_COLUMN_KIND_INT64", "_DB_KIND_INT64"),
            ("_COLUMN_KIND_FLOAT64", "_DB_KIND_FLOAT64"),
            ("_COLUMN_KIND_BOOL", "_DB_KIND_BOOL"),
            ("_COLUMN_KIND_TEXT", "_DB_KIND_TEXT"),
            ("_COLUMN_OP_EQ", "_DB_OP_EQ"),
            ("_COLUMN_OP_LT", "_DB_OP_LT"),
            ("_COLUMN_OP_LE", "_DB_OP_LE"),
            ("_COLUMN_OP_GT", "_DB_OP_GT"),
            ("_COLUMN_OP_GE", "_DB_OP_GE"),
            ("_COLUMN_OP_BETWEEN", "_DB_OP_BETWEEN"),
        ):
            with self.subTest(generic_name=generic_name):
                self.assertEqual(getattr(oracle_runtime, generic_name), getattr(oracle_runtime, legacy_name))

    def test_generic_columnar_encoder_aliases_exist(self) -> None:
        for generic_name, legacy_name in (
            ("_encode_columnar_scalar", "_encode_db_scalar"),
            ("_encode_columnar_field_kind", "_encode_db_field_kind"),
            ("_encode_columnar_table", "_encode_db_table"),
            ("_encode_columnar_text_fields", "_encode_db_text_fields"),
            ("_encode_columnar_text_clause_values", "_encode_db_text_clause_values"),
            ("_decode_columnar_group_key", "_decode_db_group_key"),
            ("_encode_columnar_clause", "_encode_db_clause"),
            ("_encode_columnar_clauses", "_encode_db_clauses"),
        ):
            with self.subTest(generic_name=generic_name):
                self.assertIs(getattr(oracle_runtime, generic_name), getattr(oracle_runtime, legacy_name))

    def test_oracle_runtime_marks_aliases_as_compatibility_layer(self) -> None:
        text = ORACLE_RUNTIME.read_text(encoding="utf-8-sig")
        self.assertIn("_RtdlColumnField = _RtdlDbField", text)
        self.assertIn("_encode_columnar_clauses = _encode_db_clauses", text)

    def test_report_records_alias_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2558", text)
        self.assertIn("generic columnar aliases", text)
        self.assertIn("legacy DB-shaped names remain", text)
        self.assertIn("No native symbol is changed", text)


if __name__ == "__main__":
    unittest.main()
