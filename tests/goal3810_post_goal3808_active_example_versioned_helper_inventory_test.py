from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3810_post_goal3808_active_example_versioned_helper_inventory_2026-06-07.md"
EXAMPLE_ROOTS = (
    ROOT / "examples" / "v2_0" / "research_benchmarks",
    ROOT / "examples" / "v2_0" / "apps",
    ROOT / "examples" / "v2_0" / "features",
    ROOT / "examples" / "v2_0" / "partners",
    ROOT / "examples" / "v2_0" / "getting_started",
)
VERSION_PATTERN = re.compile(r"v[0-9]+_[0-9]+(?:_[0-9]+)?")


def _versioned_definitions() -> dict[str, set[str]]:
    names: dict[str, set[str]] = {}
    for root in EXAMPLE_ROOTS:
        for path in root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            rel = path.relative_to(ROOT).as_posix()
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if VERSION_PATTERN.search(node.name):
                        names.setdefault(rel, set()).add(node.name)
    return names


class Goal3810PostGoal3808ActiveExampleVersionedHelperInventoryTest(unittest.TestCase):
    def test_inventory_count_matches_current_active_example_surface(self) -> None:
        definitions = _versioned_definitions()
        count = sum(len(names) for names in definitions.values())
        self.assertEqual(count, 32)

    def test_all_low_risk_candidates_now_have_current_aliases(self) -> None:
        source_blob = "\n".join(
            path.read_text(encoding="utf-8")
            for root in EXAMPLE_ROOTS
            for path in root.rglob("*.py")
        )
        for alias in (
            "describe_bounded_witness_session",
            "primitive_first_plan_payload",
            "run_triangle_counting_segmented_compact_mask_numba_preview",
            "run_rayjoin_segmented_compact_mask_numba_preview",
            "run_raydb_grouped_reduction_typed_stream_continuation_preview",
            "run_barnes_hut_grouped_vector_sum_typed_stream_preview",
            "run_rtnn_ranked_summary_typed_stream_preview",
        ):
            self.assertIn(alias, source_blob)

    def test_remaining_special_cases_are_explicitly_recorded(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Remaining low-risk app-facing aliases not covered | 0",
            "RayDB internal implementation/protocol helpers | 11",
            "RT-Graph prepared-session protocol descriptor | 1",
            "Named future/topology reference route | 1",
            "run_rayjoin_v2_9_numba_side_aware_topology_reference",
            "not a release gate",
            "No source code changed in Goal3810",
        ):
            self.assertIn(phrase, text)

    def test_report_lists_goal3808_aliases(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("describe_v2_4_bounded_witness_session", text)
        self.assertIn("describe_bounded_witness_session", text)
        self.assertIn("v2_5_plan_payload", text)
        self.assertIn("primitive_first_plan_payload", text)


if __name__ == "__main__":
    unittest.main()
