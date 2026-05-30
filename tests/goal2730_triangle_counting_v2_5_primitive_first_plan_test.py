import unittest
from pathlib import Path

import rtdsl as rt
from examples.v2_0.research_benchmarks.triangle_counting import (
    rtdl_triangle_counting_benchmark_app as triangle,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2730_triangle_counting_v2_5_primitive_first_plan_2026-05-30.md"


class Goal2730TriangleCountingV25PrimitiveFirstPlanTest(unittest.TestCase):
    def test_triangle_v25_plan_is_primitive_first(self) -> None:
        payload = triangle.run_app("v2_5_plan")
        plan = payload["v2_5_primitive_first_plan"]

        self.assertEqual(payload["status"], "primitive_first_plan_recorded_native_summary_not_relabelled_as_triton")
        self.assertEqual(plan["selected_path"], "prepared_fused_generic_rt_summary")
        self.assertIn(triangle.V2_4_RT_GRAPH_2A1_PRIMITIVE, plan["selected_primitives"])
        self.assertIn(triangle.V2_4_RT_GRAPH_1A2_PRIMITIVE, plan["selected_primitives"])
        self.assertEqual(plan["alternative_path"], "row_stream_or_compact_mask_plus_triton_continuation")
        self.assertFalse(plan["typed_hit_stream_forced"])
        self.assertFalse(plan["partner_continuation_required"])
        self.assertFalse(plan["public_speedup_claim_authorized"])
        self.assertFalse(plan["true_zero_copy_authorized"])
        self.assertIn("reserve Triton", payload["integration_decision"])

    def test_manifest_records_triangle_counting_as_primitive_first_summary(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        row = next(app for app in manifest["apps"] if app["app_id"] == "triangle_counting")

        self.assertEqual(row["benchmark_track"], "primitive_first_rt_summary")
        self.assertIn("scalar summary", row["parity_target"])
        self.assertIn("fused RTDL summary", row["same_contract_opponent"])
        self.assertIn("row-stream", row["next_action"])
        self.assertEqual(rt.validate_v2_5_tiered_benchmark_manifest()["status"], "accept")

    def test_report_documents_no_relabel_guardrail(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Triangle Counting v2.5 Primitive-First Plan", text)
        self.assertIn("do not force typed hit streams", text)
        self.assertIn("ray_triangle_weighted_any_hit_sum_3d", text)
        self.assertIn("ray_triangle_hit_count_sum_3d", text)
        self.assertIn("avoid relabeling", text)


if __name__ == "__main__":
    unittest.main()
