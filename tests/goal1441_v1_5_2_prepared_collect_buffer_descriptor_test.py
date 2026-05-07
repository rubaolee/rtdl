import unittest

import rtdsl as rt


class Goal1441V152PreparedCollectBufferDescriptorTest(unittest.TestCase):
    def test_contract_exposes_prepared_result_buffer_scope(self) -> None:
        contract = rt.validate_v1_5_2_collect_buffer_contract()

        self.assertIn("prepared_result", contract["buffer_kinds"])
        self.assertIn("rtdl", contract["owner_scope"])
        self.assertIn("native", contract["owner_scope"])
        self.assertIn("mutable", contract["mutability_scope"])

    def test_prepared_descriptor_declares_empty_mutable_output_buffer(self) -> None:
        descriptor = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=8,
            row_width=2,
            backend="embree",
        )

        self.assertEqual(descriptor["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(descriptor["buffer_kind"], "prepared_result")
        self.assertEqual(descriptor["shape"], (8, 2))
        self.assertEqual(descriptor["valid_shape"], (0, 2))
        self.assertEqual(descriptor["capacity"], 8)
        self.assertEqual(descriptor["valid_count"], 0)
        self.assertEqual(descriptor["owner"], "rtdl")
        self.assertEqual(descriptor["mutability"], "mutable")
        self.assertEqual(descriptor["copy_boundary"], "prepared_host_buffer_reuse")
        self.assertIs(descriptor["prepared_before_execution"], True)
        self.assertIs(descriptor["true_zero_copy_authorized"], False)

    def test_prepared_cuda_descriptor_is_metadata_not_zero_copy_claim(self) -> None:
        descriptor = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=4,
            row_width=3,
            backend="optix",
            device="cuda",
            owner="native",
            copy_boundary="prepared_device_buffer_reuse",
        )

        self.assertEqual(descriptor["device"], "cuda")
        self.assertEqual(descriptor["owner"], "native")
        self.assertEqual(descriptor["copy_boundary"], "prepared_device_buffer_reuse")
        self.assertIs(descriptor["true_zero_copy_authorized"], False)
        self.assertIs(descriptor["whole_app_speedup_claim_authorized"], False)

    def test_prepared_descriptor_rejects_invalid_capacity_dimensions_and_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid dimensions"):
            rt.prepare_collect_k_result_buffer_descriptor(capacity=-1, row_width=2)
        with self.assertRaisesRegex(ValueError, "invalid dimensions"):
            rt.prepare_collect_k_result_buffer_descriptor(capacity=1, row_width=0)
        with self.assertRaisesRegex(ValueError, "invalid owner"):
            rt.prepare_collect_k_result_buffer_descriptor(capacity=1, row_width=2, owner="app")
        with self.assertRaisesRegex(ValueError, "invalid mutability"):
            rt.prepare_collect_k_result_buffer_descriptor(capacity=1, row_width=2, mutability="shared")

    def test_result_descriptor_now_rejects_unknown_owner_and_mutability(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=1, row_width=2)

        with self.assertRaisesRegex(ValueError, "invalid owner"):
            rt.collect_k_result_buffer_descriptor(result, row_width=2, owner="app")
        with self.assertRaisesRegex(ValueError, "invalid mutability"):
            rt.collect_k_result_buffer_descriptor(result, row_width=2, mutability="shared")


if __name__ == "__main__":
    unittest.main()
