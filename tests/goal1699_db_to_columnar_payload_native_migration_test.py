from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native"
RUNTIME_FILES = (
    ROOT / "src" / "rtdsl" / "apple_rt_runtime.py",
    ROOT / "src" / "rtdsl" / "embree_runtime.py",
    ROOT / "src" / "rtdsl" / "hiprt_runtime.py",
    ROOT / "src" / "rtdsl" / "optix_runtime.py",
    ROOT / "src" / "rtdsl" / "vulkan_runtime.py",
)
PURITY = ROOT / "src" / "rtdsl" / "python_rtdl_app_purity.py"
REPORT = ROOT / "docs" / "reports" / "goal1699_db_to_columnar_payload_native_migration_2026-05-11.md"
GATE = ROOT / "docs" / "release_reports" / "v1_7_app_agnostic_native_gate.md"
GOAL1672 = ROOT / "docs" / "reports" / "goal1672_native_app_leakage_migration_classification_2026-05-10.md"
GOAL1680 = ROOT / "docs" / "reports" / "goal1680_current_native_app_leakage_gap_2026-05-10.md"

TERMS = ("db", "pip", "bfs", "robot", "pose", "polygon", "knn", "hausdorff", "jaccard")
LEAKAGE_RE = re.compile(
    r"\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b",
    re.IGNORECASE,
)
FALSE_POSITIVE_CONSTANT_RE = re.compile(r"\bRTDL_DB_[A-Z0-9_]+\b")
LOWERCASE_DB_ABI_RE = re.compile(r"\brtdl_[a-z0-9_]*db[a-z0-9_]*\b")

REMOVED_DB_SYMBOLS = (
    "rtdl_apple_rt_run_db_conjunctive_scan_numeric_compute",
    "rtdl_db_conjunctive_scan",
    "rtdl_db_match",
    "rtdl_hiprt_prepare_db_table",
    "rtdl_hiprt_destroy_prepared_db_table",
    "rtdl_hiprt_db_match_prepared",
    "rtdl_hiprt_db_match",
    "rtdl_embree_db_dataset_create",
    "rtdl_embree_db_dataset_create_columnar",
    "rtdl_embree_db_dataset_destroy",
    "rtdl_embree_db_dataset_conjunctive_scan",
    "rtdl_embree_db_dataset_grouped_count",
    "rtdl_embree_db_dataset_grouped_sum",
    "rtdl_optix_db_dataset_create",
    "rtdl_optix_db_dataset_create_columnar",
    "rtdl_optix_db_dataset_destroy",
    "rtdl_optix_db_dataset_conjunctive_scan",
    "rtdl_optix_db_dataset_conjunctive_scan_count",
    "rtdl_optix_db_dataset_grouped_count",
    "rtdl_optix_db_dataset_grouped_sum",
    "rtdl_optix_db_dataset_compact_summary_batch",
    "rtdl_optix_db_get_last_phase_timings",
    "rtdl_optix_fill_db_compact_summary_phase",
    "rtdl_optix_db_compact_summary_results_destroy",
    "rtdl_vulkan_db_dataset_create",
    "rtdl_vulkan_db_dataset_create_columnar",
    "rtdl_vulkan_db_dataset_destroy",
    "rtdl_vulkan_db_dataset_conjunctive_scan",
    "rtdl_vulkan_db_dataset_grouped_count",
    "rtdl_vulkan_db_dataset_grouped_sum",
)

