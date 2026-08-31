from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rtnn" / "rtdl_rtnn_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rtnn" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal3820_rtnn_prepared_optix_ranked_summary_app_mode_2026-06-07.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3820_rtnn_prepared_optix_ranked_summary_app_mode_a5000"


class Goal3820RtnnPreparedOptixRankedSummaryAppModeTest(unittest.TestCase):
    def test_cli_exposes_current_executable_mode(self) -> None:
        help_text = subprocess.check_output(
            [sys.executable, str(APP), "--help"],
            cwd=ROOT,
            text=True,
        )
        self.assertIn("prepared_optix_ranked_summary", help_text)
        self.assertIn("--point-count", help_text)
        self.assertIn("--query-batch-size", help_text)

    def test_pod_artifacts_are_pure_json_and_claim_bounded(self) -> None:
        for filename, expected_count in (
            ("rtnn_prepared_optix_4096.stdout.json", 4096),
            ("rtnn_prepared_optix_65536.stdout.json", 65536),
        ):
            text = (ARTIFACT_DIR / filename).read_text(encoding="utf-8")
            self.assertTrue(text.lstrip().startswith("{"), filename)
            payload = json.loads(text)
            runner = payload["runner_payload"]
            self.assertEqual(payload["mode"], "prepared_optix_ranked_summary")
            self.assertEqual(payload["point_count"], expected_count)
            self.assertEqual(runner["query_count"], expected_count)
            self.assertEqual(runner["search_count"], expected_count)
            self.assertTrue(runner["ok"])
            self.assertEqual(runner["result_mode"], "ranked-summary-aggregate-prepared-query-batch-float32")
            self.assertGreater(len(payload["runner_progress"]), 0)
            for key in (
                "native_engine_customization",
                "full_rtnn_paper_reproduction",
                "public_speedup_claim_authorized",
                "broad_rt_core_speedup_claim_authorized",
                "automatic_partner_selection_authorized",
                "amd_performance_claim_authorized",
            ):
                self.assertFalse(payload["claim_boundary"][key], key)

    def test_report_and_readme_document_current_command(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        for phrase in (
            "--mode prepared_optix_ranked_summary",
            "ranked-summary-aggregate-prepared-query-batch-float32",
            "pure JSON stdout",
            "full RTNN paper reproduction",
        ):
            self.assertIn(phrase, report)
        self.assertIn("--mode prepared_optix_ranked_summary", readme)
        self.assertIn("runner_progress", readme)


if __name__ == "__main__":
    unittest.main()
