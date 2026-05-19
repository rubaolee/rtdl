from __future__ import annotations

import pathlib
import unittest
import json

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    plan_rt_dbscan_execution,
    run_rt_dbscan_benchmark,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal2422_rt_dbscan_explicit_plan_mode_2026-05-19.md"
POD_SMOKE = ROOT / "docs" / "reports" / "goal2422_rt_dbscan_explicit_plan_mode_pod_smoke"


class Goal2422RtDbscanExplicitPlanModeTest(unittest.TestCase):
    def test_plan_policy_matches_goal2418_2420_boundaries(self) -> None:
        self.assertEqual(plan_rt_dbscan_execution("tiny", 9)["selected_mode"], "cpu_reference")
        self.assertEqual(
            plan_rt_dbscan_execution("ngsim_dense", 131072)["selected_mode"],
            "partner_cupy_prepared_grid_components_3d",
        )
        self.assertEqual(
            plan_rt_dbscan_execution("road3d", 131072)["selected_mode"],
            "partner_cupy_prepared_grid_components_3d",
        )
        self.assertEqual(
            plan_rt_dbscan_execution("road3d", 262144)["selected_mode"],
            "partner_cupy_prepared_grid_components_3d",
        )
        self.assertEqual(
            plan_rt_dbscan_execution("road3d", 524288)["selected_mode"],
            "optix_rt_core_flags_cupy_prepared_grid_components_3d",
        )
        self.assertEqual(
            plan_rt_dbscan_execution("clustered3d", 32768)["selected_mode"],
            "partner_cupy_prepared_grid_components_3d",
        )
        self.assertEqual(
            plan_rt_dbscan_execution("clustered3d", 65536)["selected_mode"],
            "optix_rt_core_flags_cupy_prepared_grid_components_3d",
        )

    def test_tiny_planned_mode_executes_without_gpu_and_records_plan(self) -> None:
        payload = run_rt_dbscan_benchmark(
            mode="planned_rt_dbscan",
            dataset="tiny",
            point_count=None,
            radius=None,
            min_neighbors=None,
            seed=20260519,
            partner="cupy",
            include_rows=False,
            validate=True,
        )

        self.assertEqual(payload["mode"], "planned_rt_dbscan")
        self.assertEqual(payload["selected_mode"], "cpu_reference")
        self.assertTrue(payload["matches_reference"])
        plan = payload["metadata"]["execution_plan"]
        self.assertTrue(plan["not_hidden_dispatcher"])
        self.assertFalse(payload["claim_boundary"]["automatic_hidden_dispatcher"])
        self.assertFalse(payload["claim_boundary"]["release_claim_authorized"])

    def test_docs_and_app_keep_dispatch_boundary_explicit(self) -> None:
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("planned_rt_dbscan", app)
        self.assertIn("not_hidden_dispatcher", app)
        self.assertIn("explicit benchmark-app plan", readme)
        self.assertIn("not a hidden runtime dispatcher", readme)
        self.assertIn("plan -> explain -> execute -> preserve claim boundary", report)
        self.assertIn("does not add native DBSCAN ABI", report)

    def test_pod_smoke_artifacts_record_historical_plan_boundary(self) -> None:
        expected = {
            "goal2422_clustered3d_32768.json",
            "goal2422_road3d_131072.json",
            "goal2422_road3d_262144.json",
            "goal2422_ngsim_dense_65536.json",
        }
        for name in expected:
            with self.subTest(name=name):
                payload = json.loads((POD_SMOKE / name).read_text(encoding="utf-8"))
                self.assertEqual(payload["mode"], "planned_rt_dbscan")
                self.assertTrue(payload["metadata"]["execution_plan"]["not_hidden_dispatcher"])
                self.assertFalse(payload["claim_boundary"]["automatic_hidden_dispatcher"])


if __name__ == "__main__":
    unittest.main()
