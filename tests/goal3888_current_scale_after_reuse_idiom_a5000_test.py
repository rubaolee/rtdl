from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3888_current_scale_after_reuse_idiom_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"
EXIT_CODE = ARTIFACT_DIR / "exit_code"
REPORT = ROOT / "docs" / "reports" / "goal3888_current_scale_after_reuse_idiom_a5000_2026-06-08.md"


class Goal3888CurrentScaleAfterReuseIdiomA5000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_artifact_passes_all_rows_with_clean_claim_flags(self) -> None:
        self.assertEqual(EXIT_CODE.read_text(encoding="utf-8").strip(), "0")
        self.assertTrue(self.summary["all_pass"])
        self.assertEqual(self.summary["json_pass_count"], 10)
        self.assertEqual(len(self.summary["rows"]), 10)
        self.assertEqual(self.summary["selected_prepared_session_residency_profile_count"], 4)

        for row in self.summary["rows"]:
            with self.subTest(row=row["row_id"]):
                self.assertEqual(row["status"], "pass")
                semantic = row["semantic_stdout_check"]
                self.assertTrue(semantic["stdout_json_parseable"])
                self.assertEqual(semantic["claim_flag_violations"], [])
                self.assertGreater(row["stdout_bytes"], 0)

    def test_prepared_session_profile_summary_remains_non_authorizing(self) -> None:
        profile_summary = self.summary["prepared_session_residency_summary"]
        self.assertEqual(profile_summary["app_count"], 4)
        self.assertGreater(profile_summary["geomean_prepare_to_hot_query_ratio"], 400.0)
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
        ):
            self.assertFalse(profile_summary[flag], flag)

    def test_promoted_rtnn_row_stays_benchmark_path_not_idiom_mode(self) -> None:
        row_ids = {row["row_id"] for row in self.summary["rows"]}
        self.assertIn("rtnn_prepared_optix_scale_default_65536", row_ids)
        self.assertNotIn("prepared_session_reuse_idiom", row_ids)

        stdout_path = ARTIFACT_DIR / "outputs" / "rtnn_prepared_optix_scale_default_65536.stdout.json"
        payload = json.loads(stdout_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["mode"], "prepared_optix_ranked_summary")
        self.assertIn("prepared_session_residency", payload)
        self.assertFalse(payload["claim_boundary"]["automatic_partner_selection_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_claim_authorized"])

    def test_report_documents_environment_result_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3888",
            "NVIDIA RTX A5000",
            "7c7137fa",
            "all_pass",
            "json_pass_count",
            "selected prepared-session-profiled rows",
            "not a public performance comparison",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
