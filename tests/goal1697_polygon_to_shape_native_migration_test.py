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
    ROOT / "src" / "rtdsl" / "oracle_runtime.py",
    ROOT / "src" / "rtdsl" / "vulkan_runtime.py",
)
PURITY = ROOT / "src" / "rtdsl" / "python_rtdl_app_purity.py"
REPORT = ROOT / "docs" / "reports" / "goal1697_polygon_to_shape_native_migration_2026-05-11.md"
GATE = ROOT / "docs" / "release_reports" / "v1_7_app_agnostic_native_gate.md"
GOAL1672 = ROOT / "docs" / "reports" / "goal1672_native_app_leakage_migration_classification_2026-05-10.md"

TERMS = ("db", "pip", "bfs", "robot", "pose", "polygon", "knn", "hausdorff", "jaccard")
LEAKAGE_RE = re.compile(
    r"\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b",
    re.IGNORECASE,
)
FALSE_POSITIVE_CONSTANT_RE = re.compile(r"\bRTDL_DB_[A-Z0-9_]+\b")
RTDL_POLYGON_ABI_RE = re.compile(r"\brtdl_[A-Za-z0-9_]*polygon[A-Za-z0-9_]*\b", re.IGNORECASE)

REMOVED_POLYGON_SYMBOLS = (
    "rtdl_apple_rt_run_point_polygon_candidates_2d",
    "rtdl_apple_rt_run_segment_polygon_candidates_2d",
    "rtdl_embree_run_segment_polygon_hitcount",
    "rtdl_embree_run_segment_polygon_anyhit_rows",
    "rtdl_embree_collect_polygon_pair_candidates_bounded",
    "rtdl_hiprt_run_segment_polygon_hitcount",
    "rtdl_hiprt_run_segment_polygon_anyhit_rows",
    "rtdl_hiprt_segment_polygon_2d",
    "rtdl_optix_run_segment_polygon_hitcount",
    "rtdl_optix_prepare_segment_polygon_hitcount_2d",
    "rtdl_optix_run_prepared_segment_polygon_hitcount_2d",
    "rtdl_optix_count_prepared_segment_polygon_hitcount_at_least_2d",
    "rtdl_optix_aggregate_prepared_segment_polygon_hitcount_2d",
    "rtdl_optix_destroy_prepared_segment_polygon_hitcount_2d",
    "rtdl_optix_run_segment_polygon_anyhit_rows",
    "rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded",
    "rtdl_optix_prepare_segment_polygon_anyhit_rows_2d",
    "rtdl_optix_run_prepared_segment_polygon_anyhit_rows_2d",
    "rtdl_optix_destroy_prepared_segment_polygon_anyhit_rows_2d",
    "rtdl_optix_collect_polygon_pair_candidates_bounded",
    "rtdl_oracle_run_segment_polygon_hitcount",
    "rtdl_oracle_run_segment_polygon_anyhit_rows",
    "rtdl_oracle_run_polygon_pair_overlap_area_rows",
    "rtdl_oracle_run_polygon_set_jaccard",
    "rtdl_oracle_refine_polygon_pair_overlap_area_rows_for_pairs",
    "rtdl_oracle_refine_polygon_set_jaccard_for_pairs",
    "rtdl_native_reduce_polygon_pair_exact_area_summary",
    "rtdl_vulkan_run_segment_polygon_hitcount",
    "rtdl_vulkan_run_segment_polygon_anyhit_rows",
)

