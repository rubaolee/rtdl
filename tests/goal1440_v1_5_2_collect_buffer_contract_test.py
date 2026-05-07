import unittest

import rtdsl as rt


class Goal1440V152CollectBufferContractTest(unittest.TestCase):
    def test_contract_defines_app_generic_result_buffer_metadata(self) -> None:
        contract = rt.validate_v1_5_2_collect_buffer_contract()

        self.assertEqual(contract["status"], "python_rtdl_buffer_contract_foundation")
        self.assertIn("result", contract["buffer_kinds"])
        self.assertIn("int64", contract["dtype_scope"])
        self.assertIn("cpu", contract["device_scope"])
        self.assertIn("cuda", contract["device_scope"])
        self.assertIn("capacity", contract["required_fields"])
        self.assertIn("valid_count", contract["required_fields"])

    def test_contract_keeps_claim_boundaries_closed(self) -> None:
        contract = rt.validate_v1_5_2_collect_buffer_contract()

        for flag in (
            "true_zero_copy_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "stable_public_primitive_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(contract[flag], False)
        self.assertIn("do not authorize true zero-copy", contract["claim_boundary"])

    def test_collect_k_result_buffer_descriptor_from_reference_result(self) -> None:
        result = rt.collect_k_bounded_rows(((2, 20), (1, 10)), k=4, row_width=2)

        descriptor = rt.collect_k_result_buffer_descriptor(result, row_width=2)

        self.assertEqual(descriptor["buffer_kind"], "result")
        self.assertEqual(descriptor["dtype"], "int64")
        self.assertEqual(descriptor["layout"], "row_major_dense_candidate_id_rows")
        self.assertEqual(descriptor["shape"], (4, 2))
        self.assertEqual(descriptor["valid_shape"], (2, 2))
        self.assertEqual(descriptor["capacity"], 4)
        self.assertEqual(descriptor["valid_count"], 2)
        self.assertEqual(descriptor["copy_boundary"], "python_materialized_rows")
        self.assertIs(descriptor["true_zero_copy_authorized"], False)

    def test_collect_k_result_buffer_descriptor_allows_explicit_cuda_metadata_without_zero_copy_claim(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=2, row_width=2)

        descriptor = rt.collect_k_result_buffer_descriptor(
            result,
            row_width=2,
            device="cuda",
            owner="rtdl",
            mutability="mutable",
            copy_boundary="prepared_device_buffer_reuse",
        )

        self.assertEqual(descriptor["device"], "cuda")
        self.assertEqual(descriptor["owner"], "rtdl")
        self.assertEqual(descriptor["mutability"], "mutable")
        self.assertEqual(descriptor["copy_boundary"], "prepared_device_buffer_reuse")
        self.assertIs(descriptor["true_zero_copy_authorized"], False)

    def test_descriptor_rejects_unsupported_device_and_copy_boundary(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=1, row_width=2)

        with self.assertRaisesRegex(ValueError, "unsupported collect buffer device"):
            rt.collect_k_result_buffer_descriptor(result, row_width=2, device="metal")
        with self.assertRaisesRegex(ValueError, "unsupported collect buffer copy_boundary"):
            rt.collect_k_result_buffer_descriptor(result, row_width=2, copy_boundary="true_zero_copy")

    def test_descriptor_validator_rejects_overclaims_and_shape_mismatch(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=2, row_width=2)
        descriptor = rt.collect_k_result_buffer_descriptor(result, row_width=2)

        overclaimed = dict(descriptor)
        overclaimed["true_zero_copy_authorized"] = True
        with self.assertRaisesRegex(ValueError, "true_zero_copy_authorized=False"):
            rt.validate_collect_result_buffer_descriptor(overclaimed)

        bad_shape = dict(descriptor)
        bad_shape["shape"] = (1, 2)
        with self.assertRaisesRegex(ValueError, "shape mismatch"):
            rt.validate_collect_result_buffer_descriptor(bad_shape)

    def test_descriptor_validator_rejects_valid_count_above_capacity(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=2, row_width=2)
        descriptor = rt.collect_k_result_buffer_descriptor(result, row_width=2)
        descriptor["valid_count"] = 3

        with self.assertRaisesRegex(ValueError, "valid_count exceeds capacity"):
            rt.validate_collect_result_buffer_descriptor(descriptor)


if __name__ == "__main__":
    unittest.main()
