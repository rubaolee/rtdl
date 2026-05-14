from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "rtdl_ann_candidate_app.py"
REPORT = ROOT / "docs" / "reports" / "goal1983_exact_ann_candidate_quality_partner_reference_2026-05-14.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal1983_pod_exact_ann_candidate_quality_cupy_perf.json"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
ANALYSIS_SCRIPT = ROOT / "scripts" / "goal1931_current_all_app_v18_v2_perf_analysis.py"


class Goal1983ExactAnnCandidateQualityPartnerReferenceTest(unittest.TestCase):
    def test_ann_app_exposes_partner_exact_quality_without_engine_customization(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn('"partner_exact_quality"', text)
        self.assertIn("rt.point_rows_to_partner_columns", text)
        self.assertIn("rt.top_k_nearest_points_2d_partner_columns", text)
        self.assertIn("top_k_nearest_points_2d_partner_columns", text)
        self.assertIn("ANN index", text)
        self.assertIn("native_engine_customization", text)
        self.assertIn("rt_core_speedup_claim_authorized", text)
        self.assertIn("--partner", text)

    def test_existing_cpu_quality_path_still_runs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(EXAMPLE),
                "--backend",
                "cpu_python_reference",
                "--copies",
                "1",
                "--output-mode",
                "quality_summary",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["app"], "ann_candidate_search")
        self.assertEqual(payload["backend"], "cpu_python_reference")
        self.assertEqual(payload["recall_at_1"], 2 / 3)
        self.assertEqual(payload["exact_match_count"], 2)
        self.assertFalse(payload["rt_core_accelerated"])

    def test_report_preflight_and_analysis_record_goal1983(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")
        analysis_script = ANALYSIS_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("fixed-radius candidate", report)
        self.assertIn("exact full-search reference", report)
        self.assertIn("not an ANN index", report)
        self.assertIn("0.01881x", report)
        self.assertIn("goal1983_pod_exact_ann_candidate_quality_cupy_perf.json", report)
        self.assertIn("tests.goal1983_exact_ann_candidate_quality_partner_reference_test", preflight)
        self.assertIn("_goal1983_exact_ann_quality_rows", analysis_script)

    def test_pod_artifact_records_exact_quality_boundary(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["claim_boundary"]["exact_partner_reference_path"])
        self.assertFalse(payload["claim_boundary"]["native_engine_customization"])
        self.assertFalse(payload["claim_boundary"]["ann_index_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])
        rows = {row["copies"]: row for row in payload["results"]}
        self.assertEqual(rows[128]["partner_reference_contract"], "generic_exact_top_k_nearest_points_2d")
        self.assertTrue(rows[128]["matches_cpu_quality"])
        self.assertLess(rows[128]["v2_vs_cpu_python_reference_ratio"], 0.04)
        self.assertTrue(rows[512]["matches_cpu_quality"])
        self.assertLess(rows[512]["v2_vs_cpu_python_reference_ratio"], 0.02)
        self.assertEqual(rows[2048]["query_count"], 6144)
        self.assertEqual(rows[2048]["search_count"], 12288)


if __name__ == "__main__":
    unittest.main()
