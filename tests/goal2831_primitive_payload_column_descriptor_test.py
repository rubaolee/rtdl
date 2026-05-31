from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
HIT_STREAM_HANDOFF = ROOT / "src" / "rtdsl" / "hit_stream_handoff.py"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2831_primitive_payload_column_descriptors_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2832_gemini_review_goal2831_primitive_payload_column_descriptors_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2832_goal2831_primitive_payload_column_descriptors_consensus_2026-05-31.md"


class Goal2831PrimitivePayloadColumnDescriptorTest(unittest.TestCase):
    def test_generic_descriptor_records_role_stream_lifetime_and_boundary(self) -> None:
        metadata = rt.describe_primitive_payload_column_descriptor(
            name="primitive_values",
            dtype="float64",
            shape=(4,),
            semantic_role="primitive_payload",
            producer="user_payload_columns",
            consumer="partner_grouped_reduction",
            device_type="cpu",
            source_protocol="python",
            fallback_reason="host_reference",
            host_materialized_before_handoff=True,
        )

        self.assertEqual(metadata["contract_version"], rt.GENERIC_PRIMITIVE_PAYLOAD_COLUMN_DESCRIPTOR_VERSION)
        self.assertEqual(metadata["semantic_role"], "primitive_payload")
        self.assertEqual(metadata["stream_ordering"], "not_proven")
        self.assertFalse(metadata["stream_ordering_proven"])
        self.assertEqual(metadata["fallback_reason"], "host_reference")
        self.assertTrue(metadata["fallback_required"])
        self.assertTrue(metadata["host_materialized_before_handoff"])
        self.assertEqual(metadata["neutral_buffer_seam"]["transfer_status"], "host_reference")
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])

    def test_fixed_radius_partial_descriptor_is_native_same_stream_borrowed_pointer(self) -> None:
        metadata = rt.describe_fixed_radius_graph_partial_payload_descriptor(
            partials_device_ptr=0xABC000,
            partial_count=8,
            stream_ordering="same_stream",
            request_count=2,
            query_block_count=4,
        )

        self.assertEqual(metadata["name"], "fixed_radius_ranked_summary_aggregate_partials")
        self.assertEqual(metadata["semantic_role"], "partial_aggregate_rows")
        self.assertEqual(metadata["producer"], "optix_cuda_graph")
        self.assertEqual(metadata["consumer"], "partner_partial_reduction")
        self.assertEqual(metadata["dtype"], "struct:RtdlFixedRadiusRankedNeighborAggregate")
        self.assertEqual(metadata["shape"], (8,))
        self.assertEqual(metadata["device"], "cuda:0")
        self.assertTrue(metadata["data_ptr_observed"])
        self.assertTrue(metadata["stream_ordering_proven"])
        self.assertTrue(metadata["event_or_same_stream_ordering_proven"])
        self.assertEqual(metadata["lifetime_state"], "producer_retained")
        self.assertFalse(metadata["fallback_required"])
        self.assertEqual(
            metadata["neutral_buffer_seam"]["transfer_status"],
            "borrowed_device_pointer_unmeasured",
        )
        self.assertTrue(metadata["neutral_buffer_seam"]["native_producer"])
        self.assertFalse(metadata["true_zero_copy_authorized"])

    def test_invalid_roles_and_native_lifetime_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported primitive payload column role"):
            rt.describe_primitive_payload_column_descriptor(
                name="x",
                dtype="int64",
                shape=(1,),
                semantic_role="app_specific_payload",
                producer="p",
                consumer="c",
            )

        with self.assertRaisesRegex(ValueError, "native primitive payload producers must retain ownership"):
            rt.describe_primitive_payload_column_descriptor(
                name="x",
                dtype="int64",
                shape=(1,),
                semantic_role="partial_aggregate_rows",
                producer="native",
                consumer="partner",
                device_type="cuda",
                data_ptr=123,
                native_producer=True,
            )

    def test_goal2829_runtime_metadata_wires_descriptor(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        source = HIT_STREAM_HANDOFF.read_text(encoding="utf-8")

        self.assertIn("primitive_payload_column_descriptors", runtime)
        self.assertIn("describe_fixed_radius_graph_partial_payload_descriptor", runtime)
        self.assertIn("RtdlPrimitivePayloadColumnDescriptor", source)
        self.assertIn("GENERIC_PRIMITIVE_PAYLOAD_COLUMN_DESCRIPTOR_VERSION", source)
        self.assertIn("fallback_reason", source)
        self.assertIn("native_producer", source)
        self.assertNotIn("rayjoin", source.lower())
        self.assertNotIn("rtnn", source.lower())

    def test_report_review_and_consensus_lock_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("typed primitive-payload column descriptors", report)
        self.assertIn("does not authorize", report)
        self.assertIn("True zero-copy still requires measured", report)

        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("genuinely generic", review)
        self.assertIn("borrowed_device_pointer_unmeasured", review)

        self.assertIn("Codex + Gemini consensus accepts Goal2831 with boundary", consensus)
        self.assertIn("Broad public performance/release claims | not authorized", consensus)
        self.assertIn("partner-neutral continuation planner", consensus)


if __name__ == "__main__":
    unittest.main()
