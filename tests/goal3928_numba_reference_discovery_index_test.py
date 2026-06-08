from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3928_numba_reference_discovery_index_2026-06-08.md"
MATRIX = ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md"


class Goal3928NumbaReferenceDiscoveryIndexTest(unittest.TestCase):
    def test_numba_reference_index_covers_all_benchmarks_and_no_cupy_only_gap(self) -> None:
        index = rt.v2_6_numba_reference_index()

        self.assertEqual(rt.V2_6_NUMBA_REFERENCE_INDEX_VERSION, index["index_version"])
        self.assertEqual(rt.V2_6_PARTNER_CHOICE_GUIDANCE_VERSION, index["guidance_version"])
        self.assertEqual(10, index["app_count"])
        self.assertEqual(10, index["row_count"])
        self.assertEqual((), index["cupy_only_custom_partner_gaps"])
        self.assertTrue(index["all_custom_partner_apps_have_numba_reference"])
        self.assertFalse(index["automatic_partner_selection_allowed"])
        self.assertFalse(index["public_speedup_claim_authorized"])
        self.assertFalse(index["broad_partner_speedup_claim_authorized"])
        self.assertFalse(index["true_zero_copy_claim_authorized"])

    def test_custom_partner_rows_have_available_numba_reference(self) -> None:
        index = rt.v2_6_numba_reference_index()
        rows = {row["benchmark_app"]: row for row in index["rows"]}

        self.assertEqual(
            ("spatial_rayjoin", "rt_dbscan", "raydb_style", "barnes_hut", "triangle_counting"),
            index["apps_requiring_custom_partner"],
        )
        for app in index["apps_requiring_custom_partner"]:
            self.assertTrue(rows[app]["custom_partner_required"], app)
            self.assertTrue(rows[app]["numba_reference_available"], app)
            self.assertIn("Numba", rows[app]["numba_role"])
            self.assertNotEqual("", rows[app]["evidence_goal"])

        self.assertEqual("measured_numba_reference_not_default", rows["barnes_hut"]["numba_reference_status"])
        self.assertEqual("recommended_numba_reference", rows["rt_dbscan"]["numba_reference_status"])

    def test_primitive_or_no_partner_rows_are_advisory_not_blockers(self) -> None:
        index = rt.v2_6_numba_reference_index()
        rows = {row["benchmark_app"]: row for row in index["rows"]}

        self.assertEqual("numba_contract_evidence_not_default", rows["hausdorff_xhd"]["numba_reference_status"])
        self.assertFalse(rows["hausdorff_xhd"]["custom_partner_required"])
        self.assertEqual("future_optional_not_required", rows["rtnn"]["numba_reference_status"])
        for app in ("robot_collision", "contact_manifold", "librts_spatial_index"):
            self.assertFalse(rows[app]["custom_partner_required"])
            self.assertEqual("future_optional_not_required", rows[app]["numba_reference_status"])

    def test_docs_report_and_exports_mention_index(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        matrix = MATRIX.read_text(encoding="utf-8")

        self.assertTrue(hasattr(rt, "v2_6_numba_reference_index"))
        self.assertNotIn("v2_6_numba_reference_index", rt.__all__)
        self.assertIn("v2_6_numba_reference_index", report)
        self.assertIn("v2_6_numba_reference_index", matrix)
        self.assertIn("advisory only", report)
        self.assertIn("never selects a partner", matrix)


if __name__ == "__main__":
    unittest.main()
