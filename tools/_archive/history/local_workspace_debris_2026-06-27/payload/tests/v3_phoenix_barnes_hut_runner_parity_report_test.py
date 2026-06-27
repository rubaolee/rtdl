from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_barnes_hut_runner_parity_pod_ab_fixed_20260622_182718"
    / "summary.json"
)
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_step1_barnes_hut_runner_parity_pod_ab_2026-06-22.md"
INITIAL_REVIEW = ROOT / "docs" / "reviews" / "second_ai_phoenix_v3_barnes_hut_runner_initial_review_2026-06-22.md"
FIXED_REVIEW = ROOT / "docs" / "reviews" / "second_ai_phoenix_v3_barnes_hut_runner_fixed_review_2026-06-22.md"


class V3PhoenixBarnesHutRunnerParityReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.summary = cls.payload["summary"]
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.initial_review = INITIAL_REVIEW.read_text(encoding="utf-8")
        cls.fixed_review = FIXED_REVIEW.read_text(encoding="utf-8")

    def test_fixed_evidence_passes_strict_step1_candidate_gates(self) -> None:
        self.assertEqual(self.payload["failed_checks"], [])
        self.assertTrue(all(self.payload["checks"].values()))
        self.assertTrue(self.summary["runner_parity_with_existing_fused_partner"])
        self.assertTrue(self.summary["historical_reference_material"])
        self.assertTrue(self.summary["step1_replacement_candidate"])
        self.assertTrue(self.summary["runtime_sourced_material_gain"])
        self.assertAlmostEqual(self.summary["runner_vs_existing_fused_control_geomean"], 0.999328063165968)
        self.assertAlmostEqual(self.summary["historical_optix_over_runner_geomean"], 12.730691398985789)

    def test_equivalence_rows_pass_all_sizes(self) -> None:
        rows = {row["body_count"]: row for row in self.summary["runner_control_equivalence_rows"]}
        self.assertEqual(set(rows), {32768, 65536, 131072})
        for row in rows.values():
            self.assertTrue(row["equivalence_pass"])
            self.assertTrue(row["contribution_count_match"])
            self.assertTrue(row["checksum_force_x_match"])
            self.assertTrue(row["checksum_force_y_match"])

    def test_report_keeps_claim_boundary_and_provenance(self) -> None:
        for phrase in (
            "not release",
            "Historical reference",
            "no-go reference only",
            "not evidence that the runner wrapper itself is faster",
            "git_commit: null",
            "Remote source tree",
            "authorizes no Phoenix V3 release",
            "no broad V3-over-V2.x wording",
            "no all-app pod run",
        ):
            self.assertIn(phrase, self.report)
        self.assertNotIn("release_ready", self.report)

    def test_second_ai_reviews_are_recorded(self) -> None:
        self.assertIn("`blocked_needs_fix`", self.initial_review)
        self.assertIn("`accept_ready_for_pod_report`", self.fixed_review)
        self.assertIn("Remaining Blockers", self.fixed_review)
        self.assertIn("None before recording", self.fixed_review)


if __name__ == "__main__":
    unittest.main()
