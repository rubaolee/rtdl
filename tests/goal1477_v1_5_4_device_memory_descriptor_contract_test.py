import unittest

import rtdsl as rt


class Goal1477V154DeviceMemoryDescriptorContractTest(unittest.TestCase):
    def test_host_staging_descriptor_is_reduced_copy_not_zero_copy(self) -> None:
        descriptor = rt.prepare_v1_5_4_device_memory_descriptor(
            memory_kind="host_staging",
            backend="optix",
            device="cpu",
            dtype="int64",
            shape=(16, 2),
            owner="rtdl",
            byte_count=256,
        )

        validated = rt.validate_v1_5_4_device_memory_descriptor(descriptor)

        self.assertEqual(validated["copy_boundary"], "host_staging_reduced_copy")
        self.assertFalse(validated["zero_copy_candidate"])
        self.assertFalse(validated["true_zero_copy_authorized"])
        self.assertIn("not true zero-copy", validated["claim_boundary"])

    def test_device_resident_descriptor_is_unmeasured_zero_copy_candidate_only(self) -> None:
        descriptor = rt.prepare_v1_5_4_device_memory_descriptor(
            memory_kind="device_resident",
            backend="optix",
            device="cuda:0",
            dtype="int64",
            shape=(16, 2),
            owner="rtdl",
            pointer=123456,
            byte_count=256,
        )

        validated = rt.validate_v1_5_4_device_memory_descriptor(descriptor)

        self.assertEqual(validated["copy_boundary"], "device_zero_copy_candidate_unmeasured")
        self.assertTrue(validated["zero_copy_candidate"])
        self.assertFalse(validated["measured_device_residency"])
        self.assertFalse(validated["measured_transfer_count"])
        self.assertFalse(validated["true_zero_copy_authorized"])
        self.assertFalse(validated["public_speedup_wording_authorized"])

    def test_external_shareable_device_descriptor_requires_handle(self) -> None:
        descriptor = rt.prepare_v1_5_4_device_memory_descriptor(
            memory_kind="external_shareable_device",
            backend="optix",
            device="cuda:0",
            dtype="float32",
            shape=(8, 4),
            owner="partner",
            pointer=999,
            byte_count=128,
            external_handle="dlpack:capsule-placeholder",
        )

        validated = rt.validate_v1_5_4_device_memory_descriptor(descriptor)

        self.assertTrue(validated["zero_copy_candidate"])
        self.assertEqual(validated["external_handle"], "dlpack:capsule-placeholder")
        self.assertFalse(validated["partner_tensor_handoff_authorized"])

    def test_rejects_device_candidate_without_pointer(self) -> None:
        with self.assertRaisesRegex(ValueError, "require a pointer"):
            rt.prepare_v1_5_4_device_memory_descriptor(
                memory_kind="device_resident",
                backend="optix",
                device="cuda:0",
                dtype="int64",
                shape=(16, 2),
                owner="rtdl",
            )

    def test_rejects_host_staging_on_gpu_device(self) -> None:
        with self.assertRaisesRegex(ValueError, "host staging descriptors must use device='cpu'"):
            rt.prepare_v1_5_4_device_memory_descriptor(
                memory_kind="host_staging",
                backend="optix",
                device="cuda:0",
                dtype="int64",
                shape=(16, 2),
                owner="rtdl",
            )

    def test_rejects_claim_expansion_in_descriptor(self) -> None:
        descriptor = rt.prepare_v1_5_4_device_memory_descriptor(
            memory_kind="device_resident",
            backend="optix",
            device="cuda:0",
            dtype="int64",
            shape=(16, 2),
            owner="rtdl",
            pointer=123456,
            byte_count=256,
        )
        descriptor["true_zero_copy_authorized"] = True

        with self.assertRaisesRegex(ValueError, "true_zero_copy_authorized=False"):
            rt.validate_v1_5_4_device_memory_descriptor(descriptor)


if __name__ == "__main__":
    unittest.main()
