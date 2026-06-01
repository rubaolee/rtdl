from __future__ import annotations

import unittest
import json
from pathlib import Path

import rtdsl as rt
from scripts import goal2941_rayjoin_row_view_partner_columns_scale_probe as probe


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2941_rayjoin_row_view_partner_columns_scale_probe_2026-06-01.md"
SCRIPT = ROOT / "scripts" / "goal2941_rayjoin_row_view_partner_columns_scale_probe.py"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2941_rayjoin_row_view_partner_columns_scale_probe_pod"
    / "goal2941_rayjoin_row_view_partner_columns_large.json"
)


class Goal2941RayJoinRowViewPartnerColumnsScaleProbeTest(unittest.TestCase):
    def test_script_uses_generic_row_view_bridge_and_keeps_claim_boundary(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("optix_row_view_to_partner_columns", source)
        self.assertIn("typed_columns_over_count_only_ratio", source)
        self.assertIn('"device_resident_handoff_claim_authorized": False', source)
        self.assertIn('"paper_reproduction_claim_authorized": False', source)
        self.assertIn("python_dict_row_materialization_used", source)

    def test_known_workload_fields_are_generic_primitive_payload_fields(self) -> None:
        self.assertEqual(("point_id", "shape_id", "membership"), probe.WORKLOAD_FIELDS["pip"])
        self.assertEqual(
            ("left_id", "right_id", "intersection_point_x", "intersection_point_y"),
            probe.WORKLOAD_FIELDS["lsi"],
        )
        self.assertEqual(
            ("left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"),
            probe.WORKLOAD_FIELDS["overlay_seed"],
        )

    def test_report_and_readiness_index(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertIn("Goal2941", text)
        self.assertIn("scale-aware Spatial RayJoin probe", text)
        self.assertIn("device-resident row-stream", text)
        self.assertIn("Overlay seed | `262144`", text)
        self.assertIn("`1.014x`", text)
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2941_rayjoin_row_view_partner_columns_scale_probe_2026-06-01.md"
            ]
        )
        self.assertIn("keep_goal2941_rayjoin_row_view_partner_columns_scale_probe_green", packet["allowed_next_actions"])
        self.assertEqual("accept", rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)["status"])

    def test_pod_artifact_records_large_scale_typed_column_overhead(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows = {row["workload"]: row for row in payload["rows"]}

        self.assertEqual("pass", payload["status"])
        self.assertEqual("b480901e45a0c47353da244b94642d3c6fdd81de", payload["source_commit"])
        self.assertEqual([], payload["source_dirty"])
        self.assertEqual("large", payload["scale"])
        self.assertEqual("cupy", payload["partner"])
        self.assertEqual(4096, rows["pip"]["expected_row_count"])
        self.assertEqual(65536, rows["lsi"]["expected_row_count"])
        self.assertEqual(262144, rows["overlay_seed"]["expected_row_count"])
        self.assertLess(rows["overlay_seed"]["typed_columns_over_count_only_ratio"], 1.05)
        self.assertLess(rows["lsi"]["typed_columns_over_count_only_ratio"], 1.35)
        self.assertFalse(rows["pip"]["python_dict_row_materialization_used"])
        self.assertFalse(payload["claim_boundary"]["device_resident_handoff_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
