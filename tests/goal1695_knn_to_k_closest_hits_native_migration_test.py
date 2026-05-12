from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native"
RUNTIME_FILES = (
    ROOT / "src" / "rtdsl" / "embree_runtime.py",
    ROOT / "src" / "rtdsl" / "optix_runtime.py",
    ROOT / "src" / "rtdsl" / "oracle_runtime.py",
    ROOT / "src" / "rtdsl" / "vulkan_runtime.py",
)
PURITY = ROOT / "src" / "rtdsl" / "python_rtdl_app_purity.py"
REPORT = ROOT / "docs" / "reports" / "goal1695_knn_to_k_closest_hits_native_migration_2026-05-11.md"
GATE = ROOT / "docs" / "release_reports" / "v1_7_app_agnostic_native_gate.md"
GOAL1672 = ROOT / "docs" / "reports" / "goal1672_native_app_leakage_migration_classification_2026-05-10.md"

TERMS = ("db", "pip", "bfs", "robot", "pose", "polygon", "knn", "hausdorff", "jaccard")
LEAKAGE_RE = re.compile(
    r"\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b",
    re.IGNORECASE,
)
FALSE_POSITIVE_CONSTANT_RE = re.compile(r"\bRTDL_DB_[A-Z0-9_]+\b")
RTDL_KNN_ABI_RE = re.compile(r"\brtdl_[A-Za-z0-9_]*knn[A-Za-z0-9_]*\b", re.IGNORECASE)

REMOVED_KNN_SYMBOLS = (
    "rtdl_embree_knn_rows_2d_create",
    "rtdl_embree_knn_rows_2d_run",
    "rtdl_embree_knn_rows_2d_destroy",
    "rtdl_embree_run_knn_rows",
    "rtdl_embree_run_knn_rows_3d",
    "rtdl_optix_run_knn_rows",
    "rtdl_optix_run_knn_rows_3d",
    "rtdl_oracle_run_knn_rows",
    "rtdl_oracle_run_knn_rows_3d",
    "rtdl_oracle_run_bounded_knn_rows",
    "rtdl_oracle_run_bounded_knn_rows_3d",
    "rtdl_oracle_summarize_knn_rows",
    "rtdl_vulkan_run_knn_rows",
    "rtdl_vulkan_run_knn_rows_3d",
)

REPLACEMENT_K_CLOSEST_HITS_SYMBOLS = (
    "rtdl_embree_k_closest_hits_2d_create",
    "rtdl_embree_k_closest_hits_2d_run",
    "rtdl_embree_k_closest_hits_2d_destroy",
    "rtdl_embree_run_k_closest_hits",
    "rtdl_embree_run_k_closest_hits_3d",
    "rtdl_optix_run_k_closest_hits",
    "rtdl_optix_run_k_closest_hits_3d",
    "rtdl_oracle_run_k_closest_hits",
    "rtdl_oracle_run_k_closest_hits_3d",
    "rtdl_oracle_run_bounded_k_closest_hits",
    "rtdl_oracle_run_bounded_k_closest_hits_3d",
    "rtdl_oracle_summarize_k_closest_hits",
    "rtdl_vulkan_run_k_closest_hits",
    "rtdl_vulkan_run_k_closest_hits_3d",
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


class Goal1695KnnToKClosestHitsNativeMigrationTest(unittest.TestCase):
    def test_native_sources_no_longer_export_knn_named_abi(self) -> None:
        text = _native_text()
        for symbol in REMOVED_KNN_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, text)
        self.assertEqual(RTDL_KNN_ABI_RE.findall(text), [])

    def test_native_sources_export_k_closest_hits_replacements(self) -> None:
        text = _native_text()
        for symbol in REPLACEMENT_K_CLOSEST_HITS_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, text)
        self.assertIn("k_closest_hits.comp", text)
        self.assertIn("k_closest_hits3d.comp", text)

    def test_python_compat_names_remain_while_ctypes_bindings_use_new_abi(self) -> None:
        runtime_text = "\n".join(_text(path) for path in RUNTIME_FILES)
        for old_symbol in REMOVED_KNN_SYMBOLS:
            with self.subTest(old_symbol=old_symbol):
                self.assertNotIn(old_symbol, runtime_text)
        for symbol in REPLACEMENT_K_CLOSEST_HITS_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, runtime_text)

        self.assertIn("def prepare_embree_knn_rows_2d(", runtime_text)
        self.assertIn("def _run_knn_rows_embree(", runtime_text)
        self.assertIn("def _call_knn_rows_optix_packed(", runtime_text)
        self.assertIn('"knn_rows"', runtime_text)
        self.assertIn("_RtdlKnnNeighborRow", runtime_text)

    def test_purity_audit_classifies_old_knn_abi_as_app_shaped_and_new_abi_as_generic(self) -> None:
        text = _text(PURITY)
        for fragment in ("_run_knn_rows", "_knn_rows_", "_bounded_knn_rows", "_summarize_knn_rows"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)
        for fragment in (
            "_run_k_closest_hits",
            "_run_bounded_k_closest_hits",
            "_k_closest_hits_2d",
            "_summarize_k_closest_hits",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_strict_native_scan_has_zero_knn_family_after_goal1695(self) -> None:
        text = _native_text()
        strict_occurrences = [match.group(0) for match in LEAKAGE_RE.finditer(text)]
        false_positive_symbols = set(FALSE_POSITIVE_CONSTANT_RE.findall(text))
        false_positive_occurrences = FALSE_POSITIVE_CONSTANT_RE.findall(text)
        strict_symbols = set(strict_occurrences)
        real_symbols = strict_symbols - false_positive_symbols

        self.assertFalse([symbol for symbol in real_symbols if "knn" in symbol.lower()])
        self.assertEqual(len(strict_symbols), 9)
        self.assertEqual(len(strict_occurrences), 14)
        self.assertEqual(len(false_positive_symbols), 9)
        self.assertEqual(len(false_positive_occurrences), 14)
        self.assertEqual(len(real_symbols), 0)

        by_family = Counter(_first_family(symbol) for symbol in real_symbols)
        self.assertEqual(by_family, {})

    def test_reports_and_gate_record_goal1695_boundary(self) -> None:
        report_text = _text(REPORT)
        gate_text = _text(GATE)
        goal1672_text = _text(GOAL1672)
        for phrase in (
            "KNN family is now zero",
            "rtdl_embree_run_k_closest_hits",
            "rtdl_oracle_summarize_k_closest_hits",
            "Python-facing KNN semantics remain in Python",
            "Remaining app-shaped callable/export symbols | 59",
            "no pod was used",
            "RTDL native internals are fully app-agnostic.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("goal1695_knn_to_k_closest_hits_native_migration_2026-05-11.md", gate_text)
        self.assertIn("Goal1695", goal1672_text)


if __name__ == "__main__":
    unittest.main()