REPLACEMENT_COLUMNAR_SYMBOLS = (
    "rtdl_apple_rt_run_columnar_multi_predicate_scan_numeric_compute",
    "rtdl_multi_predicate_scan",
    "rtdl_predicate_match",
    "rtdl_hiprt_prepare_columnar_payload",
    "rtdl_hiprt_destroy_prepared_columnar_payload",
    "rtdl_hiprt_predicate_match_prepared",
    "rtdl_hiprt_predicate_match",
    "rtdl_embree_columnar_payload_create",
    "rtdl_embree_columnar_payload_create_from_columns",
    "rtdl_embree_columnar_payload_destroy",
    "rtdl_embree_columnar_payload_multi_predicate_scan",
    "rtdl_embree_columnar_payload_grouped_reduction_count",
    "rtdl_embree_columnar_payload_grouped_reduction_sum",
    "rtdl_optix_columnar_payload_create",
    "rtdl_optix_columnar_payload_create_from_columns",
    "rtdl_optix_columnar_payload_destroy",
    "rtdl_optix_columnar_payload_multi_predicate_scan",
    "rtdl_optix_columnar_payload_multi_predicate_scan_count",
    "rtdl_optix_columnar_payload_grouped_reduction_count",
    "rtdl_optix_columnar_payload_grouped_reduction_sum",
    "rtdl_optix_columnar_payload_compact_summary_batch",
    "rtdl_optix_columnar_payload_get_last_phase_timings",
    "rtdl_optix_fill_columnar_compact_summary_phase",
    "rtdl_optix_columnar_compact_summary_results_destroy",
    "rtdl_vulkan_columnar_payload_create",
    "rtdl_vulkan_columnar_payload_create_from_columns",
    "rtdl_vulkan_columnar_payload_destroy",
    "rtdl_vulkan_columnar_payload_multi_predicate_scan",
    "rtdl_vulkan_columnar_payload_grouped_reduction_count",
    "rtdl_vulkan_columnar_payload_grouped_reduction_sum",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _native_text() -> str:
    chunks: list[str] = []
    for path in NATIVE.rglob("*"):
        if path.suffix.lower() in {".cpp", ".h", ".cu", ".mm"}:
            chunks.append(_text(path))
    return "\n".join(chunks)


def _first_family(symbol: str) -> str:
    lowered = symbol.lower()
    for term in TERMS:
        if term in lowered:
            return term
    raise AssertionError(f"unclassified leakage symbol: {symbol}")


class Goal1699DbToColumnarPayloadNativeMigrationTest(unittest.TestCase):
    def test_native_sources_no_longer_export_lowercase_db_named_abi(self) -> None:
        text = _native_text()
        for symbol in REMOVED_DB_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, text)
        self.assertEqual(LOWERCASE_DB_ABI_RE.findall(text), [])

    def test_native_sources_export_columnar_payload_replacements(self) -> None:
        text = _native_text()
        for symbol in REPLACEMENT_COLUMNAR_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, text)

    def test_python_compat_names_remain_while_ctypes_bindings_use_new_abi(self) -> None:
        runtime_text = "\n".join(_text(path) for path in RUNTIME_FILES)
        for old_symbol in REMOVED_DB_SYMBOLS:
            with self.subTest(old_symbol=old_symbol):
                self.assertNotIn(old_symbol, runtime_text)
        for symbol in REPLACEMENT_COLUMNAR_SYMBOLS:
            if symbol in {
                "rtdl_multi_predicate_scan",
                "rtdl_predicate_match",
                "rtdl_hiprt_predicate_match_prepared",
                "rtdl_hiprt_predicate_match",
                "rtdl_optix_fill_columnar_compact_summary_phase",
            }:
                continue
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, runtime_text)

        for compat_name in (
            "conjunctive_scan",
            "grouped_count",
            "grouped_sum",
            "prepare_embree_db_dataset",
            "PreparedEmbreeDbDataset",
            "PreparedHiprtDbTable",
            "PreparedOptixDbDataset",
            "PreparedVulkanDbDataset",
            "_RtdlDbField",
            "_RtdlDbGroupedSumRow",
        ):
            with self.subTest(compat_name=compat_name):
                self.assertIn(compat_name, runtime_text)

    def test_purity_audit_classifies_old_db_abi_as_app_shaped_and_new_abi_as_generic(self) -> None:
        text = _text(PURITY)
        for fragment in (
            "_db_dataset_",
            "_db_table",
            "_db_match",
            "_db_conjunctive_scan",
            "_run_db",
            "_db_compact_summary",
            "_fill_db_compact_summary",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)
        for fragment in (
            "_columnar_payload_",
            "_prepare_columnar_payload",
            "_destroy_prepared_columnar_payload",
            "_multi_predicate_scan",
            "_predicate_match",
            "_grouped_reduction_",
            "_columnar_compact_summary_",
            "_fill_columnar_compact_summary_",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_strict_native_scan_has_zero_real_app_shaped_symbols_after_goal1699(self) -> None:
        text = _native_text()
        strict_occurrences = [match.group(0) for match in LEAKAGE_RE.finditer(text)]
        false_positive_symbols = set(FALSE_POSITIVE_CONSTANT_RE.findall(text))
        false_positive_occurrences = FALSE_POSITIVE_CONSTANT_RE.findall(text)
        strict_symbols = set(strict_occurrences)
        real_symbols = strict_symbols - false_positive_symbols

        self.assertEqual(strict_symbols, false_positive_symbols)
        self.assertEqual(strict_occurrences, false_positive_occurrences)
        self.assertEqual(len(real_symbols), 0)

        by_family = Counter(_first_family(symbol) for symbol in real_symbols)
        self.assertEqual(by_family, {})

    def test_reports_and_gate_record_goal1699_boundary(self) -> None:
        report_text = _text(REPORT)
        goal1680_text = _text(GOAL1680)
        gate_text = _text(GATE)
        goal1672_text = _text(GOAL1672)
        for phrase in (
            "DB family is now zero",
            "rtdl_embree_columnar_payload_multi_predicate_scan",
            "rtdl_optix_columnar_payload_compact_summary_batch",
            "Python-facing database semantics remain in Python",
            "Remaining app-shaped callable/export symbols | 0",
            "No pod was used",
            "RTDL native internals are fully app-agnostic.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("No real app-shaped native callable/export families remain", goal1680_text)
        self.assertIn("goal1699_db_to_columnar_payload_native_migration_2026-05-11.md", gate_text)
        self.assertIn("Goal1699", goal1672_text)


if __name__ == "__main__":
    unittest.main()
