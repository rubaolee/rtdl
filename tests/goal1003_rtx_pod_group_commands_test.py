from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1003_rtx_pod_group_commands.sh"


class Goal1003RtxPodGroupCommandsTest(unittest.TestCase):
    def test_script_is_bounded_pod_side_helper(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("already-running RTX-class Linux pod", text)
        self.assertIn("does not create cloud resources", text)
        self.assertIn("does not authorize performance claims", text)
        self.assertIn("nvidia-smi", text)
        self.assertIn("goal763_rtx_cloud_bootstrap_check.py", text)

    def test_script_runs_all_oom_safe_groups(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for summary in (
            "goal761_group_a_robot_summary.json",
            "goal761_group_b_fixed_radius_summary.json",
            "goal761_group_c_database_summary.json",
            "goal761_group_d_spatial_summary.json",
            "goal761_group_e_segment_polygon_summary.json",
            "goal761_group_f_graph_summary.json",
            "goal761_group_g_prepared_decision_summary.json",
            "goal761_group_h_polygon_summary.json",
        ):
            with self.subTest(summary=summary):
                self.assertIn(summary, text)

    def test_script_preserves_current_scalar_and_deferred_targets(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for target in (
            "prepared_fixed_radius_density_summary",
            "prepared_fixed_radius_core_flags",
            "graph_visibility_edges_gate",
            "segment_polygon_anyhit_rows_prepared_bounded_gate",
            "polygon_set_jaccard_optix_native_assisted_phase_gate",
        ):
            with self.subTest(target=target):
                self.assertIn(f"--only {target}", text)

    def test_script_tells_operator_to_copy_artifacts_before_stopping(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("Copy back", text)
        self.assertIn("before stopping the pod", text)


if __name__ == "__main__":
    unittest.main()
