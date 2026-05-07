import json
import unittest
from pathlib import Path

import rtdsl as rt


REPORTS = Path(__file__).resolve().parents[1] / "docs" / "reports"


def load_evidence(name: str) -> dict:
    payload = json.loads((REPORTS / name).read_text(encoding="utf-8"))
    return payload["allocation_evidence"]


class Goal1488V154CudaEvidenceBoundaryGateTest(unittest.TestCase):
    def test_accepts_goal1486_allocation_and_goal1487_copy_boundary(self) -> None:
        gate = rt.v1_5_4_managed_buffer_cuda_evidence_boundary_gate(
            allocation_evidence=load_evidence("goal1486_v1_5_4_cuda_driver_allocation_probe_2026-05-07.json"),
            copy_boundary_evidence=load_evidence("goal1487_v1_5_4_cuda_driver_copy_boundary_probe_2026-05-07.json"),
        )

        validated = rt.validate_v1_5_4_managed_buffer_cuda_evidence_boundary_gate(gate)

        self.assertTrue(validated["accepted_boundary"])
        self.assertTrue(validated["allocation_only_candidate"])
        self.assertTrue(validated["allocation_only_zero_transfers"])
        self.assertFalse(validated["copy_boundary_candidate"])
        self.assertTrue(validated["copy_boundary_has_counted_transfers"])
        self.assertIn("end_to_end_rtdl_optix_device_buffer_execution", validated["not_proven"])
        self.assertFalse(validated["true_zero_copy_authorized"])
        self.assertFalse(validated["public_speedup_wording_authorized"])

    def test_rejects_copy_boundary_as_allocation_only_evidence(self) -> None:
        copy_evidence = load_evidence("goal1487_v1_5_4_cuda_driver_copy_boundary_probe_2026-05-07.json")
        gate = rt.v1_5_4_managed_buffer_cuda_evidence_boundary_gate(
            allocation_evidence=copy_evidence,
            copy_boundary_evidence=copy_evidence,
        )

        with self.assertRaisesRegex(ValueError, "not accepted"):
            rt.validate_v1_5_4_managed_buffer_cuda_evidence_boundary_gate(gate)

    def test_rejects_claim_expansion(self) -> None:
        gate = rt.v1_5_4_managed_buffer_cuda_evidence_boundary_gate(
            allocation_evidence=load_evidence("goal1486_v1_5_4_cuda_driver_allocation_probe_2026-05-07.json"),
            copy_boundary_evidence=load_evidence("goal1487_v1_5_4_cuda_driver_copy_boundary_probe_2026-05-07.json"),
        )
        gate["public_speedup_wording_authorized"] = True

        with self.assertRaisesRegex(ValueError, "public_speedup_wording_authorized=False"):
            rt.validate_v1_5_4_managed_buffer_cuda_evidence_boundary_gate(gate)


if __name__ == "__main__":
    unittest.main()
