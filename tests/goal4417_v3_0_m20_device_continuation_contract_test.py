from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/rtdsl/v3_0_m20_device_continuation_contract.py"
REPORT = ROOT / "docs/reports/goal4417_v3_0_m20_device_continuation_contract_2026-06-15.md"


class Goal4417V30M20DeviceContinuationContractTest(unittest.TestCase):
    def test_packet_covers_every_promoted_app_with_expected_state_counts(self) -> None:
        payload = rt.v3_m20_device_continuation_contract_packet()
        validation = rt.validate_v3_m20_device_continuation_contract_packet(payload)
        rows = tuple(payload["app_audit_rows"])
        apps = {str(row["app"]) for row in rows}

        self.assertEqual(set(V2_8_PROMOTED_BENCHMARK_APPS), apps)
        self.assertEqual(len(V2_8_PROMOTED_BENCHMARK_APPS), validation["row_count"])
        self.assertEqual(
            {
                "clean_device_continuation_evidence_ready": 1,
                "primitive_only_no_partner_needed": 4,
                "needs_fused_or_prepared_device_continuation_bridge": 4,
                "currently_not_a_rt_core_claim_target": 1,
            },
            validation["state_counts"],
        )

    def test_phases_define_prepared_native_output_to_partner_finalize_contract(self) -> None:
        phases = rt.v3_m20_device_continuation_phases()
        self.assertEqual(
            (
                "prepared_native_producer",
                "device_payload_handoff",
                "ordered_partner_device_continuation",
                "explicit_finalize",
            ),
            tuple(str(phase["phase_id"]) for phase in phases),
        )
        handoff = {str(phase["phase_id"]): phase for phase in phases}
        self.assertIn("prepared or explicitly resident", handoff["prepared_native_producer"]["required_property"])
        self.assertIn("typed device payload columns", handoff["device_payload_handoff"]["required_property"])
        self.assertIn("same stream", handoff["ordered_partner_device_continuation"]["required_property"])
        self.assertIn("no named-column H2D", handoff["ordered_partner_device_continuation"]["measured_window_role"])
        self.assertIn("reported separately", handoff["explicit_finalize"]["measured_window_role"])

    def test_audit_rows_make_partner_position_and_next_action_explicit(self) -> None:
        rows = {str(row["app"]): row for row in rt.v3_m20_device_continuation_audit_rows()}
        self.assertEqual("clean_device_continuation_evidence_ready", rows["rtnn"]["state"])
        self.assertIn("CuPy", rows["rtnn"]["partner_position"])
        self.assertIn("Numba", rows["rtnn"]["partner_position"])
        self.assertEqual(
            "needs_fused_or_prepared_device_continuation_bridge",
            rows["spatial_rayjoin"]["state"],
        )
        self.assertEqual(
            ("lsi_scalar_count", "pip_scalar_count", "overlay_lsi_point_location_compose"),
            rows["spatial_rayjoin"]["detail_rows"],
        )
        self.assertEqual("primitive_only_no_partner_needed", rows["robot_collision"]["state"])
        self.assertEqual("primitive_only_no_partner_needed", rows["contact_manifold"]["state"])
        self.assertEqual("primitive_only_no_partner_needed", rows["raydb_style"]["state"])
        self.assertEqual("primitive_only_no_partner_needed", rows["librts_spatial_index"]["state"])
        self.assertEqual("currently_not_a_rt_core_claim_target", rows["triangle_counting"]["state"])
        for row in rows.values():
            self.assertTrue(row["current_best_contract"])
            self.assertTrue(row["partner_position"])
            self.assertTrue(row["evidence_refs"])
            self.assertTrue(row["next_action"])

    def test_claim_boundary_and_rows_do_not_authorize_public_speedup_claims(self) -> None:
        payload = rt.v3_m20_device_continuation_contract_packet()
        for flag in rt.V3_M20_FORBIDDEN_CLAIM_FLAGS:
            self.assertFalse(payload["claim_boundary"][flag], flag)
            for row in payload["app_audit_rows"]:
                self.assertFalse(row[flag], f"{row['app']} unexpectedly authorized {flag}")
        self.assertFalse(payload["summary"]["public_claim_authorized"])

    def test_validator_rejects_public_claim_authorization(self) -> None:
        payload = rt.v3_m20_device_continuation_contract_packet()
        payload["claim_boundary"] = dict(payload["claim_boundary"])
        payload["claim_boundary"]["rt_core_speedup_claim_authorized"] = True
        with self.assertRaisesRegex(GraphValidationError, "rt_core_speedup"):
            rt.validate_v3_m20_device_continuation_contract_packet(payload)

    def test_validator_rejects_duplicate_or_missing_audit_rows(self) -> None:
        payload = rt.v3_m20_device_continuation_contract_packet()
        rows = tuple(dict(row) for row in payload["app_audit_rows"])
        payload["app_audit_rows"] = (*rows[:-1], dict(rows[0]))
        with self.assertRaisesRegex(GraphValidationError, "unique"):
            rt.validate_v3_m20_device_continuation_contract_packet(payload)

    def test_module_and_report_state_internal_claim_boundary(self) -> None:
        module = MODULE.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("prepared_native_device_payload_ordered_partner_finalize_v1", module)
        self.assertIn("V3_M20_FORBIDDEN_CLAIM_FLAGS", module)
        self.assertIn("not a public performance claim", module)
        self.assertIn("M20 conclusion", report)
        self.assertIn("10/10 promoted benchmark apps", report)
        self.assertIn("no public speedup claim", report)
        self.assertIn("prepared native output -> partner device continuation -> explicit finalize", report)
        self.assertIn("| RTNN | clean_device_continuation_evidence_ready |", report)
        self.assertIn("| Spatial RayJoin | needs_fused_or_prepared_device_continuation_bridge |", report)


if __name__ == "__main__":
    unittest.main()
