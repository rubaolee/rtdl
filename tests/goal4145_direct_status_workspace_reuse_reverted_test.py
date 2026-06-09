from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4145_direct_status_workspace_reuse_rejected_and_reverted_2026-06-09.md"


class Goal4145DirectStatusWorkspaceReuseRevertedTest(unittest.TestCase):
    def test_active_runtime_uses_measured_pre_candidate_default(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        helper = source[
            source.index("def _cupy_direct_partition_status_union_component_roots"):
            source.index("def _cupy_union_partition_pairs_with_ambiguous_points")
        ]
        prepare = source[
            source.index("def _prepare_direct_status_union_runtime_columns_cupy_3d"):
            source.index("def _run_direct_status_union_signature_from_prepared_columns_cupy_3d")
        ]

        self.assertIn("parents = cupy.arange(partition_count, dtype=cupy.uint32)", helper)
        self.assertNotIn("reset_direct_partition_status_workspaces_kernel", helper)
        self.assertNotIn("prepared_direct_status_union_workspaces_preallocated", prepare)

    def test_report_records_rejection_and_next_target(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "restoring the",
            "active runtime",
            "one-shot totals were worse",
            "measured faster default",
            "direct-status kernel work",
            "convergence/sync behavior",
            "prepare pipeline cost",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