REPLACEMENT_SHAPE_SYMBOLS = (
    "rtdl_apple_rt_run_point_shape_candidates_2d",
    "rtdl_apple_rt_run_segment_shape_candidates_2d",
    "rtdl_embree_run_segment_shape_hitcount",
    "rtdl_embree_run_segment_shape_anyhit_rows",
    "rtdl_embree_collect_shape_pair_candidates_bounded",
    "rtdl_hiprt_run_segment_shape_hitcount",
    "rtdl_hiprt_run_segment_shape_anyhit_rows",
    "rtdl_hiprt_segment_shape_2d",
    "rtdl_optix_run_segment_shape_hitcount",
    "rtdl_optix_prepare_segment_shape_hitcount_2d",
    "rtdl_optix_run_prepared_segment_shape_hitcount_2d",
    "rtdl_optix_count_prepared_segment_shape_hitcount_at_least_2d",
    "rtdl_optix_aggregate_prepared_segment_shape_hitcount_2d",
    "rtdl_optix_destroy_prepared_segment_shape_hitcount_2d",
    "rtdl_optix_run_segment_shape_anyhit_rows",
    "rtdl_optix_run_segment_shape_anyhit_rows_native_bounded",
    "rtdl_optix_prepare_segment_shape_anyhit_rows_2d",
    "rtdl_optix_run_prepared_segment_shape_anyhit_rows_2d",
    "rtdl_optix_destroy_prepared_segment_shape_anyhit_rows_2d",
    "rtdl_optix_collect_shape_pair_candidates_bounded",
    "rtdl_oracle_run_segment_shape_hitcount",
    "rtdl_oracle_run_segment_shape_anyhit_rows",
    "rtdl_oracle_run_shape_pair_overlap_area_rows",
    "rtdl_oracle_run_shape_set_overlap_ratio",
    "rtdl_oracle_refine_shape_pair_overlap_area_rows_for_pairs",
    "rtdl_oracle_refine_shape_set_overlap_ratio_for_pairs",
    "rtdl_native_reduce_shape_pair_exact_area_summary",
    "rtdl_vulkan_run_segment_shape_hitcount",
    "rtdl_vulkan_run_segment_shape_anyhit_rows",
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


class Goal1697PolygonToShapeNativeMigrationTest(unittest.TestCase):
    def test_native_sources_no_longer_export_polygon_named_abi(self) -> None:
        text = _native_text()
        for symbol in REMOVED_POLYGON_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, text)
        self.assertEqual(RTDL_POLYGON_ABI_RE.findall(text), [])

    def test_native_sources_export_shape_replacements(self) -> None:
        text = _native_text()
        for symbol in REPLACEMENT_SHAPE_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, text)

    def test_python_compat_names_remain_while_ctypes_bindings_use_new_abi(self) -> None:
        runtime_text = "\n".join(_text(path) for path in RUNTIME_FILES)
        for old_symbol in REMOVED_POLYGON_SYMBOLS:
            with self.subTest(old_symbol=old_symbol):
                self.assertNotIn(old_symbol, runtime_text)
        runtime_replacement_symbols = tuple(
            symbol for symbol in REPLACEMENT_SHAPE_SYMBOLS if symbol != "rtdl_hiprt_segment_shape_2d"
        )
        for symbol in runtime_replacement_symbols:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, runtime_text)

        for compat_name in (
            '"segment_polygon_hitcount"',
            '"segment_polygon_anyhit_rows"',
            '"polygon_pair_overlap_area_rows"',
            '"polygon_set_jaccard"',
            "def segment_polygon_candidates_apple_rt(",
            "def collect_polygon_pair_candidates_bounded_embree(",
            "_RtdlSegmentPolygonHitCountRow",
            "_RtdlPolygonPairCandidate",
        ):
            with self.subTest(compat_name=compat_name):
                self.assertIn(compat_name, runtime_text)

    def test_purity_audit_classifies_old_polygon_abi_as_app_shaped_and_new_abi_as_generic(self) -> None:
        text = _text(PURITY)
        for fragment in ("_segment_polygon_", "_point_polygon_", "_polygon_pair_", "_polygon_set_jaccard"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)
        for fragment in (
            "_segment_shape_",
            "_point_shape_",
            "_shape_pair_",
            "_shape_set_overlap_ratio",
            "_reduce_shape_pair_exact_area_summary",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_strict_native_scan_has_zero_polygon_family_after_goal1697(self) -> None:
        text = _native_text()
        strict_occurrences = [match.group(0) for match in LEAKAGE_RE.finditer(text)]
        false_positive_symbols = set(FALSE_POSITIVE_CONSTANT_RE.findall(text))
        false_positive_occurrences = FALSE_POSITIVE_CONSTANT_RE.findall(text)
        strict_symbols = set(strict_occurrences)
        real_symbols = strict_symbols - false_positive_symbols

        self.assertFalse([symbol for symbol in real_symbols if "polygon" in symbol.lower()])
        self.assertEqual(len(strict_symbols), 9)
        self.assertEqual(len(strict_occurrences), 14)
        self.assertEqual(len(false_positive_symbols), 9)
        self.assertEqual(len(false_positive_occurrences), 14)
        self.assertEqual(len(real_symbols), 0)

        by_family = Counter(_first_family(symbol) for symbol in real_symbols)
        self.assertEqual(by_family, {})

    def test_reports_and_gate_record_goal1697_boundary(self) -> None:
        report_text = _text(REPORT)
        gate_text = _text(GATE)
        goal1672_text = _text(GOAL1672)
        for phrase in (
            "Polygon family is now zero",
            "rtdl_embree_run_segment_shape_hitcount",
            "rtdl_oracle_run_shape_set_overlap_ratio",
            "Python-facing polygon semantics remain in Python",
            "Remaining app-shaped callable/export symbols | 30",
            "no pod was used",
            "RTDL native internals are fully app-agnostic.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("goal1697_polygon_to_shape_native_migration_2026-05-11.md", gate_text)
        self.assertIn("Goal1697", goal1672_text)


if __name__ == "__main__":
    unittest.main()
