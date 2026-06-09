from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4143_direct_status_prepared_workspace_reuse_2026-06-09.md"


class Goal4143DirectStatusPreparedWorkspaceReuseTest(unittest.TestCase):
    def test_prepared_handle_owns_reusable_workspaces(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")

        for fragment in (
            "workspaces: dict[str, Any]",
            '"prepared_direct_status_union_workspaces_preallocated": True',
            '"workspace_column_count": len(self.workspaces)',
            "workspaces=self.workspaces",
            '"prepared_direct_status_union_workspaces_reused": workspaces is not None',
        ):
            self.assertIn(fragment, source)

    def test_direct_status_kernel_resets_workspaces_instead_of_reallocating_identity(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        helper = source[
            source.index("def _cupy_direct_partition_status_union_component_roots"):
            source.index("def _cupy_union_partition_pairs_with_ambiguous_points")
        ]

        for fragment in (
            "reset_direct_partition_status_workspaces_kernel",
            "parents[idx] = idx;",
            "safe_skip_count[0] = 0u;",
            "positive_count[0] = 0u;",
            "workspaces[\"parents\"]",
        ):
            self.assertIn(fragment, helper)
        self.assertNotIn("parents = cupy.arange(partition_count, dtype=cupy.uint32)", helper)

    def test_report_blocks_performance_claims_until_pod_timing(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "implementation-complete-pod-needed",
            "generic fixed-radius partition/component workspace reuse",
            "does not add DBSCAN-specific native logic",
            "Pod timing is required before making any performance conclusion.",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
