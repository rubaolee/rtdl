from __future__ import annotations

import unittest

import rtdsl as rt


class Goal4403V30M9GroupedStreamPartnerTest(unittest.TestCase):
    def test_point_grid_is_deterministic_and_generic(self) -> None:
        rows = rt.make_v3_m9_point_grid_3d(10)

        self.assertEqual(rows, rt.make_v3_m9_point_grid_3d(10))
        self.assertEqual(len(rows), 10)
        self.assertNotIn("dbscan", repr(rows).lower())

    def test_instrumentation_marks_device_resident_but_not_same_stream_or_zero_copy(self) -> None:
        packet = rt.build_v3_m9_grouped_stream_instrumentation(
            partner="cupy",
            hardware="unit_test_gpu",
            prepare_seconds=0.1,
            run_seconds=0.2,
            native_seconds=0.05,
            continuation_seconds=0.15,
            validation_seconds=0.01,
            data_ptrs={"component_labels": 1234, "neighbor_counts": 5678},
            metadata={
                "native_execution_path": "prepared_rt_core_grouped_union_3d_self_query",
                "native_engine_row_contract": "generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces",
                "rt_core_accelerated": True,
            },
        )
        payload = packet.to_metadata()

        self.assertTrue(payload["claim_readiness"]["device_resident_ready"])
        self.assertFalse(payload["claim_readiness"]["same_stream_ready"])
        self.assertFalse(payload["claim_readiness"]["true_zero_copy_ready"])
        self.assertFalse(payload["claim_readiness"]["public_claim_authorized"])
        self.assertEqual(payload["residency_evidence"][0]["storage"], "cuda")
        self.assertFalse(payload["residency_evidence"][0]["host_materialized"])

    def test_payload_validation_requires_cupy_and_numba(self) -> None:
        valid_payload = {
            "version": rt.V3_M9_GROUPED_STREAM_VERSION,
            "status": rt.V3_M9_GROUPED_STREAM_STATUS,
            "partner_rows": ({"partner": "cupy"}, {"partner": "numba"}),
            "comparison": {"signature_match": True},
            "claim_boundary": {
                "public_speedup_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "true_zero_copy_public_claim_authorized": False,
                "automatic_partner_selection_authorized": False,
            },
        }
        self.assertEqual(rt.validate_v3_m9_grouped_stream_payload(valid_payload)["partner_count"], 2)

        invalid = {**valid_payload, "partner_rows": ({"partner": "cupy"},)}
        with self.assertRaisesRegex(rt.GraphValidationError, "two partner rows"):
            rt.validate_v3_m9_grouped_stream_payload(invalid)

    def test_payload_validation_rejects_claim_promotion(self) -> None:
        payload = {
            "version": rt.V3_M9_GROUPED_STREAM_VERSION,
            "status": rt.V3_M9_GROUPED_STREAM_STATUS,
            "partner_rows": ({"partner": "cupy"}, {"partner": "numba"}),
            "comparison": {"signature_match": True},
            "claim_boundary": {
                "public_speedup_claim_authorized": True,
                "rt_core_speedup_claim_authorized": False,
                "true_zero_copy_public_claim_authorized": False,
                "automatic_partner_selection_authorized": False,
            },
        }

        with self.assertRaisesRegex(rt.GraphValidationError, "public_speedup"):
            rt.validate_v3_m9_grouped_stream_payload(payload)


if __name__ == "__main__":
    unittest.main()
