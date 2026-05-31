from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
HIT_STREAM_HANDOFF = ROOT / "src" / "rtdsl" / "hit_stream_handoff.py"
REPORT = ROOT / "docs" / "reports" / "goal2833_primitive_payload_partner_planner_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2834_gemini_review_goal2833_primitive_payload_partner_planner_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2834_goal2833_primitive_payload_partner_planner_consensus_2026-05-31.md"


class Goal2833PrimitivePayloadPartnerPlannerTest(unittest.TestCase):
    def test_cupy_preview_accepts_cuda_same_stream_descriptor_for_hit_stream_operation(self) -> None:
        descriptor = rt.describe_fixed_radius_graph_partial_payload_descriptor(
            partials_device_ptr=0x1234000,
            partial_count=16,
            stream_ordering="same_stream",
            request_count=4,
            query_block_count=4,
        )
        plan = rt.plan_primitive_payload_partner_continuation(
            "hit_stream_grouped_ray_id_primitive_i64",
            "cupy",
            (descriptor,),
        )

        self.assertEqual(plan["planner_version"], rt.GENERIC_PRIMITIVE_PAYLOAD_CONTINUATION_PLANNER_VERSION)
        self.assertEqual(plan["resolved_partner"], "cupy_conformance")
        self.assertEqual(plan["support_status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
        self.assertEqual(plan["plan_status"], "accepted_preview")
        self.assertTrue(plan["can_execute_preview"])
        self.assertFalse(plan["fallback_required"])
        self.assertEqual(plan["fallback_reasons"], ())
        self.assertTrue(plan["stream_ordering_preserved"])
        self.assertFalse(plan["true_zero_copy_authorized"])
        self.assertFalse(plan["public_speedup_claim_authorized"])

    def test_descriptor_only_partner_fails_closed_with_partner_unavailable(self) -> None:
        descriptor = rt.describe_fixed_radius_graph_partial_payload_descriptor(
            partials_device_ptr=0x1234000,
            partial_count=16,
            stream_ordering="same_stream",
        )
        plan = rt.plan_primitive_payload_partner_continuation(
            "segmented_count_i64",
            "cupy",
            (descriptor,),
        )

        self.assertEqual(plan["resolved_partner"], "cupy_conformance")
        self.assertEqual(plan["support_status"], rt.V2_5_SUPPORT_STATUS_DESCRIPTOR)
        self.assertEqual(plan["plan_status"], "fallback_required")
        self.assertIn("partner_unavailable", plan["fallback_reasons"])
        self.assertFalse(plan["can_execute_preview"])

    def test_cuda_required_partner_fails_closed_on_host_descriptor(self) -> None:
        descriptor = rt.describe_primitive_payload_column_descriptor(
            name="group_ids",
            dtype="int64",
            shape=(8,),
            semantic_role="primitive_payload",
            producer="host_reference",
            consumer="partner_grouped_reduction",
            device_type="cpu",
            fallback_reason="host_reference",
            host_materialized_before_handoff=True,
        )
        plan = rt.plan_primitive_payload_partner_continuation(
            "segmented_sum_f64",
            "triton",
            (descriptor,),
        )

        self.assertEqual(plan["resolved_partner"], "triton")
        self.assertEqual(plan["plan_status"], "fallback_required")
        self.assertIn("host_reference", plan["fallback_reasons"])
        self.assertIn("stream_ordering_unproven", plan["fallback_reasons"])
        self.assertFalse(plan["can_execute_preview"])

    def test_python_reference_accepts_host_descriptor_without_pretending_zero_copy(self) -> None:
        descriptor = rt.describe_primitive_payload_column_descriptor(
            name="group_ids",
            dtype="int64",
            shape=(8,),
            semantic_role="primitive_payload",
            producer="host_reference",
            consumer="python_reference",
            device_type="cpu",
            fallback_reason="host_reference",
            host_materialized_before_handoff=True,
        )
        plan = rt.plan_primitive_payload_partner_continuation(
            "segmented_count_i64",
            "python_reference",
            (descriptor,),
        )

        self.assertEqual(plan["plan_status"], "reference_contract")
        self.assertFalse(plan["fallback_required"])
        self.assertFalse(plan["can_execute_preview"])
        self.assertFalse(plan["true_zero_copy_authorized"])

    def test_bad_descriptor_metadata_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires descriptor metadata"):
            rt.plan_primitive_payload_partner_continuation(
                "segmented_count_i64",
                "triton",
                ({"contract_version": "wrong"},),
            )

    def test_source_remains_generic_and_claim_bounded(self) -> None:
        source = HIT_STREAM_HANDOFF.read_text(encoding="utf-8")

        self.assertIn("plan_primitive_payload_partner_continuation", source)
        self.assertIn("fallback_reasons", source)
        self.assertIn("rt_traversal_replacement_allowed", source)
        self.assertIn("public_speedup_claim_authorized", source)
        self.assertNotIn("rayjoin", source.lower())
        self.assertNotIn("rtnn", source.lower())
        self.assertNotIn("dbscan", source.lower())

    def test_report_review_and_consensus_lock_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("fail-closed fallback reason", report)
        self.assertIn("does not authorize", report)
        self.assertIn("accepted_preview", report)

        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("CuPy preview remains narrow", review)
        self.assertIn("Python reference path remains available", review)

        self.assertIn("Codex + Gemini consensus accepts Goal2833 with boundary", consensus)
        self.assertIn("Fails closed with explicit fallback reasons | accept", consensus)
        self.assertIn("Broad public performance/release claims | not authorized", consensus)


if __name__ == "__main__":
    unittest.main()
