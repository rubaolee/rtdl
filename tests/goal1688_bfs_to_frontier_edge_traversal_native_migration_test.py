from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native"
NATIVE_BFS_FILES = (
    ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp",
    ROOT / "src" / "native" / "embree" / "rtdl_embree_prelude.h",
    ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp",
    ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_core.cpp",
    ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp",
    ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h",
    ROOT / "src" / "native" / "oracle" / "rtdl_oracle_abi.h",
    ROOT / "src" / "native" / "oracle" / "rtdl_oracle_api.cpp",
    ROOT / "src" / "native" / "vulkan" / "rtdl_vulkan_api.cpp",
    ROOT / "src" / "native" / "vulkan" / "rtdl_vulkan_prelude.h",
)
REPORT = ROOT / "docs" / "reports" / "goal1688_bfs_to_frontier_edge_traversal_native_migration_2026-05-11.md"
GATE = ROOT / "docs" / "release_reports" / "v1_7_app_agnostic_native_gate.md"
GOAL1672 = ROOT / "docs" / "reports" / "goal1672_native_app_leakage_migration_classification_2026-05-10.md"

LEAKAGE_RE = re.compile(
    r"\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b",
    re.IGNORECASE,
)
FALSE_POSITIVE_CONSTANT_RE = re.compile(r"\bRTDL_DB_[A-Z0-9_]+\b")

REMOVED_BFS_SYMBOLS = (
    "rtdl_embree_run_bfs_expand",
    "rtdl_hiprt_run_bfs_expand",
    "rtdl_hiprt_run_prepared_bfs_expand",
    "rtdl_hiprt_bfs_expand",
    "rtdl_optix_run_bfs_expand",
    "rtdl_oracle_run_bfs_expand",
    "rtdl_oracle_summarize_bfs_rows",
    "rtdl_vulkan_run_bfs_expand",
)

REPLACEMENT_BFS_SYMBOLS = (
    "rtdl_embree_run_frontier_edge_traversal_packet",
    "rtdl_hiprt_run_frontier_edge_traversal_packet",
    "rtdl_hiprt_run_prepared_frontier_edge_traversal_packet",
    "rtdl_hiprt_frontier_edge_traversal_packet",
    "rtdl_optix_run_frontier_edge_traversal_packet",
    "rtdl_oracle_run_frontier_edge_traversal_packet",
    "rtdl_oracle_summarize_frontier_traversal_rows",
    "rtdl_vulkan_run_frontier_edge_traversal_packet",
)

GOAL1688_DEFERRED_BFS_SYMBOLS = (
    "rtdl_apple_rt_run_bfs_discover_compute",
    "rtdl_bfs_discover",
)

GOAL1690_REPLACEMENT_SYMBOLS = (
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


class Goal1688BfsToFrontierEdgeTraversalNativeMigrationTest(unittest.TestCase):
    def test_migrated_bfs_native_files_no_longer_export_bfs_named_callables(self) -> None:
        for path in NATIVE_BFS_FILES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                for symbol in REMOVED_BFS_SYMBOLS:
                    with self.subTest(symbol=symbol):
                        self.assertNotIn(symbol, text)

    def test_native_exports_replacement_frontier_edge_traversal_symbols(self) -> None:
        combined = _native_text()
        for symbol in REPLACEMENT_BFS_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, combined)

    def test_deferred_apple_rt_bfs_symbols_were_completed_by_goal1690(self) -> None:
        combined = _native_text()
        for symbol in GOAL1688_DEFERRED_BFS_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, combined)
        for symbol in GOAL1690_REPLACEMENT_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, combined)

    def test_strict_native_scan_reduces_bfs_family_to_apple_rt_remainder(self) -> None:
        text = _native_text()
        strict_occurrences = [match.group(0) for match in LEAKAGE_RE.finditer(text)]
        false_positive_symbols = set(FALSE_POSITIVE_CONSTANT_RE.findall(text))
        strict_symbols = set(strict_occurrences)
        real_symbols = strict_symbols - false_positive_symbols

        bfs_symbols = sorted(s for s in real_symbols if "bfs" in s.lower())
        self.assertEqual(bfs_symbols, [])

        by_family: Counter[str] = Counter()
        for symbol in real_symbols:
            lowered = symbol.lower()
            for term in ("db", "pip", "bfs", "robot", "pose", "polygon", "knn", "hausdorff", "jaccard"):
                if term in lowered:
                    by_family[term] += 1
                    break
        self.assertEqual(by_family["bfs"], 0)
        self.assertEqual(by_family["db"], 0)
        self.assertEqual(by_family["polygon"], 0)
        self.assertEqual(by_family["knn"], 0)
        self.assertNotIn("pip", by_family)
        self.assertNotIn("hausdorff", by_family)
        self.assertNotIn("pose", by_family)

        self.assertEqual(len(strict_symbols), 9)
        self.assertEqual(len(strict_occurrences), 14)
        self.assertEqual(len(real_symbols), 0)

    def test_report_records_narrow_slice_boundary_and_no_pod_claim(self) -> None:
        report_text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Narrow-Slice Scope",
            "Apple RT discover variants",
            "deferred",
            "This is a local source migration only",
            "no pod was used",
            "broader app-agnostic gate still fails",
            "Remaining app-shaped callable/export symbols | 75",
            "RTDL native internals are fully app-agnostic.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)

    def test_gate_links_goal1688_report(self) -> None:
        gate_text = GATE.read_text(encoding="utf-8")
        self.assertIn(
            "goal1688_bfs_to_frontier_edge_traversal_native_migration_2026-05-11.md",
            gate_text,
        )

    def test_goal1672_records_goal1688_followup(self) -> None:
        goal1672_text = GOAL1672.read_text(encoding="utf-8")
        self.assertIn("Goal1688", goal1672_text)


if __name__ == "__main__":
    unittest.main()
