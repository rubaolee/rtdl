from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4510_v3_0_m114_rtdbscan_clean_target_audit_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4510_v3_0_m114_rtdbscan_clean_target_audit_2026-06-17.md"
README = ROOT / "examples/current/research_benchmarks/rt_dbscan/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4510_m114_rtdbscan_clean_target_audit.py"


class Goal4510V30M114RtDbscanCleanTargetAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4510_m114_rtdbscan_clean_target_audit")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_compact_signature_route_is_closed_for_measured_targets(self) -> None:
        summary = self.packet["compact_signature_summary"]
        rows = self.packet["compact_signature_matrix"]

        self.assertEqual("rtdl.v3_0.rtdbscan_clean_target_audit.goal4510.v1", self.packet["version"])
        self.assertEqual(12, summary["target_row_count"])
        self.assertEqual(12, len(rows))
        self.assertTrue(summary["predicate_direct_status_wins_all_targets"])
        self.assertTrue(summary["same_contract_signatures_all_targets"])
        self.assertIn("CuPy predicate direct-status", summary["current_best_route"])
        self.assertIn("no-C++", summary["numba_role"])

        for row in rows:
            self.assertEqual("predicate_direct_status", row["winner_mode"], row)
            self.assertTrue(row["same_contract_signatures"], row)
            self.assertGreaterEqual(row["predicate_speedup_vs_grouped_numba"], 1.0, row)

        weak_row = next(
            row
            for row in rows
            if row["point_count"] == 524_288
            and row["dataset"] == "ngsim_dense"
            and row["protocol"] == "one_shot_no_warmup"
        )
        self.assertLess(weak_row["predicate_speedup_vs_grouped_numba"], 1.01)

    def test_2m_point_column_boundary_stays_narrow_and_charged(self) -> None:
        boundary = self.packet["two_m_point_column_boundary"]

        self.assertEqual(2_097_152, boundary["point_count"])
        self.assertGreater(
            boundary["road3d"]["primitive_prepare_speedup_if_columns_already_owned"],
            45.0,
        )
        self.assertLess(
            boundary["road3d"]["one_shot_app_total_speedup_vs_charged_columns"],
            1.03,
        )
        self.assertGreater(
            boundary["clustered3d"]["prepare_speedup_if_columns_already_owned"],
            120.0,
        )
        self.assertGreater(
            boundary["ngsim_dense"]["prepare_speedup_if_columns_already_owned"],
            80.0,
        )
        self.assertEqual(
            "isolated direct-status prepare profile, not full app route",
            boundary["clustered3d"]["scope"],
        )
        self.assertFalse(boundary["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(boundary["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(
            boundary["claim_boundary"]["route_promotion_authorized_from_2m_prepare_profiles"]
        )

    def test_m113_is_not_forced_onto_current_rt_dbscan_route(self) -> None:
        applicability = self.packet["m113_applicability"]
        readiness = self.packet["readiness"]

        self.assertFalse(applicability["current_route_should_use_m113"])
        self.assertIn("prepared self-query count-threshold", applicability["reason"])
        self.assertIn("future RT-DBSCAN contract", applicability["m113_future_use"])
        self.assertEqual("route confusion, not optimization", applicability["forcing_m113_now_would_be"])
        self.assertTrue(readiness["internal_v3_clean_target_closed"])
        self.assertTrue(readiness["current_route_evidence_bounded"])
        self.assertFalse(readiness["paper_reproduction_claim_authorized"])
        self.assertFalse(readiness["public_broad_dbscan_speedup_claim_authorized"])
        self.assertFalse(readiness["automatic_partner_selection_authorized"])

    def test_report_readme_index_and_script_capture_audit(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4510 / V3 M114", report)
        self.assertIn("Current route should use M113: `False`", report)
        self.assertIn("524k/1M same-contract rows", report)
        self.assertIn("Goal4510", readme)
        self.assertIn("M113 is not the current RT-DBSCAN performance path", readme)
        self.assertIn("Goal4510 RT-DBSCAN clean-target audit", index)
        self.assertIn("PACKET_VERSION", script)


if __name__ == "__main__":
    unittest.main()
