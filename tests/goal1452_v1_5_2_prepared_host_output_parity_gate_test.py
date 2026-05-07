from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1452V152PreparedHostOutputParityGateTest(unittest.TestCase):
    def test_gate_records_prepared_host_output_embree_optix_parity_satisfied(self) -> None:
        gate = rt.validate_v1_5_2_prepared_buffer_reuse_gate()

        self.assertEqual(gate["status"], "blocked_pending_external_review")
        self.assertIn("embree_optix_same_contract_parity", gate["satisfied_evidence"])
        self.assertNotIn("embree_optix_same_contract_parity", gate["missing_evidence"])
        self.assertEqual(gate["missing_evidence"], ("external_ai_review",))
        self.assertFalse(gate["prepared_buffer_reuse_proven"])
        self.assertFalse(gate["true_zero_copy_authorized"])
        self.assertFalse(gate["public_speedup_wording_authorized"])
        self.assertFalse(gate["release_action_authorized"])

    def test_parity_artifact_records_no_required_backend_skips(self) -> None:
        report = (
            ROOT
            / "docs/reports/goal1451_prepared_host_output_linux_gtx1070_compat_2026-05-07.md"
        ).read_text(encoding="utf-8")
        parity = (
            ROOT
            / "docs/reports/goal1451_prepared_host_output_linux_gtx1070_compat_2026-05-07"
            / "goal1450_prepared_host_output_parity_pod_required_2026-05-07.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Accepted as Linux OptiX compatibility/parity evidence", report)
        self.assertIn("Not accepted as RT-core evidence", report)
        self.assertIn("not a performance claim", parity)
        self.assertIn("embree: pass=4, fail=0, skipped=0", parity)
        self.assertIn("optix: pass=4, fail=0, skipped=0", parity)
        self.assertIn("Required backend skips: none", parity)


if __name__ == "__main__":
    unittest.main()
