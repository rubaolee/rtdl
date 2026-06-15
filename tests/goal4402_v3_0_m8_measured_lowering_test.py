from __future__ import annotations

import unittest

import rtdsl as rt


def _reference_backend(points, tree_nodes, *, theta, max_total_rows):
    result = rt.collect_aggregate_frontier_2d(
        points,
        tree_nodes,
        theta=theta,
        max_total_rows=max_total_rows,
    )
    return {
        **result,
        "metadata": {
            **result["metadata"],
            "native_symbol": "reference_backend_symbol",
            "native_engine_app_specific": False,
        },
    }


class Goal4402V30M8MeasuredLoweringTest(unittest.TestCase):
    def test_weighted_point_grid_is_deterministic_and_generic(self) -> None:
        first = rt.make_v3_m8_weighted_point_grid(9)
        second = rt.make_v3_m8_weighted_point_grid(9)

        self.assertEqual(first, second)
        self.assertEqual(tuple(point["id"] for point in first), tuple(range(9)))
        self.assertNotIn("barnes", repr(first).lower())

    def test_fake_backend_case_builds_two_row_harness_without_claims(self) -> None:
        payload = rt.run_v3_m8_aggregate_frontier_lowering_case(
            point_count=16,
            bucket_size=4,
            theta=0.5,
            warmups=0,
            repeats=2,
            hardware="unit_test_host",
            backend_functions={"embree": _reference_backend, "optix": _reference_backend},
        )
        validation = rt.validate_v3_m8_aggregate_frontier_lowering_payload(payload)

        self.assertEqual(validation["status"], rt.V3_M8_MEASURED_LOWERING_STATUS)
        self.assertEqual(validation["backend_count"], 2)
        self.assertFalse(validation["public_claim_authorized"])
        self.assertEqual(payload["harness_validation"]["row_count"], 2)
        self.assertEqual(
            {row["backend"] for row in payload["backend_rows"]},
            {"embree", "optix"},
        )
        for row in payload["backend_rows"]:
            self.assertTrue(row["rows_match_reference"])
            self.assertFalse(row["claim_readiness"]["device_resident_ready"])
            self.assertFalse(row["claim_readiness"]["true_zero_copy_ready"])

    def test_lowering_instrumentation_is_phase_complete_and_host_materialized(self) -> None:
        packet = rt.build_v3_m8_lowering_instrumentation(
            backend="optix",
            hardware="unit_test_gpu",
            prepare_seconds=0.001,
            build_seconds=0.002,
            native_seconds=0.003,
            validation_seconds=0.004,
            native_symbol="rtdl_optix_collect_aggregate_frontier_2d",
            frontier_row_count=7,
        )
        payload = packet.to_metadata()

        self.assertTrue(payload["claim_readiness"]["phase_complete"])
        self.assertFalse(payload["claim_readiness"]["same_stream_ready"])
        self.assertFalse(payload["claim_readiness"]["device_resident_ready"])
        self.assertFalse(payload["claim_readiness"]["true_zero_copy_ready"])
        self.assertTrue(payload["residency_evidence"][0]["host_materialized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_authorized"])

    def test_rejects_missing_backend_function(self) -> None:
        with self.assertRaisesRegex(rt.GraphValidationError, "requires optix"):
            rt.run_v3_m8_aggregate_frontier_lowering_case(
                point_count=8,
                bucket_size=2,
                backend_functions={"embree": _reference_backend},
            )


if __name__ == "__main__":
    unittest.main()
