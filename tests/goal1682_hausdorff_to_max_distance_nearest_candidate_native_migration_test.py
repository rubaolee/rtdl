from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native"
NATIVE_HAUSDORFF_FILES = (
    ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp",
    ROOT / "src" / "native" / "embree" / "rtdl_embree_prelude.h",
)
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_2026-05-10.md"
)
GATE = ROOT / "docs" / "release_reports" / "v1_7_app_agnostic_native_gate.md"
GOAL1672 = ROOT / "docs" / "reports" / "goal1672_native_app_leakage_migration_classification_2026-05-10.md"
EMBREE_RUNTIME = ROOT / "src" / "rtdsl" / "embree_runtime.py"

LEAKAGE_RE = re.compile(
    r"\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b",
    re.IGNORECASE,
)
FALSE_POSITIVE_CONSTANT_RE = re.compile(r"\bRTDL_DB_[A-Z0-9_]+\b")

REMOVED_HAUSDORFF_SYMBOL = "rtdl_embree_run_directed_hausdorff_2d"
REPLACEMENT_HAUSDORFF_SYMBOL = "rtdl_embree_run_max_distance_nearest_candidate_2d"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _native_text() -> str:
    chunks: list[str] = []
    for path in NATIVE.rglob("*"):
        if path.suffix.lower() in {".cpp", ".h", ".cu", ".mm"}:
            chunks.append(_text(path))
    return "\n".join(chunks)


class Goal1682HausdorffToMaxDistanceNearestCandidateNativeMigrationTest(unittest.TestCase):
    def test_native_files_no_longer_export_hausdorff_named_callable(self) -> None:
        for path in NATIVE_HAUSDORFF_FILES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(REMOVED_HAUSDORFF_SYMBOL, text)

    def test_native_exports_replacement_max_distance_nearest_candidate_symbol(self) -> None:
        combined = _native_text()
        self.assertIn(REPLACEMENT_HAUSDORFF_SYMBOL, combined)

    def test_strict_native_scan_no_longer_flags_hausdorff_family(self) -> None:
        text = _native_text()
        strict_occurrences = [match.group(0) for match in LEAKAGE_RE.finditer(text)]
        false_positive_symbols = set(FALSE_POSITIVE_CONSTANT_RE.findall(text))
        strict_symbols = set(strict_occurrences)
        real_symbols = strict_symbols - false_positive_symbols

        hausdorff_symbols = sorted(s for s in real_symbols if "hausdorff" in s.lower())
        self.assertEqual(hausdorff_symbols, [])

        by_family: Counter[str] = Counter()
        for symbol in real_symbols:
            lowered = symbol.lower()
            for term in ("db", "pip", "bfs", "robot", "pose", "polygon", "knn", "hausdorff", "jaccard"):
                if term in lowered:
                    by_family[term] += 1
                    break
        self.assertNotIn("hausdorff", by_family)
        self.assertNotIn("pip", by_family)
        self.assertIn(by_family["db"], {0, 30})
        self.assertIn(by_family["polygon"], {0, 29})
        self.assertIn(by_family["knn"], {0, 14})
        self.assertIn(by_family["bfs"], {0, 2, 10})

        self.assertIn(len(strict_symbols), {9, 39, 68, 82, 84, 92})
        self.assertIn(len(strict_occurrences), {14, 73, 131, 159, 164, 178})
        self.assertIn(len(real_symbols), {0, 30, 59, 73, 75, 83})

    def test_python_runtime_binds_replacement_symbol(self) -> None:
        text = EMBREE_RUNTIME.read_text(encoding="utf-8")
        self.assertIn(REPLACEMENT_HAUSDORFF_SYMBOL, text)
        self.assertNotIn(REMOVED_HAUSDORFF_SYMBOL, text)
        # The Python helper retains Hausdorff semantics and a stable public
        # function name; the migration moves only the native ABI string.
        self.assertIn("def directed_hausdorff_2d_embree(", text)

    def test_report_records_boundary_and_no_pod_claim(self) -> None:
        report_text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "no longer exports a\n`hausdorff`-shaped symbol",
            "Hausdorff semantics",
            "remain in the\nPython",
            "This is a local source migration only",
            "No pod validation was run",
            "broader app-agnostic gate still fails",
            "Remaining app-shaped callable/export symbols | 83",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)

    def test_gate_links_goal1682_report(self) -> None:
        gate_text = GATE.read_text(encoding="utf-8")
        self.assertIn(
            "goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_2026-05-10.md",
            gate_text,
        )

    def test_goal1672_records_goal1682_followup(self) -> None:
        goal1672_text = GOAL1672.read_text(encoding="utf-8")
        self.assertIn("Goal1682", goal1672_text)


if __name__ == "__main__":
    unittest.main()
