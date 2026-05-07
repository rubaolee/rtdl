import ctypes
import unittest
from types import SimpleNamespace

from scripts import goal1467_v1_5_3_typed_host_buffer_parity as parity


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
        overflowed = len(normalized) > int(row_capacity)
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 1 if overflowed else 0
        if overflowed:
            return 0
        for row_index, row in enumerate(normalized):
            for column_index, value in enumerate(row):
                rows_out[row_index * int(row_width) + column_index] = value
        return 0


class Goal1467V153TypedHostBufferParityRunnerTest(unittest.TestCase):
    def test_run_backend_case_passes_exact_fit(self) -> None:
        case = parity.TypedHostParityCase(
            name="exact",
            candidate_rows=((2, 11), (1, 10), (2, 11)),
            capacity=2,
            expect_overflow=False,
        )
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_CollectKSymbol())

        result = parity.run_backend_case("embree", library, case)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["observed_rows"], ((1, 10), (2, 11)))
        self.assertTrue(result["typed_contiguous_host_buffer_path"])

    def test_run_backend_case_passes_fail_closed_overflow(self) -> None:
        case = parity.TypedHostParityCase(
            name="overflow",
            candidate_rows=((2, 11), (1, 10), (2, 11)),
            capacity=1,
            expect_overflow=True,
        )
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_CollectKSymbol())

        result = parity.run_backend_case("embree", library, case)

        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["observed_overflow"])

    def test_acceptance_payload_keeps_claims_blocked(self) -> None:
        payload = parity.run_acceptance_package(backends=(), required_backends=())

        self.assertTrue(payload["accepted"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["public_speedup_wording_authorized"])
        self.assertIn("does not authorize true zero-copy", payload["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
