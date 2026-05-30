import json
import unittest
from pathlib import Path

from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2728_raydb_v2_5_primitive_first_planner_2026-05-30.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2728_pod_artifacts"
    / "goal2728_raydb_v25_primitive_first_planner_pod_69_30_85_171_2026-05-30.json"
)


class Goal2728RaydbV25PrimitiveFirstPlannerTest(unittest.TestCase):
    def test_pod_artifact_records_primitive_first_selection(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["all_correct"])
        self.assertTrue(payload["no_public_speedup_claim"])
        self.assertEqual(payload["backends"], [raydb.PAPER_RT_OPTIX_V2_5_PRIMITIVE_FIRST_BACKEND])
        self.assertEqual(payload["row_counts"], [250000, 1000000])
        self.assertEqual(payload["modes"], ["count", "sum"])
        self.assertIn("NVIDIA RTX A5000", payload["nvidia_smi"])

        for case in payload["cases"]:
            with self.subTest(row_count=case["row_count"], mode=case["mode"]):
                self.assertTrue(case["matches_cpu_reference"])
                self.assertTrue(case["prepared_steady_state"])
                self.assertTrue(case["prepared_optix_scene_reused"])
                self.assertTrue(case["prepared_primitive_payload_reused"])
                self.assertTrue(case["prepared_ray_batch_reused"])
                self.assertFalse(case["prepared_payload_columns_reused"])
                self.assertFalse(case["native_device_column_path_used"])
                self.assertFalse(case["native_device_hit_stream_columns_ready"])
                self.assertFalse(case["typed_hit_stream_forced"])
                self.assertFalse(case["partner_continuation_required"])
                self.assertFalse(case["true_zero_copy_authorized"])
                self.assertEqual(
                    case["v2_5_selected_backend"],
                    raydb.PAPER_RT_OPTIX_PREPARED_GROUPED_REDUCTION_BACKEND,
                )
                self.assertEqual(case["v2_5_selected_path"], "prepared_fused_generic_grouped_reduction")
                self.assertEqual(
                    case["v2_5_selected_generic_primitive"],
                    raydb.GENERIC_RAY_TRIANGLE_GROUPED_REDUCTION_3D_SYMBOL,
                )
                self.assertEqual(
                    case["v2_5_alternative_backend"],
                    raydb.PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_PREPARED_BACKEND,
                )
                self.assertEqual(
                    case["v2_5_alternative_reserved_for"],
                    "continuations_not_expressible_as_fused_generic_rtdl_reductions",
                )
                plan = case["v2_5_primitive_first_plan"]
                self.assertEqual(plan["selected_path"], "prepared_fused_generic_grouped_reduction")
                self.assertFalse(plan["public_speedup_claim_authorized"])
                self.assertFalse(plan["true_zero_copy_authorized"])

    def test_report_documents_planner_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("RayDB v2.5 Primitive-First Planner", text)
        self.assertIn("v2.5 should not be \"partner first\" or \"hit-stream first.\"", text)
        self.assertIn("prepared fused generic grouped reduction", text)
        self.assertIn("typed hit-stream plus partner-continuation path available", text)
        self.assertIn("true-zero-copy wording", text)
        self.assertIn("selected backend, selected primitive/path", text)


if __name__ == "__main__":
    unittest.main()
