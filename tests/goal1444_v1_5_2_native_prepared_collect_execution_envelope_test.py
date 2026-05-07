import ctypes
import unittest
from types import SimpleNamespace

import rtdsl as rt


def _make_generic_collect_k_symbol():
    def _symbol(
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
            for column, value in enumerate(row):
                rows_out[row_index * int(row_width) + column] = value
        return 0

    return _symbol


class Goal1444V152NativePreparedCollectExecutionEnvelopeTest(unittest.TestCase):
    def test_native_execution_envelope_returns_result_and_descriptor(self) -> None:
        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=4,
            row_width=2,
            backend="embree",
            owner="native",
            copy_boundary="prepared_host_buffer_reuse",
        )
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_make_generic_collect_k_symbol())

        envelope = rt.run_native_collect_k_bounded_rows_with_prepared_result_buffer(
            ((2, 20), (1, 10), (1, 10)),
            prepared,
            library=library,
            symbol_name="rtdl_embree_collect_k_bounded_i64",
            candidate_source_symbol="test_candidate_rows",
        )

        self.assertEqual(envelope["execution_mode"], "native_generic_symbol_prepared_descriptor_envelope")
        self.assertEqual(envelope["backend"], "embree")
        self.assertEqual(envelope["result"]["candidate_id_rows"], ((1, 10), (2, 20)))
        self.assertEqual(envelope["result"]["native_generic_symbol"], "rtdl_embree_collect_k_bounded_i64")
        self.assertEqual(envelope["result_buffer_descriptor"]["prepared_backend"], "embree")
        self.assertEqual(envelope["result_buffer_descriptor"]["valid_shape"], (2, 2))
        self.assertIs(envelope["prepared_descriptor_compatible"], True)
        self.assertIs(envelope["true_zero_copy_authorized"], False)

    def test_cuda_metadata_remains_metadata_only_for_native_envelope(self) -> None:
        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=2,
            row_width=2,
            backend="optix",
            device="cuda",
            owner="native",
            copy_boundary="prepared_device_buffer_reuse",
        )
        library = SimpleNamespace(rtdl_optix_collect_k_bounded_i64=_make_generic_collect_k_symbol())

        envelope = rt.run_native_collect_k_bounded_rows_with_prepared_result_buffer(
            ((1, 10),),
            prepared,
            library=library,
            symbol_name="rtdl_optix_collect_k_bounded_i64",
            candidate_source_symbol="test_candidate_rows",
        )

        self.assertEqual(envelope["result_buffer_descriptor"]["device"], "cuda")
        self.assertEqual(envelope["result_buffer_descriptor"]["prepared_copy_boundary"], "prepared_device_buffer_reuse")
        self.assertIn("ctypes-managed buffers", envelope["claim_boundary"])
        self.assertIs(envelope["true_zero_copy_authorized"], False)
        self.assertIs(envelope["public_speedup_wording_authorized"], False)
        self.assertIs(envelope["whole_app_speedup_claim_authorized"], False)

    def test_native_envelope_rejects_missing_or_mismatched_backend(self) -> None:
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_make_generic_collect_k_symbol())

        missing_backend = rt.prepare_collect_k_result_buffer_descriptor(capacity=1, row_width=2)
        with self.assertRaisesRegex(ValueError, "requires an explicit backend"):
            rt.run_native_collect_k_bounded_rows_with_prepared_result_buffer(
                ((1, 10),),
                missing_backend,
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_rows",
            )

        prepared = rt.prepare_collect_k_result_buffer_descriptor(capacity=1, row_width=2, backend="embree")
        with self.assertRaisesRegex(ValueError, "backend mismatch"):
            rt.run_native_collect_k_bounded_rows_with_prepared_result_buffer(
                ((1, 10),),
                prepared,
                backend="optix",
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_rows",
            )

    def test_native_envelope_rejects_non_prepared_descriptor_and_overflow(self) -> None:
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_make_generic_collect_k_symbol())
        result = rt.collect_k_bounded_rows(((1, 10),), k=1, row_width=2)
        completed_descriptor = rt.collect_k_result_buffer_descriptor(result, row_width=2)

        with self.assertRaisesRegex(ValueError, "buffer_kind=prepared_result"):
            rt.run_native_collect_k_bounded_rows_with_prepared_result_buffer(
                ((1, 10),),
                completed_descriptor,
                backend="embree",
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_rows",
            )

        prepared = rt.prepare_collect_k_result_buffer_descriptor(capacity=1, row_width=2, backend="embree")
        with self.assertRaisesRegex(RuntimeError, "overflowed capacity"):
            rt.run_native_collect_k_bounded_rows_with_prepared_result_buffer(
                ((1, 10), (2, 20)),
                prepared,
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_rows",
            )


if __name__ == "__main__":
    unittest.main()
