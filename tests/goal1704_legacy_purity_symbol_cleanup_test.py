from __future__ import annotations

from pathlib import Path
import re
import unittest

from src.rtdsl.python_rtdl_app_purity import native_symbol_purity_audit


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native"
PURITY = ROOT / "src" / "rtdsl" / "python_rtdl_app_purity.py"
REPORT = ROOT / "docs" / "reports" / "goal1704_legacy_purity_symbol_cleanup_2026-05-11.md"

REMOVED_LEGACY_SYMBOLS = (
    "rtdl_embree_run_lsi",
    "rtdl_optix_run_lsi",
    "rtdl_embree_run_overlay",
    "rtdl_optix_run_overlay",
    "rtdl_embree_run_triangle_probe",
    "rtdl_optix_run_triangle_probe",
)

GENERIC_REPLACEMENT_SYMBOLS = (
    "rtdl_embree_run_segment_pair_intersection",
    "rtdl_optix_run_segment_pair_intersection",
    "rtdl_embree_run_shape_pair_relation_flags",
    "rtdl_optix_run_shape_pair_relation_flags",
    "rtdl_embree_run_edge_neighbor_intersection_packet",
    "rtdl_optix_run_edge_neighbor_intersection_packet",
)

STRICT_RE = re.compile(
    r"\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b",
    re.IGNORECASE,
)
FALSE_POSITIVE_CONSTANT_RE = re.compile(r"\bRTDL_DB_[A-Z0-9_]+\b")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _native_text() -> str:
    return "\n".join(
        _text(path)
        for path in NATIVE.rglob("*")
        if path.suffix.lower() in {".cpp", ".h", ".cu", ".mm"}
    )


class Goal1704LegacyPuritySymbolCleanupTest(unittest.TestCase):
    def test_six_legacy_purity_symbols_are_absent_from_native_and_runtime_sources(self) -> None:
        text = _native_text()
        runtime_text = "\n".join(
            _text(path)
            for path in (ROOT / "src" / "rtdsl").glob("*_runtime.py")
        )
        combined = text + "\n" + runtime_text
        for symbol in REMOVED_LEGACY_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, combined)

    def test_generic_replacements_are_present(self) -> None:
        text = _native_text()
        runtime_text = "\n".join(
            _text(path)
            for path in (ROOT / "src" / "rtdsl").glob("*_runtime.py")
        )
        combined = text + "\n" + runtime_text
        for symbol in GENERIC_REPLACEMENT_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, combined)

    def test_purity_audit_has_no_legacy_engine_customized_native_symbols(self) -> None:
        audit = native_symbol_purity_audit(repo_root=ROOT)
        self.assertEqual(tuple(audit["legacy_engine_customized_symbols"]), ())
        self.assertFalse(audit["pure_native_app_contract_ready"])

    def test_purity_classifier_keeps_old_fragments_blocked_and_new_fragments_generic(self) -> None:
        text = _text(PURITY)
        for fragment in ("_run_lsi", "_run_overlay", "_run_triangle_probe"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)
        for fragment in (
            "_run_segment_pair_intersection",
            "_run_shape_pair_relation_flags",
            "_run_edge_neighbor_intersection_packet",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_strict_tracked_family_scan_remains_9_14_0(self) -> None:
        text = _native_text()
        strict_occurrences = [match.group(0) for match in STRICT_RE.finditer(text)]
        false_positive_occurrences = FALSE_POSITIVE_CONSTANT_RE.findall(text)
        strict_symbols = set(strict_occurrences)
        false_positive_symbols = set(false_positive_occurrences)
        real_symbols = strict_symbols - false_positive_symbols

        self.assertEqual(len(strict_symbols), 9)
        self.assertEqual(len(strict_occurrences), 14)
        self.assertEqual(len(false_positive_symbols), 9)
        self.assertEqual(len(false_positive_occurrences), 14)
        self.assertEqual(real_symbols, set())

    def test_report_records_boundary(self) -> None:
        text = _text(REPORT)
        for phrase in (
            "six legacy purity symbols are now generic",
            "strict tracked-family scan remains `9/14/0`",
            "table` and `column` expanded-term findings",
            "RTDL native internals are fully app-agnostic.",
            "needs-more-evidence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
