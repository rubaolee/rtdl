import unittest

import rtdsl as rt


def device_descriptor() -> dict:
    return rt.prepare_v1_5_4_device_memory_descriptor(
        memory_kind="device_resident",
        backend="optix",
        device="cuda:0",
        dtype="int64",
        shape=(16, 2),
        owner="rtdl",
        pointer=123456,
        byte_count=256,
    )


class Goal1478V154DeviceMemoryMeasurementEnvelopeTest(unittest.TestCase):
    def test_records_transfer_counts_without_authorizing_claims(self) -> None:
        measurement = rt.attach_v1_5_4_device_memory_measurement(
            device_descriptor(),
            host_to_device_transfers=1,
            device_to_host_transfers=1,
            device_residency_observed=True,
            measurement_backend="optix",
            measurement_scope="unit_test_device_descriptor",
            measured_on_real_nvidia=False,
        )

        validated = rt.validate_v1_5_4_device_memory_measurement(measurement)

        self.assertEqual(validated["host_to_device_transfers"], 1)
        self.assertEqual(validated["device_to_host_transfers"], 1)
        self.assertTrue(validated["measured_device_residency"])
        self.assertTrue(validated["measured_transfer_count"])
        self.assertFalse(validated["true_zero_copy_evidence_candidate"])
        self.assertFalse(validated["true_zero_copy_authorized"])
        self.assertFalse(validated["public_speedup_wording_authorized"])

    def test_marks_zero_transfer_real_nvidia_device_path_as_candidate_only(self) -> None:
        measurement = rt.attach_v1_5_4_device_memory_measurement(
            device_descriptor(),
            host_to_device_transfers=0,
            device_to_host_transfers=0,
            device_residency_observed=True,
            measurement_backend="optix",
            measurement_scope="synthetic_zero_transfer_shape",
            measured_on_real_nvidia=True,
        )

        validated = rt.validate_v1_5_4_device_memory_measurement(measurement)

        self.assertTrue(validated["true_zero_copy_evidence_candidate"])
        self.assertFalse(validated["true_zero_copy_authorized"])
        self.assertFalse(validated["release_action_authorized"])
        self.assertIn("without separate reviewed evidence", validated["claim_boundary"])

    def test_host_staging_measurement_never_becomes_zero_copy_candidate(self) -> None:
        descriptor = rt.prepare_v1_5_4_device_memory_descriptor(
            memory_kind="host_staging",
            backend="optix",
            device="cpu",
            dtype="int64",
            shape=(16, 2),
            owner="rtdl",
            byte_count=256,
        )
        measurement = rt.attach_v1_5_4_device_memory_measurement(
            descriptor,
            host_to_device_transfers=0,
            device_to_host_transfers=0,
            device_residency_observed=True,
            measurement_backend="optix",
            measurement_scope="synthetic_host_staging_shape",
            measured_on_real_nvidia=True,
        )

        validated = rt.validate_v1_5_4_device_memory_measurement(measurement)

        self.assertFalse(validated["zero_copy_candidate"])
        self.assertFalse(validated["measured_device_residency"])
        self.assertFalse(validated["true_zero_copy_evidence_candidate"])

    def test_rejects_negative_transfer_count(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-negative"):
            rt.attach_v1_5_4_device_memory_measurement(
                device_descriptor(),
                host_to_device_transfers=-1,
                device_to_host_transfers=0,
                device_residency_observed=True,
                measurement_backend="optix",
                measurement_scope="bad_negative_transfer",
            )

    def test_rejects_measurement_claim_expansion(self) -> None:
        measurement = rt.attach_v1_5_4_device_memory_measurement(
            device_descriptor(),
            host_to_device_transfers=0,
            device_to_host_transfers=0,
            device_residency_observed=True,
            measurement_backend="optix",
            measurement_scope="synthetic_zero_transfer_shape",
            measured_on_real_nvidia=True,
        )
        measurement["public_speedup_wording_authorized"] = True

        with self.assertRaisesRegex(ValueError, "public_speedup_wording_authorized=False"):
            rt.validate_v1_5_4_device_memory_measurement(measurement)


if __name__ == "__main__":
    unittest.main()
