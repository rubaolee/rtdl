from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2939_rayjoin_row_view_partner_columns_pod_smoke_2026-06-01.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2939_rayjoin_row_view_partner_columns_pod"
    / "goal2939_rayjoin_row_view_partner_columns.json"
)


class Goal2939RayJoinRowViewPartnerColumnsPodSmokeTest(unittest.TestCase):
    def test_rayjoin_rows_convert_to_cupy_partner_columns(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows = {row["workload"]: row for row in payload["rows"]}

        self.assertEqual("pass", payload["status"])
        self.assertEqual("fed661d370bd3ee899bc93b8b383ee7a586fbe58", payload["source_commit"])
        self.assertEqual([], payload["source_dirty"])
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertEqual("cupy", payload["partner"])
        self.assertEqual(6, rows["pip"]["observed_row_count"])
        self.assertEqual(1, rows["lsi"]["observed_row_count"])
        self.assertEqual(0, rows["overlay_seed"]["observed_row_count"])
        for row in rows.values():
            self.assertEqual("pass", row["status"])
            self.assertEqual(row["expected_row_count"], row["observed_row_count"])
            self.assertEqual("optix_row_view_to_partner_columns", row["metadata"]["adapter"])
            self.assertTrue(row["metadata"]["host_stage_copy_used"])
            self.assertFalse(row["metadata"]["python_dict_row_materialization_used"])
            self.assertFalse(row["metadata"]["true_zero_copy_claim_authorized"])

    def test_claim_boundary_and_readiness_index(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["true_zero_copy_claim_authorized"])
        self.assertFalse(boundary["device_resident_handoff_claim_authorized"])
        self.assertFalse(boundary["paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["v2_5_release_authorized"])
        self.assertFalse(boundary["native_engine_customization"])
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2939_rayjoin_row_view_partner_columns_pod_smoke_2026-06-01.md"
            ]
        )
        self.assertIn("keep_goal2939_rayjoin_row_view_partner_columns_pod_smoke_green", packet["allowed_next_actions"])
        self.assertEqual("accept", rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)["status"])

    def test_report_states_step_not_finish_line(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2939",
            "Spatial RayJoin benchmark route",
            "python_dict_row_materialization_used: false",
            "does not make the RayJoin row/overlay path fully device-resident",
            "v3 device-resident row-stream",
            "not authorize v2.5 release",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
