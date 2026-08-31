from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3894_current_scale_with_runtime_provenance_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"
EXIT_CODE = ARTIFACT_DIR / "exit_code"
REPORT = ROOT / "docs" / "reports" / "goal3894_current_scale_with_runtime_provenance_a5000_2026-06-08.md"


class Goal3894CurrentScaleWithRuntimeProvenanceA5000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_clean_a5000_scale_smoke_passes_all_rows(self) -> None:
        self.assertEqual(EXIT_CODE.read_text(encoding="utf-8").strip(), "0")
        self.assertTrue(self.summary["all_pass"])
        self.assertEqual(self.summary["json_pass_count"], 10)
        self.assertEqual(len(self.summary["rows"]), 10)
        self.assertEqual(self.summary["selected_prepared_session_residency_profile_count"], 4)

        for row in self.summary["rows"]:
            with self.subTest(row=row["row_id"]):
                self.assertEqual(row["status"], "pass")
                self.assertEqual(row["returncode"], 0)
                semantic = row["semantic_stdout_check"]
                self.assertTrue(semantic["stdout_json_parseable"])
                self.assertEqual(semantic["claim_flag_violations"], [])
                self.assertGreater(row["stdout_bytes"], 0)

    def test_runtime_environment_records_clean_source_and_a5000(self) -> None:
        env = self.summary["runtime_environment"]
        self.assertEqual(env["source_commit_short"], "506bdf3c")
        self.assertTrue(env["working_tree_clean"])
        self.assertEqual(env["git_status_short"], [])
        self.assertEqual(env["cwd"], "/root/rtdl_goal3894_runner_1780899518")
        self.assertIn("NVIDIA RTX A5000", env["nvidia_smi"])
        self.assertIn("580.126.09", env["nvidia_smi"])
        self.assertIn("python", env["python_executable"])
        self.assertIn("RTDL_OPTIX_LIBRARY", env["rt_library_env"])

    def test_rtnn_promoted_row_stays_prepared_optix_not_reuse_idiom(self) -> None:
        row_ids = {row["row_id"] for row in self.summary["rows"]}
        self.assertIn("rtnn_prepared_optix_scale_default_65536", row_ids)
        self.assertNotIn("prepared_session_reuse_idiom", row_ids)

        stdout_path = ARTIFACT_DIR / "outputs" / "rtnn_prepared_optix_scale_default_65536.stdout.json"
        payload = json.loads(stdout_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["mode"], "prepared_optix_ranked_summary")
        self.assertIn("prepared_session_residency", payload)
        self.assertFalse(payload["claim_boundary"]["automatic_partner_selection_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_claim_authorized"])

    def test_report_documents_clean_provenance_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3894",
            "506bdf3c",
            "NVIDIA RTX A5000",
            "working_tree_clean",
            "git_status_short",
            "all_pass",
            "json_pass_count",
            "not a public performance comparison",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
