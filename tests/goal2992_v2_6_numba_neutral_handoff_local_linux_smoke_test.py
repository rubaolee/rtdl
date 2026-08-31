from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2992_v2_6_numba_neutral_handoff_local_linux_smoke_2026-06-01.md"
)
ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2992_v2_6_numba_neutral_handoff_local_linux_smoke_2026-06-01.json"
)


class Goal2992NumbaNeutralHandoffLocalLinuxSmokeTest(unittest.TestCase):
    def test_report_keeps_smoke_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for required in (
            "v2.6 neutral partner handoff",
            "without using the legacy torch carrier",
            "not release evidence",
            "not performance evidence",
            "does not authorize release",
            "true-zero-copy wording",
            "CUDA pod run",
        ):
            self.assertIn(required, text)

    def test_artifact_records_successful_numba_path_without_torch(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["goal"], "Goal2991")
        self.assertIn("GTX 1070", data["gpu"])
        self.assertEqual(data["rows"], 65536)
        self.assertEqual(data["groups"], 1024)
        self.assertTrue(data["counts_match_cpu"])
        self.assertTrue(data["sums_match_cpu"])
        self.assertLess(data["max_sum_abs_error"], 1e-9)

        handoff = data["handoff"]
        self.assertEqual(handoff["selected_partner"], "numba")
        self.assertEqual(handoff["validation"]["status"], "accept")
        self.assertEqual(handoff["runtime_observed_descriptor_count"], 2)
        self.assertTrue(handoff["all_columns_device_resident"])
        self.assertTrue(handoff["all_leases_completed"])
        self.assertFalse(handoff["torch_conversion_used"])
        self.assertFalse(handoff["torch_carrier_used"])

    def test_artifact_claim_boundary_authorizes_nothing(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        for field, value in data["claim_boundary"].items():
            self.assertIs(
                value,
                False,
                msg=f"{field} must remain false for local smoke evidence",
            )

        for phase_name in ("count_phase_timing", "sum_phase_timing"):
            phase = data[phase_name]
            self.assertEqual(phase["validation"]["status"], "accept")
            self.assertFalse(phase["promoted_performance_path"])
            self.assertFalse(phase["same_phase_contract_as_basis"])


if __name__ == "__main__":
    unittest.main()
