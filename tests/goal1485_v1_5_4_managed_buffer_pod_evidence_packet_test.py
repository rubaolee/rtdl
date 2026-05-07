import importlib.util
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "goal1485_v1_5_4_managed_buffer_pod_evidence_packet.py"


def load_packet_module():
    spec = importlib.util.spec_from_file_location("goal1485_packet", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal1485V154ManagedBufferPodEvidencePacketTest(unittest.TestCase):
    def test_local_synthetic_packet_fails_closed(self) -> None:
        packet = load_packet_module()

        payload = packet.build_payload(
            buffer_kind="rtdl_device_resident",
            device="cuda:0",
            allocation_method="synthetic_contract_only",
            host_to_device_transfers=1,
            device_to_host_transfers=0,
            device_residency_observed=False,
            measured_on_real_nvidia=False,
            hardware_identity=None,
            backend_version=None,
            measurement_scope="unit_test_local_fail_closed",
        )

        evidence = rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
            payload["allocation_evidence"]
        )
        self.assertFalse(evidence["true_zero_copy_evidence_candidate"])
        self.assertFalse(payload["probe_summary"]["accepted_public_claim"])
        self.assertTrue(payload["pod_needed_for_stronger_result"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertIn("does not authorize public speedup wording", payload["claim_boundary"])

    def test_real_nvidia_zero_transfer_payload_is_candidate_only(self) -> None:
        packet = load_packet_module()

        payload = packet.build_payload(
            buffer_kind="rtdl_device_resident",
            device="cuda:0",
            allocation_method="cuda_device_alloc",
            host_to_device_transfers=0,
            device_to_host_transfers=0,
            device_residency_observed=True,
            measured_on_real_nvidia=True,
            hardware_identity="NVIDIA synthetic unit test",
            backend_version="OptiX synthetic unit test",
            measurement_scope="unit_test_real_nvidia_candidate_shape",
        )

        evidence = rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
            payload["allocation_evidence"]
        )
        self.assertTrue(evidence["true_zero_copy_evidence_candidate"])
        self.assertTrue(payload["probe_summary"]["candidate_only"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["public_speedup_wording_authorized"])
        self.assertFalse(payload["release_action_authorized"])

    def test_host_packet_cannot_become_candidate(self) -> None:
        packet = load_packet_module()

        payload = packet.build_payload(
            buffer_kind="pinned_host_staging",
            device="cpu",
            allocation_method="host_pinned_staging",
            host_to_device_transfers=0,
            device_to_host_transfers=0,
            device_residency_observed=True,
            measured_on_real_nvidia=True,
            hardware_identity="NVIDIA synthetic unit test",
            backend_version="OptiX synthetic unit test",
            measurement_scope="unit_test_host_not_candidate",
        )

        evidence = rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
            payload["allocation_evidence"]
        )
        self.assertFalse(evidence["true_zero_copy_evidence_candidate"])
        self.assertFalse(evidence["measured_device_residency"])


if __name__ == "__main__":
    unittest.main()
