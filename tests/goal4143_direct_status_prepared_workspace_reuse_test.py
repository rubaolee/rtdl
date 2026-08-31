from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4143_direct_status_prepared_workspace_reuse_2026-06-09.md"


class Goal4143DirectStatusPreparedWorkspaceReuseTest(unittest.TestCase):
    def test_candidate_is_documented_but_not_active_after_goal4144(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        helper = source[
            source.index("def _cupy_direct_partition_status_union_component_roots"):
            source.index("def _cupy_union_partition_pairs_with_ambiguous_points")
        ]

        self.assertNotIn("reset_direct_partition_status_workspaces_kernel", helper)
        self.assertNotIn("workspaces[\"parents\"]", helper)
        self.assertIn("parents = cupy.arange(partition_count, dtype=cupy.uint32)", helper)

    def test_report_marks_candidate_superseded(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "superseded-by-goal4144-negative-pod-result",
            "Goal4144 measured this candidate on the pod and rejected it",
            "runtime is therefore restored",
            "Do not promote prepared workspace",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
