from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native"
REPORT = ROOT / "docs" / "reports" / "goal1680_current_native_app_leakage_gap_2026-05-10.md"
GATE = ROOT / "docs" / "release_reports" / "v1_7_app_agnostic_native_gate.md"

TERMS = ("db", "pip", "bfs", "robot", "pose", "polygon", "knn", "hausdorff", "jaccard")
LEAKAGE_RE = re.compile(
    r"\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b",
    re.IGNORECASE,
)
FALSE_POSITIVE_CONSTANT_RE = re.compile(r"\bRTDL_DB_[A-Z0-9_]+\b")


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


class Goal1680CurrentNativeAppLeakageGapTest(unittest.TestCase):
    def test_current_real_native_leakage_counts_are_recorded(self) -> None:
        text = _native_text()
        strict_occurrences = [match.group(0) for match in LEAKAGE_RE.finditer(text)]
        false_positive_occurrences = FALSE_POSITIVE_CONSTANT_RE.findall(text)
        strict_symbols = set(strict_occurrences)
        false_positive_symbols = set(false_positive_occurrences)
        real_symbols = strict_symbols - false_positive_symbols

        # Post-Goal1681/1682/1688/1690/1695/1697/1699/1704 strict cleanup
        # complete; all 9 remaining strict hits are uppercase RTDL_DB_*
        # constant false positives.
        self.assertEqual(len(strict_symbols), 9)
        self.assertEqual(len(strict_occurrences), 14)
        self.assertEqual(len(false_positive_symbols), 9)
        self.assertEqual(len(false_positive_occurrences), 14)
        self.assertEqual(len(real_symbols), 0)

        by_family = Counter(_first_family(symbol) for symbol in real_symbols)
        self.assertEqual(by_family, Counter())

    def test_first_cleanup_deltas_remain_absent_from_current_gap(self) -> None:
        text = _native_text()
        for symbol in (
            "rtdl_optix_prepare_pose_indices_2d",
            "rtdl_optix_pose_flags_prepared_ray_anyhit_2d_packed",
            "rtdl_optix_count_poses_prepared_ray_anyhit_2d_prepared_indices",
            "rtdl_oracle_polygon",
            "rtdl_embree_run_pip",
            "rtdl_hiprt_run_pip",
            "rtdl_hiprt_pip_2d",
            "rtdl_optix_run_pip",
            "rtdl_oracle_run_pip",
            "rtdl_vulkan_run_pip",
            "rtdl_embree_run_directed_hausdorff_2d",
            "rtdl_embree_run_bfs_expand",
            "rtdl_hiprt_run_bfs_expand",
            "rtdl_hiprt_run_prepared_bfs_expand",
            "rtdl_optix_run_bfs_expand",
            "rtdl_oracle_run_bfs_expand",
            "rtdl_oracle_summarize_bfs_rows",
            "rtdl_vulkan_run_bfs_expand",
        ):
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, text)

    def test_report_and_gate_link_current_gap(self) -> None:
        report_text = REPORT.read_text(encoding="utf-8")
        gate_text = GATE.read_text(encoding="utf-8")
        for phrase in (
            "The native app-agnostic release gate still fails.",
            "RTDL native internals are fully app-agnostic.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("goal1680_current_native_app_leakage_gap_2026-05-10.md", gate_text)


if __name__ == "__main__":
    unittest.main()
