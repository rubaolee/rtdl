from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3925_numba_custom_partner_coverage_after_local_smokes_2026-06-08.md"


class Goal3925NumbaCustomPartnerCoverageAfterLocalSmokesTest(unittest.TestCase):
    def test_guidance_has_no_cupy_only_recommended_custom_partner(self) -> None:
        guidance = rt.v2_6_partner_choice_guidance()

        self.assertEqual(10, guidance["app_count"])
        for row in guidance["rows"]:
            recommended = row["recommended_partner"]
            if recommended == "cupy":
                self.assertIn("numba", row["numba_role"].lower())
                self.assertRegex(row["numba_role"].lower(), r"(measured|reference)")
                self.assertFalse(row["automatic_partner_selection_allowed"])
                self.assertFalse(row["broad_partner_speedup_claim_authorized"])

    def test_numba_recommended_rows_have_non_future_evidence(self) -> None:
        guidance = rt.v2_6_partner_choice_guidance()
        rows = {row["benchmark_app"]: row for row in guidance["rows"]}
        expected_numba_apps = {
            "spatial_rayjoin",
            "rt_dbscan",
            "raydb_style",
            "triangle_counting",
        }

        self.assertEqual(expected_numba_apps, {app for app, row in rows.items() if row["recommended_partner"] == "numba"})
        for app in expected_numba_apps:
            row = rows[app]
            self.assertIn("Numba", row["numba_role"])
            self.assertNotIn("future candidate", row["numba_role"].lower())
            self.assertNotEqual("", row["evidence_goal"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["automatic_partner_selection_allowed"])

    def test_primitive_or_no_partner_rows_are_not_custom_partner_blockers(self) -> None:
        guidance = rt.v2_6_partner_choice_guidance()
        rows = {row["benchmark_app"]: row for row in guidance["rows"]}

        for app in ("robot_collision", "contact_manifold", "librts_spatial_index"):
            self.assertEqual("none", rows[app]["recommended_partner"])
            self.assertIn("No partner", REPORT.read_text(encoding="utf-8"))
        for app in ("hausdorff_xhd", "rtnn"):
            self.assertEqual("rtdl_primitive", rows[app]["recommended_partner"])
            self.assertIn(app, REPORT.read_text(encoding="utf-8"))

    def test_report_records_local_smokes_and_non_authorization(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "GTX 1070",
            "not release performance evidence",
            "optix_rt_core_grouped_stream_numba_column_signature_3d",
            "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d",
            "32,768 candidate rows",
            "CPU parity true",
            "Goal3923",
            "does not add native engine",
            "auto-select partners",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
