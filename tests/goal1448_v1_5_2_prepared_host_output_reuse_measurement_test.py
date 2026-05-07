import ctypes
import unittest
from types import SimpleNamespace

import rtdsl as rt


class _CountingNativeCollectKSymbol:
    def __init__(self) -> None:
        self.rows_out_addresses = []

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
        self.rows_out_addresses.append(ctypes.addressof(rows_out.contents) if rows_out else None)
        rows = []
        for row_index in range(int(candidate_count)):
            start = row_index * int(row_width)
            rows.append(tuple(int(candidate_rows[start + column]) for column in range(int(row_width))))
        normalized = tuple(sorted(set(rows)))
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = len(normalized)
        overflowed = len(normalized) > int(row_capacity)
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 1 if overflowed else 0
        if overflowed:
            return 0
        for row_index, row in enumerate(normalized):
            for column, value in enumerate(row):
                rows_out[row_index * int(row_width) + column] = value
        return 0


class Goal1448V152PreparedHostOutputReuseMeasurementTest(unittest.TestCase):
    def test_measurement_records_stable_caller_owned_host_buffer_address(self) -> None:
        symbol = _CountingNativeCollectKSymbol()
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=symbol)
        output_buffer = (ctypes.c_int64 * 4)()
        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=2,
            row_width=2,
            backend="embree",
            copy_boundary="prepared_host_buffer_reuse",
        )

        measurement = rt.measure_native_collect_k_prepared_host_output_reuse(
            ((2, 20), (1, 10), (1, 10)),
            prepared,
            output_buffer=output_buffer,
            library=library,
            symbol_name="rtdl_embree_collect_k_bounded_i64",
            candidate_source_symbol="test_candidate_rows",
            iterations=4,
        )

        self.assertEqual(measurement["status"], "host_prepared_output_reuse_measured_python_wrapper_scope")
        self.assertEqual(measurement["iterations"], 4)
        self.assertEqual(measurement["output_buffer_address"], ctypes.addressof(output_buffer))
        self.assertIs(measurement["stable_output_buffer_address"], True)
        self.assertEqual(symbol.rows_out_addresses, [ctypes.addressof(output_buffer)] * 4)
        self.assertTrue(all(run["valid_shape"] == (2, 2) for run in measurement["runs"]))
        self.assertTrue(all(run["prepared_descriptor_compatible"] for run in measurement["runs"]))
        self.assertIs(measurement["host_reuse_or_device_reuse_measured"], True)
        self.assertEqual(measurement["measurement_scope"], "python_wrapper_ctypes_host_output_buffer_reuse_only")
        self.assertIs(measurement["device_reuse_measured"], False)
        for flag in (
            "true_zero_copy_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "stable_public_primitive_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(measurement[flag], False)

    def test_measurement_rejects_non_positive_iterations(self) -> None:
        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=1,
            row_width=2,
            backend="embree",
            copy_boundary="prepared_host_buffer_reuse",
        )
        output_buffer = (ctypes.c_int64 * 2)()
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_CountingNativeCollectKSymbol())

        with self.assertRaisesRegex(ValueError, "iterations > 0"):
            rt.measure_native_collect_k_prepared_host_output_reuse(
                ((1, 10),),
                prepared,
                output_buffer=output_buffer,
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_rows",
                iterations=0,
            )


if __name__ == "__main__":
    unittest.main()
