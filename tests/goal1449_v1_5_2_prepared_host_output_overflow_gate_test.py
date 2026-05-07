import ctypes
import unittest
from types import SimpleNamespace

import rtdsl as rt


class _OverflowNativeCollectKSymbol:
    def __call__(
        self,
        _candidate_rows,
        _candidate_count,
        _row_width,
        _rows_out,
        _row_capacity,
        emitted_count_out,
        overflowed_out,
        _error,
        _error_size,
    ):
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = 2
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 1
        return 0


class _FailingNativeCollectKSymbol:
    def __call__(
        self,
        _candidate_rows,
        _candidate_count,
        _row_width,
        _rows_out,
        _row_capacity,
        _emitted_count_out,
        _overflowed_out,
        error,
        _error_size,
    ):
        error.value = b"synthetic native failure"
        return 7


class Goal1449V152PreparedHostOutputOverflowGateTest(unittest.TestCase):
    def test_overflow_validation_returns_fail_closed_evidence(self) -> None:
        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=1,
            row_width=2,
            backend="embree",
            copy_boundary="prepared_host_buffer_reuse",
        )
        output_buffer = (ctypes.c_int64 * 2)()
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_OverflowNativeCollectKSymbol())

        evidence = rt.validate_native_collect_k_prepared_host_output_overflow_fail_closed(
            ((1, 10), (2, 20)),
            prepared,
            output_buffer=output_buffer,
            library=library,
            symbol_name="rtdl_embree_collect_k_bounded_i64",
            candidate_source_symbol="test_candidate_rows",
        )

        self.assertEqual(evidence["status"], "prepared_host_output_overflow_fail_closed_validated")
        self.assertIs(evidence["overflow_fail_closed_with_prepared_buffer"], True)
        self.assertIs(evidence["partial_result_returned"], False)
        self.assertEqual(evidence["exception_type"], "RuntimeError")
        self.assertIn("overflowed capacity", evidence["exception_message"])
        for flag in (
            "true_zero_copy_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "stable_public_primitive_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(evidence[flag], False)

    def test_overflow_validation_does_not_swallow_non_overflow_runtime_errors(self) -> None:
        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=1,
            row_width=2,
            backend="embree",
            copy_boundary="prepared_host_buffer_reuse",
        )
        output_buffer = (ctypes.c_int64 * 2)()
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_FailingNativeCollectKSymbol())

        with self.assertRaisesRegex(RuntimeError, "synthetic native failure"):
            rt.validate_native_collect_k_prepared_host_output_overflow_fail_closed(
                ((1, 10),),
                prepared,
                output_buffer=output_buffer,
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_rows",
            )

    def test_reuse_gate_records_overflow_evidence_satisfied(self) -> None:
        gate = rt.validate_v1_5_2_prepared_buffer_reuse_gate()

        self.assertIn("overflow_fail_closed_with_prepared_buffer", gate["satisfied_evidence"])
        self.assertNotIn("overflow_fail_closed_with_prepared_buffer", gate["missing_evidence"])
        self.assertEqual(gate["missing_evidence"], ("external_ai_review",))


if __name__ == "__main__":
    unittest.main()
