import ctypes
import unittest
from types import SimpleNamespace

import rtdsl as rt


class _MeasurementCollectKSymbol:
    def __call__(
        self,
        candidate_rows,
        candidate_count,
        row_width,
        rows_out,
        row_capacity,
        emitted_count_out,
        overflowed_out,
        _error,
        _error_size,
    ):
        rows = []
        for row_index in range(int(candidate_count)):
            start = row_index * int(row_width)
            rows.append(tuple(int(candidate_rows[start + column]) for column in range(int(row_width))))
        normalized = tuple(sorted(set(rows)))
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = len(normalized)
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 0
        for row_index, row in enumerate(normalized[: int(row_capacity)]):
            for column_index, value in enumerate(row):
                rows_out[row_index * int(row_width) + column_index] = value
        return 0


class Goal1464V153TypedHostInputMeasurementTest(unittest.TestCase):
    def test_measurement_records_input_materialization_count_delta(self) -> None:
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_MeasurementCollectKSymbol())
        output_buffer = (ctypes.c_int64 * 4)()
        output_descriptor = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=2,
            row_width=2,
            backend="embree",
            copy_boundary="prepared_host_buffer_reuse",
        )

        measurement = rt.measure_collect_k_typed_host_input_reuse(
            ((2, 20), (1, 10), (1, 10)),
            output_descriptor,
            output_buffer=output_buffer,
            library=library,
            symbol_name="rtdl_embree_collect_k_bounded_i64",
            backend="embree",
            row_width=2,
            iterations=4,
        )

        self.assertEqual(measurement["status"], "typed_host_input_copy_count_measurement_complete")
        self.assertEqual(measurement["iterations"], 4)
        self.assertEqual(measurement["baseline_input_materialization_count"], 4)
        self.assertEqual(measurement["typed_input_materialization_count"], 1)
        self.assertEqual(measurement["input_materialization_count_delta"], 3)
        self.assertTrue(measurement["copy_count_or_transfer_count_measurement"])
        self.assertTrue(measurement["timing_recorded_for_diagnostics_only"])
        self.assertEqual(
            {run["input_buffer_address"] for run in measurement["typed_runs"]},
            {measurement["typed_input_buffer_address"]},
        )

    def test_measurement_keeps_public_claims_blocked(self) -> None:
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_MeasurementCollectKSymbol())
        output_buffer = (ctypes.c_int64 * 2)()
        output_descriptor = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=1,
            row_width=2,
            backend="embree",
            copy_boundary="prepared_host_buffer_reuse",
        )

        measurement = rt.measure_collect_k_typed_host_input_reuse(
            ((1, 10),),
            output_descriptor,
            output_buffer=output_buffer,
            library=library,
            symbol_name="rtdl_embree_collect_k_bounded_i64",
            backend="embree",
            row_width=2,
            iterations=1,
        )

        for flag in (
            "true_zero_copy_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "stable_public_primitive_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(measurement[flag], False)
        self.assertIn("Timing is diagnostic only", measurement["claim_boundary"])
        self.assertIn("partner tensor handoff", measurement["claim_boundary"])

    def test_measurement_rejects_non_positive_iterations(self) -> None:
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_MeasurementCollectKSymbol())
        output_buffer = (ctypes.c_int64 * 2)()
        output_descriptor = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=1,
            row_width=2,
            backend="embree",
            copy_boundary="prepared_host_buffer_reuse",
        )

        with self.assertRaisesRegex(ValueError, "iterations > 0"):
            rt.measure_collect_k_typed_host_input_reuse(
                ((1, 10),),
                output_descriptor,
                output_buffer=output_buffer,
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                backend="embree",
                row_width=2,
                iterations=0,
            )


if __name__ == "__main__":
    unittest.main()
