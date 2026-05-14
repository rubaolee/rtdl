from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "rtdl_control_apps_cupy_rawkernel.py"
REPORT = ROOT / "docs" / "reports" / "goal1957_partner_identity_payload_contract_2026-05-14.md"
RETEST_REPORT = ROOT / "docs" / "reports" / "goal1957_partner_identity_payload_pod_retest_2026-05-14.md"
RETEST_SUMMARY = ROOT / "docs" / "reports" / "goal1957_partner_identity_payload_pod_optix_v800" / "summary.json"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal1957_claude_review_partner_identity_payload_contract_2026-05-14.md"
HANDOFF = ROOT / "HANDOFF_GOAL1957_CLAUDE_REVIEW.md"


class Goal1957PartnerIdentityPayloadContractTest(unittest.TestCase):
    def test_report_documents_general_contract_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("identity-preserving payload table", text)
        self.assertIn("RTDL discovery result -> identity-preserving payload table -> partner continuation", text)
        self.assertIn("not to special-case the polygon examples", text)
        self.assertIn("does not claim arbitrary polygon overlay acceleration", text)
        self.assertIn("does not claim true engine-level zero-copy", text)
        self.assertIn("external consensus", text)

    def test_example_uses_compact_payload_table_for_polygon_cupy_path(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn("class PartnerPairPayloadTable", text)
        self.assertIn("aabb_pair_overlap_summary_2d_partner_columns", text)
        self.assertNotIn("POLYGON_EXTENT_RAWKERNEL_SOURCE", text)
        self.assertNotIn("rtdl_user_pair_extent_summary", text)
        self.assertIn("_pair_extent_cupy_summary(pair_payload_table)", text)
        self.assertIn("candidate_and_payload_construction_sec", text)
        self.assertNotIn("_polygon_pair_cupy_summary(\n            inputs[\"left_masks\"]", text)

    def test_cpu_fallback_polygon_contract_matches_v1_8_oracles(self) -> None:
        for app in ("polygon_pair_overlap_area_rows", "polygon_set_jaccard"):
            completed = subprocess.run(
                [
                    sys.executable,
                    str(EXAMPLE),
                    "--app",
                    app,
                    "--copies",
                    "4",
                    "--partner",
                    "cpu_fallback",
                    "--candidate-backend",
                    "cpu_all_pairs",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn('"matches_v1_8_python_rtdl_oracle": true', completed.stdout)
            self.assertIn('"pair_payload_row_count"', completed.stdout)

    def test_claude_handoff_requests_independent_review(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("independent Claude", text)
        self.assertIn("Goal1957", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("docs/reviews/goal1957_claude_review_partner_identity_payload_contract_2026-05-14.md", text)

    def test_pod_retest_records_bounded_improvement(self) -> None:
        report = RETEST_REPORT.read_text(encoding="utf-8")
        summary = RETEST_SUMMARY.read_text(encoding="utf-8")
        review = CLAUDE_REVIEW.read_text(encoding="utf-8")

        self.assertIn("10.720x", report)
        self.assertIn("16.186x", report)
        self.assertIn("1.421x", report)
        self.assertIn("1.063x", report)
        self.assertIn("general arbitrary polygon overlay implementation", report)
        self.assertIn('"v2_0_release_authorized": false', summary)
        self.assertIn('"matches_v1_8_python_rtdl_oracle": true', summary)
        self.assertIn("accept-with-boundary", review)


if __name__ == "__main__":
    unittest.main()
