import unittest

import rtdsl as rt


class Goal1482PythonRtdlManagedBufferDescriptorTest(unittest.TestCase):
    def test_prepared_host_descriptor_is_rtdl_owned_reduced_copy(self) -> None:
        descriptor = rt.prepare_v1_5_4_python_rtdl_managed_buffer_descriptor(
            buffer_kind="prepared_host",
            backend="optix",
            device="cpu",
            dtype="int64",
            shape=(16, 2),
            lifetime="single_call",
            byte_count=256,
        )

        validated = rt.validate_v1_5_4_python_rtdl_managed_buffer_descriptor(descriptor)

        self.assertEqual(validated["owner"], "rtdl")
        self.assertFalse(validated["partner_owned"])
        self.assertEqual(validated["copy_boundary"], "rtdl_owned_host_reduced_copy")
        self.assertEqual(validated["residency_state"], "host_resident")
        self.assertFalse(validated["device_residency_candidate"])
        self.assertFalse(validated["true_zero_copy_authorized"])

    def test_pinned_host_descriptor_uses_host_residency(self) -> None:
        descriptor = rt.prepare_v1_5_4_python_rtdl_managed_buffer_descriptor(
            buffer_kind="pinned_host_staging",
            backend="optix",
            device="cpu",
            dtype="float32",
            shape=(8, 4),
            lifetime="session",
            byte_count=128,
        )

        validated = rt.validate_v1_5_4_python_rtdl_managed_buffer_descriptor(descriptor)

        self.assertEqual(validated["residency_state"], "host_resident")
        self.assertEqual(validated["transfer_count_state"], "not_measured")
        self.assertIn("Host managed buffers are reduced-copy", validated["claim_boundary"])

    def test_device_resident_descriptor_is_unmeasured_residency_candidate(self) -> None:
        descriptor = rt.prepare_v1_5_4_python_rtdl_managed_buffer_descriptor(
            buffer_kind="rtdl_device_resident",
            backend="optix",
            device="cuda:0",
            dtype="int64",
            shape=(16, 2),
            lifetime="explicit_release",
            byte_count=256,
            pointer=123456,
            transfer_count_state="instrumentation_planned",
        )

        validated = rt.validate_v1_5_4_python_rtdl_managed_buffer_descriptor(descriptor)

        self.assertTrue(validated["device_residency_candidate"])
        self.assertEqual(validated["residency_state"], "device_candidate_unmeasured")
        self.assertEqual(validated["copy_boundary"], "rtdl_owned_device_residency_candidate_unmeasured")
        self.assertFalse(validated["managed_buffer_zero_copy_authorized"])

    def test_managed_unified_descriptor_is_unmeasured_candidate(self) -> None:
        descriptor = rt.prepare_v1_5_4_python_rtdl_managed_buffer_descriptor(
            buffer_kind="rtdl_managed_unified",
            backend="optix",
            device="cuda:0",
            dtype="uint64",
            shape=(32,),
            lifetime="session",
            byte_count=256,
            transfer_count_state="instrumentation_planned",
        )

        validated = rt.validate_v1_5_4_python_rtdl_managed_buffer_descriptor(descriptor)

        self.assertTrue(validated["device_residency_candidate"])
        self.assertEqual(validated["residency_state"], "managed_unified_candidate_unmeasured")
        self.assertEqual(validated["copy_boundary"], "rtdl_owned_managed_unified_candidate_unmeasured")

    def test_rejects_host_managed_buffer_on_gpu_device(self) -> None:
        with self.assertRaisesRegex(ValueError, "host managed buffers must use device='cpu'"):
            rt.prepare_v1_5_4_python_rtdl_managed_buffer_descriptor(
                buffer_kind="prepared_host",
                backend="optix",
                device="cuda:0",
                dtype="int64",
                shape=(16, 2),
                lifetime="single_call",
            )

    def test_rejects_partner_owned_or_claim_expansion(self) -> None:
        descriptor = rt.prepare_v1_5_4_python_rtdl_managed_buffer_descriptor(
            buffer_kind="rtdl_device_resident",
            backend="optix",
            device="cuda:0",
            dtype="int64",
            shape=(16, 2),
            lifetime="session",
            byte_count=256,
        )
        descriptor["partner_owned"] = True

        with self.assertRaisesRegex(ValueError, "must not be partner-owned"):
            rt.validate_v1_5_4_python_rtdl_managed_buffer_descriptor(descriptor)

        descriptor["partner_owned"] = False
        descriptor["true_zero_copy_authorized"] = True
        with self.assertRaisesRegex(ValueError, "true_zero_copy_authorized=False"):
            rt.validate_v1_5_4_python_rtdl_managed_buffer_descriptor(descriptor)


if __name__ == "__main__":
    unittest.main()
