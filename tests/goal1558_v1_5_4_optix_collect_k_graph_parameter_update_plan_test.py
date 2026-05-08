from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1558_v1_5_4_optix_collect_k_graph_parameter_update_plan_2026-05-08.md"


class Goal1558V154OptixCollectKGraphParameterUpdatePlanTest(unittest.TestCase):
    def test_report_names_cuda_update_api_and_target_block(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("cuGraphExecKernelNodeSetParams", text)
        self.assertIn("CUDA_KERNEL_NODE_PARAMS", text)
        self.assertIn("collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived", text)
        self.assertIn("collect_k_bounded_i64_row_width2_final_mark_counts_level_counts", text)
        self.assertIn("collect_k_bounded_i64_row_width2_final_prefix_offsets_level", text)
        self.assertIn("collect_k_bounded_i64_row_width2_final_compact_level_derived", text)

    def test_report_keeps_candidate_opt_in_and_claim_boundary_narrow(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY=1", text)
        self.assertIn("fall back to the current direct-launch path", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
