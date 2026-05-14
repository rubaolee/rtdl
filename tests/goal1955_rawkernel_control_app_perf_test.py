from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1955_rawkernel_control_app_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal1955_rawkernel_control_app_local_linux_perf_2026-05-13.md"


class Goal1955RawKernelControlAppPerfTest(unittest.TestCase):
    def test_runner_cpu_fallback_writes_reviewable_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = pathlib.Path(tmp) / "perf.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--apps",
                    "database_analytics,graph_analytics",
                    "--copies",
                    "2",
                    "--partner",
                    "cpu_fallback",
                    "--repeats",
                    "1",
                    "--warmups",
                    "0",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)

            self.assertEqual(payload["goal"], "Goal1955")
            self.assertTrue(payload["all_match_v1_8_python_rtdl_oracle"])
            self.assertFalse(payload["claim_boundary"]["local_linux_gtx1070_is_release_perf_evidence"])
            self.assertTrue(payload["claim_boundary"]["comparison_is_not_absolutely_fair"])
            self.assertTrue(payload["claim_boundary"]["requires_pod_for_release_timing"])
            self.assertEqual(len(payload["results"]), 2)
            self.assertTrue(output.exists())
            for result in payload["results"]:
                self.assertTrue(result["matches_v1_8_python_rtdl_oracle"])
                self.assertIn("v1_8_python_rtdl_wall", result)
                self.assertIn("v2_rawkernel_wall", result)
                self.assertIn("v2_vs_v1_8_ratio", result)
                self.assertIn("sha256", result["v1_8_payload_signature"])
                self.assertIn("sha256", result["v2_payload_signature"])
                self.assertNotIn("v1_8_payload", result)
                self.assertNotIn("v2_payload", result)

    def test_script_declares_default_control_app_scales_and_boundary(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("DEFAULT_COPIES", text)
        self.assertIn("local_linux_gtx1070_is_release_perf_evidence", text)
        self.assertIn("requires_pod_for_release_timing", text)
        self.assertIn("payload_signature", text)
        self.assertIn("list_length", text)
        self.assertIn("not absolutely fair", text)

    def test_local_linux_report_documents_rawkernel_perf_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("local-linux-smoke-complete", text)
        self.assertIn("GTX 1070", text)
        self.assertIn("not v2.0 release performance evidence", text)
        self.assertIn("database_analytics", text)
        self.assertIn("graph_analytics", text)
        self.assertIn("polygon_pair_overlap_area_rows", text)
        self.assertIn("polygon_set_jaccard", text)
        self.assertIn("candidate-backend optix", text)


if __name__ == "__main__":
    unittest.main()
