from __future__ import annotations

from pathlib import Path
import json
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3431_spatial_rayjoin_prepared_cupy_refined_pip_pod_2026-06-05.json"


class Goal3431SpatialRayJoinPreparedCupyRefinedPipRouteTest(unittest.TestCase):
    def test_app_exposes_explicit_prepared_cupy_refined_pip_route(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn("def run_rayjoin_prepared_optix_cupy_refined_pip", app)
        self.assertIn('"prepared_optix_cupy_refined_pip"', app)
        self.assertIn("--candidate-max-rows", app)
        self.assertIn("prepare_closed_shape_membership_candidate_refiner_exact_cupy", app)
        self.assertIn("candidate_device_columns(points, max_rows=max_rows)", app)
        self.assertIn("prepared_refiner.refine(columns)", app)
        self.assertIn("candidate_columns_and_prepared_cupy_refiner_complete", app)
        self.assertIn('"rt_core_speedup_claim_authorized": False', app)
        self.assertIn("prepared_optix_cupy_refined_pip currently supports only --workload pip", app)

    def test_readme_documents_route_without_claim_expansion(self) -> None:
        readme = README.read_text(encoding="utf-8")

        self.assertIn("prepared_optix_cupy_refined_pip", readme)
        self.assertIn("instance identity ordinals", readme)
        self.assertIn("prepared CuPy simple-ring", readme)
        self.assertIn("--candidate-max-rows", readme)
        self.assertIn("full RayJoin paper reproduction", readme)

    def test_v2_8_gap_matrix_records_goal3427_spatial_rayjoin_update(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("prepared CuPy exact refiner", spatial["current_best_path"])
        self.assertIn("CuPy is the measured prepared closed-shape refinement partner", spatial["partner_position"])
        self.assertIn("instance-aware candidate columns", spatial["current_bottleneck"])
        self.assertIn("device-resident relation-row output beyond PIP", spatial["current_bottleneck"])
        for goal in ("Goal3424", "Goal3427", "Goal3428"):
            self.assertIn(goal, spatial["evidence_refs"])
        self.assertFalse(spatial["release_authorized"])
        self.assertFalse(spatial["public_speedup_claim_authorized"])
        self.assertFalse(spatial["rt_core_speedup_claim_authorized"])
        self.assertFalse(spatial["true_zero_copy_claim_authorized"])

    def test_report_records_route_and_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3431",
            "prepared_optix_cupy_refined_pip",
            "generic point/closed-shape candidate columns",
            "prepared CuPy exact refiner",
            "Goal3427",
            "Goal3428",
            "`release_authorized: False`",
            "`rt_core_speedup_claim_authorized: False`",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3431 pod artifact pending")
    def test_pod_artifact_records_route_execution(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["execution_route"], "prepared_optix_cupy_refined_pip")
        self.assertEqual(payload["workload"], "pip")
        self.assertEqual(payload["backend"], "optix+cupy")
        self.assertEqual(payload["result_mode"], "count")
        self.assertEqual(payload["summary"]["positive_hit_row_count"], payload["row_count"])
        self.assertTrue(payload["candidate_columns"]["has_instance_identity_columns"])
        self.assertTrue(payload["partner_refinement"]["instance_identity_columns_used"])
        self.assertEqual(payload["partner_refinement"]["row_count"], payload["row_count"])
        for value in payload["claim_boundary"].values():
            self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
