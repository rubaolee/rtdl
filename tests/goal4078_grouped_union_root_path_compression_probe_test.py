from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal4078_grouped_union_root_path_compression_probe_2026-06-09.md"


class Goal4078GroupedUnionRootPathCompressionProbeTest(unittest.TestCase):
    def test_native_grouped_union_uses_monotonic_path_halving_probe(self) -> None:
        source = CORE.read_text(encoding="utf-8")
        self.assertIn("find_grouped_union_root_compressing", source)
        self.assertIn("const int next = parent[root];", source)
        self.assertIn("const int grand = parent[next];", source)
        self.assertIn("atomicMin(parent + root, grand);", source)
        self.assertNotIn("find_grouped_union_root_readonly", source)

    def test_runtime_metadata_exposes_policy_for_measured_paths(self) -> None:
        source = RUNTIME.read_text(encoding="utf-8")
        self.assertIn(
            '"grouped_union_root_path_compression_policy": "monotonic_atomic_min_path_halving_default"',
            source,
        )
        self.assertGreaterEqual(source.count("grouped_union_root_path_compression_policy"), 4)

    def test_report_records_probe_acceptance_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "Goal4078",
            "generic prepared fixed-radius grouped-union primitive",
            "kept only if pod evidence shows",
            "reverted and recorded as negative evidence",
            "does not add native ABI",
            "true-zero-copy",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
