from __future__ import annotations

import ctypes
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1520_v1_5_4_collect_k_native_emitted_count_guard_2026-05-08.md"


class _LyingEmittedCountSymbol:
    argtypes = None
    restype = None

    def __call__(
        self,
        _candidate_rows,
        _candidate_count,
        _row_width,
        rows_out,
        row_capacity,
        emitted_count_out,
        overflowed_out,
        _error,
        _error_size,
    ):
        capacity = int(row_capacity)
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = capacity + 1
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 0
        for index in range(capacity):
            rows_out[index] = 100 + index
        return 0


class _FakeLibrary:
    def __init__(self):
        self.rtdl_embree_collect_k_bounded_i64 = _LyingEmittedCountSymbol()


class Goal1520V154CollectKNativeEmittedCountGuardTest(unittest.TestCase):
    def test_report_records_boundary_and_validation(self):
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("emitted_count > capacity", text)
        self.assertIn("Ran 23 tests", text)
        self.assertIn("does not authorize stable `COLLECT_K_BOUNDED` promotion", text)

    def test_native_i64_wrapper_fails_closed_when_emitted_count_exceeds_capacity(self):
        with self.assertRaisesRegex(RuntimeError, "emitted_count exceeded capacity"):
            rt.collect_native_i64_rows_with_backend_symbol(
                [(1,), (2,)],
                capacity=1,
                row_width=1,
                backend="embree",
                library=_FakeLibrary(),
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_source",
            )

    def test_prepared_output_wrapper_fails_closed_when_emitted_count_exceeds_capacity(self):
        output = (ctypes.c_int64 * 1)()
        with self.assertRaisesRegex(RuntimeError, "emitted_count exceeded capacity"):
            rt.collect_native_i64_rows_into_prepared_output_buffer(
                [(1,), (2,)],
                output_buffer=output,
                capacity=1,
                row_width=1,
                backend="embree",
                library=_FakeLibrary(),
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_source",
            )


if __name__ == "__main__":
    unittest.main()
