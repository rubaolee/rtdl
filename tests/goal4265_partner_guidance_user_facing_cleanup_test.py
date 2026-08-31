from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md"
GUIDE = ROOT / "docs" / "learn" / "partner_choice_for_custom_logic.md"
REPORT = ROOT / "docs" / "reports" / "goal4265_partner_guidance_user_facing_cleanup_2026-06-09.md"


class Goal4265PartnerGuidanceUserFacingCleanupTest(unittest.TestCase):
    def test_docs_split_partner_needed_from_primitive_first_rows(self) -> None:
        matrix = MATRIX.read_text(encoding="utf-8")
        guide = GUIDE.read_text(encoding="utf-8")

        self.assertIn("## Partner-Needed Continuations", matrix)
        self.assertIn("## Primitive-First Paths", matrix)
        self.assertIn("## Primitive-First Rows", guide)

        partner_section = matrix.split("## Partner-Needed Continuations", 1)[1].split(
            "## Primitive-First Paths", 1
        )[0]
        primitive_section = matrix.split("## Primitive-First Paths", 1)[1]

        self.assertIn("RayDB-style unfused grouped continuation", partner_section)
        self.assertIn("Triangle candidate-row compaction", partner_section)
        self.assertNotIn("RayDB fused count/sum", partner_section)
        self.assertNotIn("Triangle scalar answer", partner_section)

        self.assertIn("RayDB fused count/sum", primitive_section)
        self.assertIn("Triangle scalar answer", primitive_section)

    def test_triangle_scalar_path_uses_generic_engine_language(self) -> None:
        text = MATRIX.read_text(encoding="utf-8") + "\n" + GUIDE.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("triangle_counting")
        plan = rt.plan_v2_6_partner_choice("triangle_counting", "candidate_row_compact_mask")

        forbidden = (
            "native scalar triangle-count primitive",
            "native triangle-count primitive",
            "native RT graph summary mode for the scalar triangle-count route",
        )
        for phrase in forbidden:
            self.assertNotIn(phrase, text)
            self.assertNotIn(phrase, str(route))
            self.assertNotIn(phrase, str(plan))

        self.assertIn("generic RT graph relationship-count composition", text)
        self.assertIn("generic RT graph relationship-count composition", str(route))
        self.assertIn("generic RT graph relationship-count composition", str(plan))

    def test_numba_reference_index_remains_advisory_not_a_cupy_vs_numba_table(self) -> None:
        index = rt.v2_6_numba_reference_index()
        rows = {row["benchmark_app"]: row for row in index["rows"]}

        self.assertIn("raydb_style", index["apps_requiring_custom_partner"])
        self.assertIn("triangle_counting", index["apps_requiring_custom_partner"])
        self.assertEqual("recommended_numba_reference", rows["raydb_style"]["numba_reference_status"])
        self.assertEqual("recommended_numba_reference", rows["triangle_counting"]["numba_reference_status"])
        self.assertFalse(index["public_speedup_claim_authorized"])
        self.assertFalse(index["broad_partner_speedup_claim_authorized"])

    def test_report_documents_the_cleanup_scope(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal4265", report)
        self.assertIn("Partner-needed continuations", report)
        self.assertIn("Primitive-first rows", report)
        self.assertIn("native scalar triangle-count primitive", report)
        self.assertIn("generic RT graph relationship-count composition", report)
        self.assertIn("No release, public speedup, or broad partner-speedup claim", report)


if __name__ == "__main__":
    unittest.main()
