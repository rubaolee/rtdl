from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native"
APPLE_RT_NATIVE = ROOT / "src" / "native" / "apple_rt" / "rtdl_apple_rt_metal_compute.mm"
APPLE_RT_RUNTIME = ROOT / "src" / "rtdsl" / "apple_rt_runtime.py"
PURITY = ROOT / "src" / "rtdsl" / "python_rtdl_app_purity.py"
REPORT = ROOT / "docs" / "reports" / "goal1690_apple_rt_bfs_to_frontier_discover_native_migration_2026-05-11.md"
GATE = ROOT / "docs" / "release_reports" / "v1_7_app_agnostic_native_gate.md"
GOAL1672 = ROOT / "docs" / "reports" / "goal1672_native_app_leakage_migration_classification_2026-05-10.md"

TERMS = ("db", "pip", "bfs", "robot", "pose", "polygon", "knn", "hausdorff", "jaccard")
LEAKAGE_RE = re.compile(
    r"\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b",
    re.IGNORECASE,
)
FALSE_POSITIVE_CONSTANT_RE = re.compile(r"\bRTDL_DB_[A-Z0-9_]+\b")

REMOVED_APPLE_RT_BFS_SYMBOLS = (
    "rtdl_apple_rt_run_bfs_discover_compute",
    "rtdl_bfs_discover",
)

REPLACEMENT_APPLE_RT_FRONTIER_SYMBOLS = (
    "rtdl_apple_rt_run_frontier_discover_compute",
    "rtdl_frontier_discover",
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


class Goal1690AppleRtBfsToFrontierDiscoverMigrationTest(unittest.TestCase):
    def test_apple_rt_native_no_longer_exports_bfs_discover_symbols(self) -> None:
        text = _text(APPLE_RT_NATIVE)
        for symbol in REMOVED_APPLE_RT_BFS_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, text)
        for symbol in REPLACEMENT_APPLE_RT_FRONTIER_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, text)
        self.assertIn('newFunctionWithName:@"rtdl_frontier_discover"', text)

    def test_python_bfs_semantics_are_preserved_while_binding_new_abi(self) -> None:
        runtime = _text(APPLE_RT_RUNTIME)
        self.assertIn("def bfs_discover_apple_rt(", runtime)
        self.assertIn('"bfs_discover"', runtime)
        self.assertIn("library.rtdl_apple_rt_run_frontier_discover_compute.argtypes", runtime)
        self.assertIn("library.rtdl_apple_rt_run_frontier_discover_compute(", runtime)
        self.assertNotIn("library.rtdl_apple_rt_run_bfs_discover_compute", runtime)

    def test_purity_audit_classifies_frontier_discover_as_generic(self) -> None:
        text = _text(PURITY)
        self.assertIn("_run_frontier_discover_compute", text)
        self.assertIn("_run_bfs", text)

    def test_strict_native_scan_has_zero_bfs_family_after_goal1690(self) -> None:
        text = _native_text()
        strict_occurrences = [match.group(0) for match in LEAKAGE_RE.finditer(text)]
        false_positive_symbols = set(FALSE_POSITIVE_CONSTANT_RE.findall(text))
        strict_symbols = set(strict_occurrences)
        real_symbols = strict_symbols - false_positive_symbols

        self.assertFalse([symbol for symbol in real_symbols if "bfs" in symbol.lower()])
        self.assertEqual(len(strict_symbols), 9)
        self.assertEqual(len(strict_occurrences), 14)
        self.assertEqual(len(real_symbols), 0)

        by_family = Counter(_first_family(symbol) for symbol in real_symbols)
        self.assertEqual(by_family, {})

    def test_reports_and_gate_record_goal1690_boundary(self) -> None:
        report_text = _text(REPORT)
        gate_text = _text(GATE)
        goal1672_text = _text(GOAL1672)
        for phrase in (
            "BFS family is now zero",
            "rtdl_apple_rt_run_frontier_discover_compute",
            "rtdl_frontier_discover",
            "Python-facing BFS semantics remain in Python",
            "Remaining app-shaped callable/export symbols | 73",
            "no pod was used",
            "RTDL native internals are fully app-agnostic.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("goal1690_apple_rt_bfs_to_frontier_discover_native_migration_2026-05-11.md", gate_text)
        self.assertIn("Goal1690", goal1672_text)


if __name__ == "__main__":
    unittest.main()
