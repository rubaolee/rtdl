import importlib.util
import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "goal1487_v1_5_4_cuda_driver_copy_boundary_probe.py"


def load_probe_module():
    spec = importlib.util.spec_from_file_location("goal1487_probe", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal1487V154CudaDriverCopyBoundaryProbeTest(unittest.TestCase):
    def test_successful_copy_boundary_probe_is_not_zero_copy_candidate(self) -> None:
        probe_module = load_probe_module()
        payload = probe_module.build_payload(
            {
                "status": "ok",
                "reason": None,
                "cuda_driver_loaded": True,
                "device_count": 1,
                "device_name": "NVIDIA synthetic unit test",
                "cuda_driver_version": 12040,
                "row_count": 4,
                "byte_count": 64,
                "device_allocation_performed": True,
                "device_free_performed": True,
                "host_to_device_transfers": 1,
                "device_to_host_transfers": 1,
                "device_residency_observed": True,
                "roundtrip_matches": True,
                "input_flat": (1, 10, 2, 20, 3, 30, 4, 40),
                "observed_flat": (1, 10, 2, 20, 3, 30, 4, 40),
                "measured_on_real_nvidia": True,
                "hardware_identity": "NVIDIA synthetic unit test driver_api=12040",
                "backend_version": "CUDA Driver API 12040",
                "device_pointer_nonzero": True,
            }
        )

        evidence = rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
            payload["allocation_evidence"]
        )
        self.assertFalse(payload["candidate_only"])
        self.assertFalse(evidence["true_zero_copy_evidence_candidate"])
        self.assertTrue(payload["content_roundtrip_verified"])
        self.assertEqual(evidence["host_to_device_transfers"], 1)
        self.assertEqual(evidence["device_to_host_transfers"], 1)
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertIn("not a true zero-copy evidence candidate", payload["claim_boundary"])

    def test_failed_probe_fails_closed(self) -> None:
        probe_module = load_probe_module()
        payload = probe_module.build_payload(
            {
                "status": "unavailable",
                "reason": "unit test no driver",
                "cuda_driver_loaded": False,
                "device_allocation_performed": False,
                "device_free_performed": False,
                "host_to_device_transfers": 0,
                "device_to_host_transfers": 0,
                "device_residency_observed": False,
                "roundtrip_matches": False,
                "measured_on_real_nvidia": False,
                "hardware_identity": None,
                "backend_version": None,
                "device_pointer_nonzero": False,
            }
        )

        evidence = rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
            payload["allocation_evidence"]
        )
        self.assertFalse(payload["content_roundtrip_verified"])
        self.assertFalse(evidence["true_zero_copy_evidence_candidate"])
        self.assertFalse(payload["public_speedup_wording_authorized"])

    def test_copy_boundary_payload_survives_json_roundtrip(self) -> None:
        probe_module = load_probe_module()
        payload = probe_module.build_payload(
            {
                "status": "ok",
                "reason": None,
                "cuda_driver_loaded": True,
                "device_count": 1,
                "device_name": "NVIDIA synthetic unit test",
                "cuda_driver_version": 12040,
                "row_count": 4,
                "byte_count": 64,
                "device_allocation_performed": True,
                "device_free_performed": True,
                "host_to_device_transfers": 1,
                "device_to_host_transfers": 1,
                "device_residency_observed": True,
                "roundtrip_matches": True,
                "input_flat": (1, 10, 2, 20, 3, 30, 4, 40),
                "observed_flat": (1, 10, 2, 20, 3, 30, 4, 40),
                "measured_on_real_nvidia": True,
                "hardware_identity": "NVIDIA synthetic unit test driver_api=12040",
                "backend_version": "CUDA Driver API 12040",
                "device_pointer_nonzero": True,
            }
        )
        roundtripped = json.loads(json.dumps(payload))

        evidence = rt.validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
            roundtripped["allocation_evidence"]
        )

        self.assertFalse(evidence["true_zero_copy_evidence_candidate"])


if __name__ == "__main__":
    unittest.main()
