from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
EXAMPLE = ROOT / "examples" / "rtdl_facility_knn_assignment.py"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
REPORT = ROOT / "docs" / "reports" / "goal1978_exact_top_k_partner_facility_assignment_2026-05-14.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal1978_pod_exact_top_k_facility_cupy_perf.json"


class Goal1978ExactTopKPartnerFacilityAssignmentTest(unittest.TestCase):
    def test_partner_adapter_exposes_generic_exact_top_k_nearest_points(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def top_k_nearest_points_2d_partner_columns", adapters)
        self.assertIn("generic_exact_top_k_nearest_points_2d", adapters)
        self.assertIn("distance_then_candidate_id", adapters)
        self.assertIn("torch.argsort", adapters)
        self.assertIn("stable=True", adapters)
        self.assertIn("cupy.argsort", adapters)
        self.assertIn("kind=\"stable\"", adapters)
        self.assertIn("native_engine_row_contract", adapters)
        self.assertIn("not_called_partner_reference_only", adapters)
        self.assertIn("rt_core_speedup_claim_authorized", adapters)
        self.assertIn("from .partner_adapters import top_k_nearest_points_2d_partner_columns", init_text)
        self.assertIn('"top_k_nearest_points_2d_partner_columns"', init_text)

    def test_facility_app_exposes_partner_exact_without_rt_core_claim(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn('"partner_exact"', text)
        self.assertIn("rt.point_rows_to_partner_columns", text)
        self.assertIn("rt.top_k_nearest_points_2d_partner_columns", text)
        self.assertIn("generic partner point-column algebra", text)
        self.assertIn("rt_core_accelerated\": False", text)
        self.assertIn("--partner", text)

    def test_cpu_reference_path_still_runs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(EXAMPLE),
                "--backend",
                "cpu_python_reference",
                "--copies",
                "1",
                "--output-mode",
                "rows",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["app"], "facility_knn_assignment")
        self.assertEqual(payload["backend"], "cpu_python_reference")
        self.assertEqual(payload["k"], 3)
        self.assertEqual(payload["row_count"], 12)
        self.assertFalse(payload["rt_core_accelerated"])

    def test_report_and_preflight_record_goal1978(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        self.assertIn("ranked nearest depots", report)
        self.assertIn("fixed-radius threshold", report)
        self.assertIn("exact top-k partner row", report)
        self.assertIn("not native engine customization", report)
        self.assertIn("0.04565x", report)
        self.assertIn("goal1978_pod_exact_top_k_facility_cupy_perf.json", report)
        self.assertIn("tests.goal1978_exact_top_k_partner_facility_assignment_test", preflight)

    def test_pod_artifact_records_exact_cupy_top_k_boundary(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["claim_boundary"]["exact_partner_reference_path"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])
        rows = {row["copies"]: row for row in payload["results"]}
        self.assertEqual(rows[128]["partner_reference_contract"], "generic_exact_top_k_nearest_points_2d")
        self.assertTrue(rows[128]["matches_cpu_row_count"])
        self.assertLess(rows[128]["v2_vs_cpu_python_reference_ratio"], 0.05)
        self.assertTrue(rows[1024]["matches_shape"])
        self.assertEqual(rows[1024]["row_count"], 12288)


if __name__ == "__main__":
    unittest.main()
