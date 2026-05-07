import unittest

import rtdsl as rt


class Goal1442V152PreparedCollectCompletionTest(unittest.TestCase):
    def test_completed_result_binds_to_compatible_prepared_descriptor(self) -> None:
        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=4,
            row_width=2,
            backend="embree",
        )
        result = rt.collect_k_bounded_rows(((2, 20), (1, 10)), k=4, row_width=2)

        completed = rt.complete_prepared_collect_k_result_buffer_descriptor(prepared, result)

        self.assertEqual(completed["buffer_kind"], "result")
        self.assertEqual(completed["prepared_buffer_kind"], "prepared_result")
        self.assertEqual(completed["shape"], (4, 2))
        self.assertEqual(completed["valid_shape"], (2, 2))
        self.assertEqual(completed["prepared_shape"], (4, 2))
        self.assertEqual(completed["prepared_valid_shape"], (0, 2))
        self.assertEqual(completed["prepared_capacity"], 4)
        self.assertEqual(completed["valid_count"], 2)
        self.assertIs(completed["prepared_descriptor_compatible"], True)
        self.assertIs(completed["true_zero_copy_authorized"], False)

    def test_completed_cuda_metadata_keeps_false_claim_flags(self) -> None:
        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=2,
            row_width=2,
            backend="optix",
            device="cuda",
            owner="native",
            copy_boundary="prepared_device_buffer_reuse",
        )
        result = rt.collect_k_bounded_rows(((1, 10),), k=2, row_width=2)

        completed = rt.complete_prepared_collect_k_result_buffer_descriptor(prepared, result)

        self.assertEqual(completed["device"], "cuda")
        self.assertEqual(completed["owner"], "native")
        self.assertEqual(completed["prepared_copy_boundary"], "prepared_device_buffer_reuse")
        self.assertIs(completed["true_zero_copy_authorized"], False)
        self.assertIs(completed["public_speedup_wording_authorized"], False)
        self.assertIs(completed["whole_app_speedup_claim_authorized"], False)

    def test_completion_rejects_non_prepared_descriptor(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=1, row_width=2)
        completed_descriptor = rt.collect_k_result_buffer_descriptor(result, row_width=2)

        with self.assertRaisesRegex(ValueError, "buffer_kind=prepared_result"):
            rt.complete_prepared_collect_k_result_buffer_descriptor(completed_descriptor, result)

    def test_completion_rejects_capacity_row_width_and_backend_mismatch(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=2, row_width=2)

        too_small = rt.prepare_collect_k_result_buffer_descriptor(capacity=0, row_width=2)
        with self.assertRaisesRegex(RuntimeError, "exceeds prepared buffer capacity"):
            rt.complete_prepared_collect_k_result_buffer_descriptor(too_small, result)

        declared_wrong_width = {
            **result,
            "row_width": 3,
        }
        with self.assertRaisesRegex(ValueError, "row_width does not match"):
            rt.complete_prepared_collect_k_result_buffer_descriptor(
                rt.prepare_collect_k_result_buffer_descriptor(capacity=2, row_width=2),
                declared_wrong_width,
            )

        undeclared_width_result = dict(result)
        del undeclared_width_result["row_width"]
        wrong_candidate_width = rt.prepare_collect_k_result_buffer_descriptor(capacity=2, row_width=3)
        with self.assertRaisesRegex(ValueError, "row width mismatch"):
            rt.complete_prepared_collect_k_result_buffer_descriptor(
                wrong_candidate_width,
                undeclared_width_result,
            )

        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=2,
            row_width=2,
            backend="embree",
        )
        native_result = {
            **result,
            "backend": "optix",
        }
        with self.assertRaisesRegex(ValueError, "backend mismatch"):
            rt.complete_prepared_collect_k_result_buffer_descriptor(prepared, native_result)


if __name__ == "__main__":
    unittest.main()
