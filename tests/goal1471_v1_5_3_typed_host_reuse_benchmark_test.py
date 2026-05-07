import ctypes
import json
from pathlib import Path
import unittest
from types import SimpleNamespace

from scripts import goal1471_v1_5_3_typed_host_reuse_benchmark as benchmark


ROOT = Path(__file__).resolve().parents[1]
POD_JSON = ROOT / "docs" / "reports" / "goal1471_v1_5_3_typed_host_reuse_benchmark_pod_2026-05-07.json"


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

    def test_pod_benchmark_artifact_is_accepted_but_diagnostic_only(self) -> None:
        payload = json.loads(POD_JSON.read_text(encoding="utf-8"))

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["required_backends"], ["embree", "optix"])
        self.assertEqual(payload["skipped_required"], [])
        by_backend = {row["backend"]: row for row in payload["results"]}
        self.assertEqual(set(by_backend), {"embree", "optix"})
        for backend, row in by_backend.items():
            with self.subTest(backend=backend):
                self.assertEqual(row["status"], "pass")
                self.assertEqual(row["baseline_input_materialization_count"], 20)
                self.assertEqual(row["typed_input_materialization_count"], 1)
                self.assertEqual(row["input_materialization_count_delta"], 19)
                self.assertTrue(row["timing_recorded_for_diagnostics_only"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["public_speedup_wording_authorized"])
        self.assertIn("does not authorize true zero-copy", payload["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
