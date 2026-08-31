from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3806_active_example_versioned_helper_inventory_2026-06-07.md"
EXAMPLE_ROOTS = (
    ROOT / "examples" / "v2_0" / "research_benchmarks",
    ROOT / "examples" / "v2_0" / "apps",
    ROOT / "examples" / "v2_0" / "features",
    ROOT / "examples" / "v2_0" / "partners",
    ROOT / "examples" / "v2_0" / "getting_started",
)
VERSION_PATTERN = re.compile(r"v[0-9]+_[0-9]+(?:_[0-9]+)?")


def _versioned_function_names() -> list[str]:
    names: list[str] = []
    for root in EXAMPLE_ROOTS:
        for path in root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if VERSION_PATTERN.search(node.name):
                        names.append(node.name)
    return names


class Goal3806ActiveExampleVersionedHelperInventoryTest(unittest.TestCase):
    def test_inventory_count_matches_current_active_example_surface(self) -> None:
        names = _versioned_function_names()
        self.assertEqual(len(names), 32)

    def test_current_aliases_exist_for_cleaned_legacy_shims(self) -> None:
        names = _versioned_function_names()
        cleaned_legacy_names = {
            "run_triangle_counting_v2_6_numba_compact_mask_preview",
            "run_rayjoin_v2_6_numba_compact_mask_preview",
            "run_raydb_v2_8_typed_stream_continuation_preview",
            "run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview",
            "run_rtnn_v2_8_ranked_summary_typed_stream_preview",
        }
        self.assertTrue(cleaned_legacy_names.issubset(set(names)))

        source_blob = "\n".join(
            path.read_text(encoding="utf-8")
            for root in EXAMPLE_ROOTS
            for path in root.rglob("*.py")
        )
        for alias in (
            "run_triangle_counting_segmented_compact_mask_numba_preview",
            "run_rayjoin_segmented_compact_mask_numba_preview",
            "run_raydb_grouped_reduction_typed_stream_continuation_preview",
            "run_barnes_hut_grouped_vector_sum_typed_stream_preview",
            "run_rtnn_ranked_summary_typed_stream_preview",
        ):
            self.assertIn(alias, source_blob)

    def test_report_records_remaining_candidate_aliases_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "32 versioned function/class names",
            "Legacy compatibility shims now covered by current aliases",
            "RayDB internal implementation/protocol helpers",
            "describe_bounded_witness_session",
            "primitive_first_plan_payload",
            "No native engine code changed",
            "Future cleanup should add aliases before renaming or removing old names",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
