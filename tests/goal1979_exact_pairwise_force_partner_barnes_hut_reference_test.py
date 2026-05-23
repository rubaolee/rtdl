from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
APP_ADAPTER = ROOT / "src" / "rtdsl" / "app_adapters" / "barnes_hut.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
EXAMPLE = ROOT / "examples" / "v2_0" / "apps" / "simulation" / "rtdl_barnes_hut_force_app.py"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
REPORT = ROOT / "docs" / "reports" / "goal1979_exact_pairwise_force_partner_barnes_hut_reference_2026-05-14.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal1979_pod_exact_pairwise_force_barnes_hut_cupy_perf.json"


class Goal1979ExactPairwiseForcePartnerBarnesHutReferenceTest(unittest.TestCase):
    def test_partner_adapter_exposes_generic_weighted_point_force_vectors(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        app_adapter = APP_ADAPTER.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def weighted_point_rows_to_partner_columns", adapters)
        self.assertIn("from .partner_adapters import weighted_point_rows_to_partner_columns", init_text)
        self.assertIn("def pairwise_inverse_square_force_2d_partner_columns", app_adapter)
        self.assertIn("from .app_adapters import pairwise_inverse_square_force_2d_partner_columns", init_text)
        self.assertIn('"pairwise_inverse_square_force_2d_partner_columns"', init_text)
        self.assertNotIn("def pairwise_inverse_square_force_2d_partner_columns", adapters)
        self.assertIn("generic_pairwise_inverse_square_force_2d", app_adapter)
        self.assertIn("caller_supplied_partner_device_weighted_point_columns", app_adapter)
        self.assertIn("exclude_equal_ids", app_adapter)
        self.assertIn("torch.rsqrt", app_adapter)
        self.assertIn("cupy.RawKernel", app_adapter)
        self.assertIn("pairwise_force_2d", app_adapter)
        self.assertIn("rt_core_speedup_claim_authorized", app_adapter)

    def test_barnes_app_exposes_partner_exact_force_without_rt_core_claim(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn('"partner_exact_force"', text)
        self.assertIn("rt.weighted_point_rows_to_partner_columns", text)
        self.assertIn("rt.pairwise_inverse_square_force_2d_partner_columns", text)
        self.assertIn("generic weighted-point pairwise inverse-square force", text)
        self.assertIn("not an RT-core claim", text)
        self.assertIn("--skip-validation", text)

    def test_cpu_reference_path_still_runs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(EXAMPLE),
                "--backend",
                "cpu_python_reference",
                "--output-mode",
                "force_summary",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["app"], "barnes_hut_force_app")
        self.assertEqual(payload["backend"], "cpu_python_reference")
        self.assertEqual(payload["force_row_count"], payload["body_count"])
        self.assertFalse(payload["rt_core_accelerated"])

    def test_report_and_preflight_record_goal1979(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        self.assertIn("force vectors", report)
        self.assertIn("generic weighted point columns", report)
        self.assertIn("not a Barnes-Hut tree-opening accelerator", report)
        self.assertIn("RT-core force-vector speedup claim: no", report)
        self.assertIn("0.01986x", report)
        self.assertIn("goal1979_pod_exact_pairwise_force_barnes_hut_cupy_perf.json", report)
        self.assertIn("tests.goal1979_exact_pairwise_force_partner_barnes_hut_reference_test", preflight)

    def test_pod_artifact_records_exact_force_kernel_boundary(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["claim_boundary"]["exact_partner_reference_path"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertTrue(payload["validation_row"]["matches_oracle"])
        self.assertLess(payload["validation_row"]["max_relative_error"], 1.0e-12)
        rows = {row["body_count"]: row for row in payload["results"]}
        self.assertEqual(rows[512]["partner_reference_contract"], "generic_pairwise_inverse_square_force_2d")
        self.assertLess(rows[512]["v2_vs_cpu_python_reference_ratio"], 0.03)
        self.assertTrue(rows[8192]["validation_skipped"])
        self.assertEqual(rows[8192]["force_row_count"], 8192)


if __name__ == "__main__":
    unittest.main()
