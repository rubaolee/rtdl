import json
import unittest
from pathlib import Path

import rtdsl as rt


REPORTS = Path(__file__).resolve().parents[1] / "docs" / "reports"


def cuda_boundary_gate() -> dict:
    allocation = json.loads(
        (REPORTS / "goal1486_v1_5_4_cuda_driver_allocation_probe_2026-05-07.json").read_text(
            encoding="utf-8"
        )
    )["allocation_evidence"]
    copy_boundary = json.loads(
        (REPORTS / "goal1487_v1_5_4_cuda_driver_copy_boundary_probe_2026-05-07.json").read_text(
            encoding="utf-8"
        )
    )["allocation_evidence"]
    return rt.v1_5_4_managed_buffer_cuda_evidence_boundary_gate(
        allocation_evidence=allocation,
        copy_boundary_evidence=copy_boundary,
    )


def blocked_preflight() -> dict:
    return json.loads(
        (REPORTS / "goal1489_v1_5_4_optix_device_buffer_preflight_pod_2026-05-07.json").read_text(
            encoding="utf-8"
        )
    )


class Goal1491V154OptixDeviceBufferExecutionContractTest(unittest.TestCase):
    def test_contract_is_blocked_until_preflight_green(self) -> None:
        gate = rt.v1_5_4_optix_device_buffer_execution_contract_gate(
            preflight=blocked_preflight(),
            cuda_boundary_gate=cuda_boundary_gate(),
        )

        validated = rt.validate_v1_5_4_optix_device_buffer_execution_contract_gate(gate)

        self.assertEqual(validated["status"], "v1_5_4_optix_device_buffer_execution_contract_blocked_by_preflight")
        self.assertFalse(validated["preflight_valid"])
        self.assertIn("optix_header_available", validated["preflight_blockers"])
        self.assertEqual(validated["first_target_primitive"], "COLLECT_K_BOUNDED")
        self.assertIn("rtdl_optix_collect_k_bounded_i64", validated["first_target_native_symbols"])
        self.assertFalse(validated["true_zero_copy_authorized"])
        self.assertFalse(validated["public_speedup_wording_authorized"])

    def test_contract_ready_shape_after_green_preflight(self) -> None:
        preflight = blocked_preflight()
        preflight["valid_for_optix_device_buffer_execution_work"] = True
        preflight["blockers"] = []

        gate = rt.v1_5_4_optix_device_buffer_execution_contract_gate(
            preflight=preflight,
            cuda_boundary_gate=cuda_boundary_gate(),
        )
        validated = rt.validate_v1_5_4_optix_device_buffer_execution_contract_gate(gate)

        self.assertEqual(validated["status"], "v1_5_4_optix_device_buffer_execution_contract_ready")
        self.assertTrue(validated["preflight_valid"])
        self.assertIn("same_deduplicated_lexicographic_rows", validated["required_parity"])
        self.assertIn(
            "allocation_only_transfers_distinguished_from_content_transfers",
            validated["required_transfer_accounting"],
        )

    def test_rejects_claim_expansion(self) -> None:
        gate = rt.v1_5_4_optix_device_buffer_execution_contract_gate(
            preflight=blocked_preflight(),
            cuda_boundary_gate=cuda_boundary_gate(),
        )
        gate["true_zero_copy_authorized"] = True

        with self.assertRaisesRegex(ValueError, "true_zero_copy_authorized=False"):
            rt.validate_v1_5_4_optix_device_buffer_execution_contract_gate(gate)


if __name__ == "__main__":
    unittest.main()
