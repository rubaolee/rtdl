from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native"
NATIVE_PIP_FILES = (
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
REPORT = ROOT / "docs" / "reports" / "goal1681_pip_to_point_primitive_anyhit_native_migration_2026-05-10.md"
GATE = ROOT / "docs" / "release_reports" / "v1_7_app_agnostic_native_gate.md"
GOAL1672 = ROOT / "docs" / "reports" / "goal1672_native_app_leakage_migration_classification_2026-05-10.md"

LEAKAGE_RE = re.compile(
    r"\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b",
    re.IGNORECASE,
)
FALSE_POSITIVE_CONSTANT_RE = re.compile(r"\bRTDL_DB_[A-Z0-9_]+\b")

REMOVED_PIP_SYMBOLS = (
    "rtdl_embree_run_pip",
    "rtdl_hiprt_run_pip",
    "rtdl_hiprt_pip_2d",
    "rtdl_optix_run_pip",
    "rtdl_oracle_run_pip",
    "rtdl_vulkan_run_pip",
)

REPLACEMENT_PIP_SYMBOLS = (
    "rtdl_embree_run_point_primitive_anyhit_packet",
    "rtdl_hiprt_run_point_primitive_anyhit_packet",
    "rtdl_hiprt_point_primitive_anyhit_2d",
    "rtdl_optix_run_point_primitive_anyhit_packet",
    "rtdl_oracle_run_point_primitive_anyhit_packet",
    "rtdl_vulkan_run_point_primitive_anyhit_packet",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _native_text() -> str:
    chunks: list[str] = []
    for path in NATIVE.rglob("*"):
        if path.suffix.lower() in {".cpp", ".h", ".cu", ".mm"}:
            chunks.append(_text(path))
    return "\n".join(chunks)


class Goal1681PipToPointPrimitiveAnyhitNativeMigrationTest(unittest.TestCase):
    def test_pip_native_files_no_longer_export_pip_named_callables(self) -> None:
        for path in NATIVE_PIP_FILES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                for symbol in REMOVED_PIP_SYMBOLS:
                    with self.subTest(symbol=symbol):
                        self.assertNotIn(symbol, text)

    def test_native_exports_replacement_point_primitive_anyhit_symbols(self) -> None:
        combined = _native_text()
        for symbol in REPLACEMENT_PIP_SYMBOLS:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, combined)

    def test_strict_native_scan_no_longer_flags_pip_family(self) -> None:
        text = _native_text()
        strict_occurrences = [match.group(0) for match in LEAKAGE_RE.finditer(text)]
        false_positive_symbols = set(FALSE_POSITIVE_CONSTANT_RE.findall(text))
        strict_symbols = set(strict_occurrences)
        real_symbols = strict_symbols - false_positive_symbols

        pip_symbols = sorted(s for s in real_symbols if "pip" in s.lower())
        self.assertEqual(pip_symbols, [])

        by_family = Counter()
        for symbol in real_symbols:
            lowered = symbol.lower()
            for term in ("db", "pip", "bfs", "robot", "pose", "polygon", "knn", "hausdorff", "jaccard"):
                if term in lowered:
                    by_family[term] += 1
                    break
        self.assertNotIn("pip", by_family)
        self.assertIn(by_family["db"], {0, 30})
        self.assertIn(by_family["polygon"], {0, 29})
        self.assertIn(by_family["knn"], {0, 14})
        self.assertIn(by_family["bfs"], {0, 2, 10})
        # Goal1682 may remove the final Hausdorff-shaped symbol after this
        # PIP migration. This test only owns the PIP family.
        self.assertIn(by_family["hausdorff"], {0, 1})

        self.assertIn(len(strict_symbols), {9, 39, 68, 82, 84, 92, 93})
        self.assertIn(len(strict_occurrences), {14, 73, 131, 159, 164, 178, 180})
        self.assertIn(len(real_symbols), {0, 30, 59, 73, 75, 83, 84})

    def test_report_records_boundary_and_no_pod_claim(self) -> None:
        report_text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "no longer\nexport `pip`-shaped symbols",
            "This is a local source migration only",
            "No pod validation was run",
            "broader app-agnostic gate still fails",
            "Remaining app-shaped callable/export symbols | 84",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)

    def test_gate_links_goal1681_report(self) -> None:
        gate_text = GATE.read_text(encoding="utf-8")
        self.assertIn(
            "goal1681_pip_to_point_primitive_anyhit_native_migration_2026-05-10.md",
            gate_text,
        )

    def test_goal1672_records_goal1681_followup(self) -> None:
        goal1672_text = GOAL1672.read_text(encoding="utf-8")
        self.assertIn("Goal1681", goal1672_text)


if __name__ == "__main__":
    unittest.main()
