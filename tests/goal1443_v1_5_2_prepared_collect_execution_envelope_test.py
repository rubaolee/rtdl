import unittest

import rtdsl as rt


class Goal1443V152PreparedCollectExecutionEnvelopeTest(unittest.TestCase):
    def test_python_reference_execution_envelope_returns_result_and_descriptor(self) -> None:
        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=4,
            row_width=2,
            backend="embree",
        )

        envelope = rt.run_collect_k_bounded_rows_with_prepared_result_buffer(
            ((2, 20), (1, 10), (1, 10)),
            prepared,
        )

        self.assertEqual(envelope["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(
            envelope["execution_mode"],
            "python_reference_prepared_descriptor_envelope",
        )
        self.assertEqual(envelope["backend"], "embree")
        self.assertEqual(envelope["result"]["candidate_id_rows"], ((1, 10), (2, 20)))
        self.assertEqual(envelope["result"]["valid_count"], 2)
        self.assertEqual(envelope["result_buffer_descriptor"]["shape"], (4, 2))
        self.assertEqual(envelope["result_buffer_descriptor"]["valid_shape"], (2, 2))
        self.assertIs(envelope["prepared_descriptor_compatible"], True)
        self.assertIs(envelope["true_zero_copy_authorized"], False)

    def test_cuda_prepared_metadata_does_not_claim_native_or_zero_copy_execution(self) -> None:
        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=2,
            row_width=2,
            backend="optix",
            device="cuda",
            owner="native",
            copy_boundary="prepared_device_buffer_reuse",
        )

        envelope = rt.run_collect_k_bounded_rows_with_prepared_result_buffer(
            ((1, 10),),
            prepared,
        )

        self.assertEqual(envelope["result_buffer_descriptor"]["device"], "cuda")
        self.assertEqual(envelope["result_buffer_descriptor"]["owner"], "native")
        self.assertEqual(envelope["result_buffer_descriptor"]["prepared_backend"], "optix")
        self.assertIn("Python reference execution envelope", envelope["claim_boundary"])
        self.assertIs(envelope["true_zero_copy_authorized"], False)
        self.assertIs(envelope["public_speedup_wording_authorized"], False)
        self.assertIs(envelope["whole_app_speedup_claim_authorized"], False)

    def test_execution_envelope_rejects_non_prepared_descriptor(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=1, row_width=2)
        completed_descriptor = rt.collect_k_result_buffer_descriptor(result, row_width=2)

        with self.assertRaisesRegex(ValueError, "buffer_kind=prepared_result"):
            rt.run_collect_k_bounded_rows_with_prepared_result_buffer(
                ((1, 10),),
                completed_descriptor,
            )

    def test_execution_envelope_fails_closed_on_overflow(self) -> None:
        prepared = rt.prepare_collect_k_result_buffer_descriptor(capacity=1, row_width=2)

        with self.assertRaisesRegex(RuntimeError, "overflowed capacity"):
            rt.run_collect_k_bounded_rows_with_prepared_result_buffer(
                ((1, 10), (2, 20)),
                prepared,
            )

    def test_execution_envelope_rejects_candidate_width_mismatch(self) -> None:
        prepared = rt.prepare_collect_k_result_buffer_descriptor(capacity=2, row_width=2)

        with self.assertRaisesRegex(ValueError, "candidate row width mismatch"):
            rt.run_collect_k_bounded_rows_with_prepared_result_buffer(
                ((1, 10, 100),),
                prepared,
            )


if __name__ == "__main__":
    unittest.main()
