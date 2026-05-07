import ctypes
import unittest
from types import SimpleNamespace

from scripts import goal1471_v1_5_3_typed_host_reuse_benchmark as benchmark


class _CollectKSymbol:
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
        if len(normalized) > int(row_capacity):
            ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 1
            return 0
        for row_index, row in enumerate(normalized):
            for column_index, value in enumerate(row):
                rows_out[row_index * int(row_width) + column_index] = value
        return 0


class Goal1471V153TypedHostReuseBenchmarkTest(unittest.TestCase):
    def test_benchmark_package_records_diagnostic_counts_without_claims(self) -> None:
        original_loader = benchmark.load_backend_library
        try:
            benchmark.load_backend_library = lambda _backend: SimpleNamespace(
                rtdl_embree_collect_k_bounded_i64=_CollectKSymbol()
            )
            payload = benchmark.run_benchmark_package(
                backends=("embree",),
                required_backends=("embree",),
                unique_rows=8,
                repeats=2,
                iterations=3,
            )
        finally:
            benchmark.load_backend_library = original_loader

        self.assertTrue(payload["accepted"])
        result = payload["results"][0]
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["candidate_row_count"], 16)
        self.assertEqual(result["baseline_input_materialization_count"], 3)
        self.assertEqual(result["typed_input_materialization_count"], 1)
        self.assertEqual(result["input_materialization_count_delta"], 2)
        self.assertTrue(result["timing_recorded_for_diagnostics_only"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["public_speedup_wording_authorized"])


if __name__ == "__main__":
    unittest.main()
