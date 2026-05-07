from pathlib import Path
import json
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
POD_RESULT_DIR = ROOT / "docs" / "reports" / "goal1467_v1_5_3_typed_host_buffer_pod_results_2026-05-07"
POD_JSON = POD_RESULT_DIR / "goal1467_typed_host_buffer_parity_required_2026-05-07.json"


class Goal1470V153TypedHostPodParityAcceptanceTest(unittest.TestCase):
    def test_pod_payload_is_accepted_by_fail_closed_checker(self) -> None:
        payload = json.loads(POD_JSON.read_text(encoding="utf-8"))

        result = rt.validate_v1_5_3_typed_host_pod_parity_payload(payload)

        self.assertTrue(result["accepted"])
        self.assertTrue(result["backend_parity_where_claimed_satisfied"])
        self.assertEqual(payload["backend_summary"]["embree"], {"fail": 0, "pass": 4, "skipped": 0})
        self.assertEqual(payload["backend_summary"]["optix"], {"fail": 0, "pass": 4, "skipped": 0})

    def test_parity_gate_is_accepted_but_claims_remain_blocked(self) -> None:
        gate = rt.validate_v1_5_3_typed_host_buffer_parity_gate()

        self.assertTrue(gate["accepted"])
        self.assertTrue(gate["required_pod_parity_accepted"])
        self.assertEqual(gate["contract_missing_evidence"], ())
        self.assertFalse(gate["true_zero_copy_authorized"])
        self.assertFalse(gate["public_speedup_wording_authorized"])
        self.assertFalse(gate["stable_public_primitive_authorized"])
        self.assertFalse(gate["release_action_authorized"])

    def test_required_pod_artifacts_exist(self) -> None:
        for relative_path in rt.V1_5_3_TYPED_HOST_PARITY_REQUIRED_EVIDENCE:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())


if __name__ == "__main__":
    unittest.main()
