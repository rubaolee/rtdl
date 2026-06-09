from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4146_direct_status_redundant_sync_removal_2026-06-09.md"


class Goal4146DirectStatusRedundantSyncRemovalTest(unittest.TestCase):
    def test_direct_status_convergence_loop_keeps_item_check_without_explicit_sync(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        helper = source[
            source.index("def _cupy_direct_partition_status_union_component_roots"):
            source.index("def _cupy_union_partition_pairs_with_ambiguous_points")
        ]

        self.assertIn("final_changed_flag = int(changed[0].item())", helper)
        self.assertIn("if final_changed_flag == 0:", helper)
        self.assertNotIn("cupy.cuda.get_current_stream().synchronize()", helper)

    def test_report_blocks_performance_claim_until_pod_timing(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "implementation-complete-pod-measured-in-goal4147",
            "scalar `.item()` read already",
            "not alter convergence semantics",
            "bounded",
            "replay-path cleanup",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
