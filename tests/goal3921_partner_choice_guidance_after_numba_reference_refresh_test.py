from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3921_partner_choice_guidance_after_numba_reference_refresh_2026-06-08.md"


class Goal3921PartnerChoiceGuidanceAfterNumbaReferenceRefreshTest(unittest.TestCase):
    def test_rt_dbscan_recommends_numba_and_keeps_blocked_modes_timing_bounded(self) -> None:
        plan = rt.plan_v2_6_partner_choice("rt_dbscan", "component_labeling")

        self.assertEqual("single_recommendation", plan["status"])
        self.assertEqual("numba", plan["recommended_partner"])
        self.assertFalse(plan["auto_select_partner_allowed"])
        row = plan["matches"][0]
        self.assertIn("Numba prepared grouped-stream", row["numba_role"])
        self.assertIn("blocked", row["numba_role"])
        self.assertIn("Goal3918", row["evidence_goal"])
        self.assertIn("Goal3920", row["user_advice"])
        self.assertFalse(row["public_speedup_claim_authorized"])
        self.assertFalse(row["automatic_partner_selection_allowed"])

    def test_barnes_hut_keeps_cupy_winner_but_exposes_numba_reference(self) -> None:
        plan = rt.plan_v2_6_partner_choice("barnes_hut", "force_vector_continuation")

        self.assertEqual("cupy", plan["recommended_partner"])
        row = plan["matches"][0]
        self.assertIn("active exact force-vector", row["cupy_role"])
        self.assertIn("no-RawKernel", row["numba_role"])
        self.assertIn("Goal3837", row["evidence_goal"])
        self.assertIn("Numba", row["user_advice"])
        self.assertFalse(row["broad_partner_speedup_claim_authorized"])

    def test_report_records_non_authorizing_metadata_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("advisory metadata correction", text)
        self.assertIn("does not auto-select partners", text)
        self.assertIn("Goal3920 RT-DBSCAN blocked Numba runbook", text)


if __name__ == "__main__":
    unittest.main()
