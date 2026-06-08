from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3929_numba_reference_parity_expectations_2026-06-08.md"
MATRIX = ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md"


class Goal3929NumbaReferenceParityExpectationsTest(unittest.TestCase):
    def test_parity_expectations_cover_available_numba_references(self) -> None:
        parity = rt.v2_6_numba_parity_expectations()

        self.assertEqual(rt.V2_6_NUMBA_PARITY_EXPECTATIONS_VERSION, parity["expectations_version"])
        self.assertEqual(rt.V2_6_NUMBA_REFERENCE_INDEX_VERSION, parity["index_version"])
        self.assertEqual((), parity["missing_expectation_apps"])
        self.assertTrue(parity["all_available_numba_references_have_parity_expectations"])
        self.assertFalse(parity["automatic_partner_selection_allowed"])
        self.assertFalse(parity["public_speedup_claim_authorized"])
        self.assertFalse(parity["broad_partner_speedup_claim_authorized"])
        self.assertFalse(parity["true_zero_copy_claim_authorized"])

        apps = {row["benchmark_app"] for row in parity["rows"]}
        self.assertEqual(
            {
                "hausdorff_xhd",
                "spatial_rayjoin",
                "rt_dbscan",
                "raydb_style",
                "barnes_hut",
                "triangle_counting",
            },
            apps,
        )

    def test_each_custom_partner_row_names_oracle_or_tolerance_and_evidence(self) -> None:
        parity = rt.v2_6_numba_parity_expectations()

        for row in parity["rows"]:
            self.assertNotEqual("", row["parity_requirement"])
            self.assertRegex(row["parity_requirement"], r"(match|oracle|tolerance|preserve)")
            self.assertIn("Goal", row["parity_evidence"])
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["automatic_partner_selection_allowed"])

        rows = {row["benchmark_app"]: row for row in parity["rows"]}
        self.assertIn("pending_goal3920", rows["rt_dbscan"]["parity_status"])
        self.assertIn("CPU mask oracle", rows["triangle_counting"]["parity_requirement"])
        self.assertIn("exact force-vector tolerance", rows["barnes_hut"]["parity_requirement"])

    def test_report_docs_and_exports_index_the_helper(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        matrix = MATRIX.read_text(encoding="utf-8")

        self.assertTrue(hasattr(rt, "v2_6_numba_parity_expectations"))
        self.assertNotIn("v2_6_numba_parity_expectations", rt.__all__)
        self.assertIn("v2_6_numba_parity_expectations", report)
        self.assertIn("v2_6_numba_parity_expectations", matrix)
        self.assertIn("does not run new pod tests", report)
        self.assertIn("RT-DBSCAN blocked-mode A5000 timing", matrix)


if __name__ == "__main__":
    unittest.main()
