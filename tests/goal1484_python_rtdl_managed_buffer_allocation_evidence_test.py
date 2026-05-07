import unittest

import rtdsl as rt


def lifecycle_for(buffer_kind: str, device: str, allocation_id: str) -> dict:
    descriptor = rt.prepare_v1_5_4_python_rtdl_managed_buffer_descriptor(
        buffer_kind=buffer_kind,
        backend="optix",
        device=device,
        dtype="int64",
        shape=(16, 2),
        lifetime="explicit_release",
        byte_count=256,
        pointer=123456 if device != "cpu" else None,
        transfer_count_state="instrumentation_planned",
    )
    return rt.begin_v1_5_4_python_rtdl_managed_buffer_lifecycle(
        descriptor,
        allocation_id=allocation_id,
    )


class Goal1484PythonRtdlManagedBufferAllocationEvidenceTest(unittest.TestCase):
    def test_host_allocation_evidence_never_becomes_zero_copy_candidate(self) -> None:
        evidence = rt.attach_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
            lifecycle_for("pinned_host_staging", "cpu", "host-alloc-1"),
            allocation_method="host_pinned_staging",
            measurement_backend="optix",
            measurement_scope="synthetic_host_allocation",
            host_to_device_transfers=0,
            device_to_host_transfers=0,
            device_residency_observed=True,
            measured_on_real_nvidia=True,
            hardware_identity="synthetic-rtx",
        )

        validated = rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(evidence)

        self.assertFalse(validated["measured_device_residency"])
        self.assertFalse(validated["true_zero_copy_evidence_candidate"])
        self.assertFalse(validated["true_zero_copy_authorized"])

    def test_real_nvidia_zero_transfer_device_path_is_candidate_only(self) -> None:
        evidence = rt.attach_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
            lifecycle_for("rtdl_device_resident", "cuda:0", "device-alloc-1"),
            allocation_method="cuda_device_alloc",
            measurement_backend="optix",
            measurement_scope="synthetic_zero_transfer_device_allocation",
            host_to_device_transfers=0,
            device_to_host_transfers=0,
            device_residency_observed=True,
            measured_on_real_nvidia=True,
            hardware_identity="NVIDIA synthetic contract",
            backend_version="OptiX synthetic contract",
        )

        validated = rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(evidence)

        self.assertTrue(validated["measured_device_residency"])
        self.assertTrue(validated["true_zero_copy_evidence_candidate"])
        self.assertFalse(validated["managed_buffer_zero_copy_authorized"])
        self.assertFalse(validated["public_speedup_wording_authorized"])
        self.assertIn("does not authorize true zero-copy wording", validated["claim_boundary"])

    def test_non_nvidia_or_nonzero_transfer_device_path_is_not_candidate(self) -> None:
        lifecycle = lifecycle_for("rtdl_device_resident", "cuda:0", "device-alloc-2")

        not_real_nvidia = rt.attach_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
            lifecycle,
            allocation_method="cuda_device_alloc",
            measurement_backend="optix",
            measurement_scope="synthetic_not_real_nvidia",
            host_to_device_transfers=0,
            device_to_host_transfers=0,
            device_residency_observed=True,
            measured_on_real_nvidia=False,
        )
        nonzero_transfer = rt.attach_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
            lifecycle,
            allocation_method="cuda_device_alloc",
            measurement_backend="optix",
            measurement_scope="synthetic_nonzero_transfer",
            host_to_device_transfers=1,
            device_to_host_transfers=0,
            device_residency_observed=True,
            measured_on_real_nvidia=True,
        )

        self.assertFalse(
            rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(not_real_nvidia)[
                "true_zero_copy_evidence_candidate"
            ]
        )
        self.assertFalse(
            rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(nonzero_transfer)[
                "true_zero_copy_evidence_candidate"
            ]
        )

    def test_rejects_invalid_counts_method_or_claim_expansion(self) -> None:
        lifecycle = lifecycle_for("rtdl_device_resident", "cuda:0", "device-alloc-3")

        with self.assertRaisesRegex(ValueError, "allocation method"):
            rt.attach_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
                lifecycle,
                allocation_method="partner_external_alloc",
                measurement_backend="optix",
                measurement_scope="bad_method",
                host_to_device_transfers=0,
                device_to_host_transfers=0,
                device_residency_observed=True,
            )
        with self.assertRaisesRegex(ValueError, "non-negative"):
            rt.attach_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
                lifecycle,
                allocation_method="cuda_device_alloc",
                measurement_backend="optix",
                measurement_scope="bad_count",
                host_to_device_transfers=-1,
                device_to_host_transfers=0,
                device_residency_observed=True,
            )

        evidence = rt.attach_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
            lifecycle,
            allocation_method="cuda_device_alloc",
            measurement_backend="optix",
            measurement_scope="claim_expansion",
            host_to_device_transfers=0,
            device_to_host_transfers=0,
            device_residency_observed=True,
            measured_on_real_nvidia=True,
        )
        evidence["true_zero_copy_authorized"] = True

        with self.assertRaisesRegex(ValueError, "true_zero_copy_authorized=False"):
            rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(evidence)


if __name__ == "__main__":
    unittest.main()
