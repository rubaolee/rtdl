from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
HIT_STREAM_HANDOFF = ROOT / "src" / "rtdsl" / "hit_stream_handoff.py"
TRITON_CONTINUATION = ROOT / "src" / "rtdsl" / "triton_partner_continuation.py"
REPORT = ROOT / "docs" / "reports" / "goal2835_primitive_payload_entrypoint_metadata_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2836_gemini_review_goal2835_primitive_payload_entrypoint_metadata_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2836_goal2835_primitive_payload_entrypoint_metadata_consensus_2026-05-31.md"


class Goal2835PrimitivePayloadEntrypointMetadataTest(unittest.TestCase):
    def test_reference_entrypoint_attaches_planner_metadata_to_result(self) -> None:
        descriptor = rt.describe_primitive_payload_column_descriptor(
            name="group_ids",
            dtype="int64",
            shape=(3,),
            semantic_role="primitive_payload",
            producer="host_reference",
            consumer="python_reference",
            device_type="cpu",
            fallback_reason="host_reference",
            host_materialized_before_handoff=True,
        )

        result = rt.execute_v2_5_partner_continuation_reference(
            "segmented_count_i64",
            {"group_ids": [0, 1, 1], "group_count": 2},
            primitive_payload_descriptors=(descriptor,),
        )
        entrypoint = result["primitive_payload_continuation_entrypoint"]

        self.assertEqual(result["outputs"], {"counts": [1, 2]})
        self.assertEqual(
            entrypoint["contract_version"],
            rt.GENERIC_PRIMITIVE_PAYLOAD_CONTINUATION_ENTRYPOINT_METADATA_VERSION,
        )
        self.assertEqual(entrypoint["entrypoint"], "execute_v2_5_partner_continuation_reference")
        self.assertEqual(entrypoint["execution_status"], "completed_reference")
        self.assertEqual(entrypoint["requested_partner"], "python_reference")
        self.assertEqual(entrypoint["resolved_partner"], "python_reference")
        self.assertEqual(entrypoint["plan_status"], "reference_contract")
        self.assertEqual(entrypoint["runtime_action"], "execute_reference_contract")
        self.assertFalse(entrypoint["can_execute_preview"])
        self.assertFalse(entrypoint["fallback_required"])
        self.assertFalse(result["true_zero_copy_authorized"])
        self.assertFalse(result["public_speedup_claim_authorized"])

    def test_triton_dispatcher_records_planner_on_explicit_reference_fallback(self) -> None:
        descriptor = rt.describe_fixed_radius_graph_partial_payload_descriptor(
            partials_device_ptr=0x1234000,
            partial_count=4,
            stream_ordering="same_stream",
            request_count=2,
            query_block_count=2,
        )

        result = rt.run_triton_partner_continuation(
            "hit_stream_grouped_ray_id_primitive_i64",
            {
                "ray_ids": [0, 0, 1],
                "primitive_ids": [5, 7, 11],
                "row_count": 3,
                "hit_event_count": 3,
                "overflow": False,
                "group_count": 2,
            },
            allow_reference_fallback=True,
            primitive_payload_descriptors=(descriptor,),
        )
        entrypoint = result["primitive_payload_continuation_entrypoint"]

        self.assertEqual(result["partner"], "python_reference")
        self.assertEqual(result["requested_partner"], "triton")
        self.assertEqual(result["outputs"]["group_hit_counts"], [2, 1])
        self.assertEqual(entrypoint["entrypoint"], "run_triton_partner_continuation")
        self.assertEqual(entrypoint["requested_partner"], "triton")
        self.assertEqual(entrypoint["resolved_partner"], "triton")
        self.assertEqual(entrypoint["plan_status"], "fallback_required")
        self.assertIn("partner_unavailable", entrypoint["fallback_reasons"])
        self.assertEqual(
            entrypoint["runtime_action"],
            "fallback_required_before_partner_execution",
        )
        self.assertTrue(result["primitive_payload_planner_fallback_required"])
        self.assertFalse(entrypoint["true_zero_copy_authorized"])
        self.assertFalse(entrypoint["public_speedup_claim_authorized"])

    def test_planned_entrypoint_metadata_can_be_inspected_without_execution(self) -> None:
        descriptor = rt.describe_fixed_radius_graph_partial_payload_descriptor(
            partials_device_ptr=0x1234000,
            partial_count=8,
            stream_ordering="same_stream",
        )

        metadata = rt.describe_primitive_payload_partner_continuation_entrypoint(
            operation="hit_stream_grouped_ray_id_primitive_i64",
            partner="cupy",
            descriptors=(descriptor,),
            entrypoint="prepared_graph.replay_same_stream_device_partials_summary_cupy",
        )

        self.assertEqual(metadata["resolved_partner"], "cupy_conformance")
        self.assertEqual(metadata["plan_status"], "accepted_preview")
        self.assertEqual(
            metadata["runtime_action"],
            "execute_preview_with_explicit_descriptor_plan",
        )
        self.assertTrue(metadata["stream_ordering_preserved"])
        self.assertEqual(metadata["fallback_reasons"], ())
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])

    def test_source_is_generic_and_claim_bounded(self) -> None:
        handoff = HIT_STREAM_HANDOFF.read_text(encoding="utf-8")
        triton = TRITON_CONTINUATION.read_text(encoding="utf-8")

        self.assertIn("describe_primitive_payload_partner_continuation_entrypoint", handoff)
        self.assertIn("attach_primitive_payload_partner_continuation_metadata", handoff)
        self.assertIn("primitive_payload_descriptors", triton)
        self.assertIn("public_speedup_claim_authorized", handoff)
        for source in (handoff, triton):
            self.assertNotIn("rayjoin", source.lower())
            self.assertNotIn("rtnn", source.lower())
            self.assertNotIn("dbscan", source.lower())

    def test_report_review_and_consensus_lock_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("real continuation entrypoints", report)
        self.assertIn("does not change kernel execution", report)
        self.assertIn("planner decision visible", report)

        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("entrypoint metadata", review)
        self.assertIn("unauthorized public speedup", review)

        self.assertIn("Codex + Gemini consensus accepts Goal2835 with boundary", consensus)
        self.assertIn("Planner decisions attached to continuation metadata | accept", consensus)
        self.assertIn("Broad public performance/release claims | not authorized", consensus)


if __name__ == "__main__":
    unittest.main()
