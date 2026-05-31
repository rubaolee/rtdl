import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal2671V25PreviewGateTest(unittest.TestCase):
    def test_preview_gate_is_accept_but_not_completion_or_release(self):
        gate = rt.v2_5_partner_preview_gate()
        validation = rt.validate_v2_5_partner_preview_gate(gate)

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(gate["status"], "internal_v2_5_preview_pod_validation_required")
        self.assertEqual(gate["contract_validation_status"], "accept")
        self.assertTrue(gate["pod_validation_required"])
        self.assertTrue(gate["cuda_execution_validated"])
        self.assertEqual(gate["cuda_validation_goal"], "Goal2683")
        self.assertFalse(gate["benchmark_integration_validated"])
        self.assertIn("RT hit-stream handoff", gate["remaining_validation_scope"])
        self.assertFalse(gate["external_3ai_consensus_complete"])
        self.assertFalse(gate["public_release_tag_authorized"])
        self.assertFalse(gate["public_speedup_claim_authorized"])
        self.assertFalse(gate["rt_traversal_replacement_allowed"])
        self.assertFalse(gate["rawkernel_required_allowed"])

    def test_preview_gate_partitions_preview_kernel_and_reference_only_ops(self):
        gate = rt.v2_5_partner_preview_gate()

        self.assertEqual(
            gate["preview_kernel_operations"],
            (
                "segmented_count_i64",
                "segmented_sum_f64",
                "segmented_min_f64",
                "segmented_max_f64",
                "compact_mask_i64",
                "grouped_argmin_f64",
                "bounded_collect_finalize_i64",
            ),
        )
        self.assertEqual(gate["cupy_preview_operations"], ("hit_stream_grouped_ray_id_primitive_i64",))
        self.assertEqual(gate["reference_only_operations"], ())
        self.assertEqual(
            set(gate["preview_kernel_operations"]).union(
                gate["cupy_preview_operations"],
                gate["reference_only_operations"],
            ),
            set(rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES),
        )

    def test_goal2683_cuda_validation_artifact_is_importable(self):
        artifact = ROOT / "docs/reports/artifacts/goal2683_goal2665_low_level_triton_l4.json"
        payload = json.loads(artifact.read_text())

        self.assertTrue(payload["environment"]["cuda_available"])
        self.assertEqual(payload["environment"]["gpu_name"], "NVIDIA L4")
        for scale in payload["scales"]:
            self.assertTrue(all(scale["correctness"].values()))

    def test_docs_record_goal2671_preview_gate(self):
        report = (ROOT / "docs/reports/goal2671_v2_5_preview_gate_2026-05-27.md").read_text()

        self.assertIn("internal_v2_5_preview_pod_validation_required", report)
        self.assertIn("not a v2.5 completion gate", report)
        self.assertIn("pod validation required", report)


if __name__ == "__main__":
    unittest.main()
