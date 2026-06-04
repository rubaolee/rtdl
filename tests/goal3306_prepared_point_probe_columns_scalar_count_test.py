from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
RUNNER = ROOT / "scripts" / "goal3244_rayjoin_same_slice_repeated_count_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal3306_prepared_point_probe_columns_scalar_count_2026-06-04.md"
PREPARED_ARTIFACT = ROOT / "docs" / "reports" / "goal3306_prepared_points_rayjoin_same_slice_pod_2026-06-04.json"
BASELINE_ARTIFACT = ROOT / "docs" / "reports" / "goal3306_baseline_device_filtered_same_slice_pod_2026-06-04.json"


class Goal3306PreparedPointProbeColumnsScalarCountTest(unittest.TestCase):
    def test_native_exports_generic_prepared_point_probe_columns(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")

        for phrase in (
            "struct PreparedPointProbeColumns2D",
            "DevPtr d_count",
            "DevPtr d_params",
            "prepare_point_probe_columns_2d_optix",
            "count_prepared_point_closed_shape_membership_device_filtered_prepared_points_2d_optix",
        ):
            self.assertIn(phrase, workloads)

        for symbol in (
            "rtdl_optix_prepare_point_probe_columns_2d",
            "rtdl_optix_count_prepared_point_closed_shape_membership_device_filtered_prepared_points_2d",
            "rtdl_optix_destroy_prepared_point_probe_columns_2d",
        ):
            self.assertIn(symbol, api)
            self.assertIn(symbol, prelude)

        start = workloads.index("struct PreparedPointProbeColumns2D")
        end = workloads.index("static void run_prepared_point_closed_shape_first_boundary_crossing_2d_optix", start)
        self.assertNotIn("rayjoin", workloads[start:end].lower())

        count_start = workloads.index(
            "static void count_prepared_point_closed_shape_membership_device_filtered_prepared_points_2d_optix"
        )
        count_end = workloads.index(
            "static void run_prepared_point_closed_shape_membership_candidate_device_columns_2d_optix",
            count_start,
        )
        prepared_count_body = workloads[count_start:count_end]
        self.assertIn("prepared_points->d_count.ptr", prepared_count_body)
        self.assertIn("prepared_points->d_params.ptr", prepared_count_body)
        self.assertNotIn("DevPtr d_count(sizeof(uint32_t));", prepared_count_body)
        self.assertNotIn("DevPtr d_params(sizeof(PipLaunchParams));", prepared_count_body)

    def test_python_runtime_exposes_context_managed_prepared_points(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        init_text = (ROOT / "src" / "rtdsl" / "__init__.py").read_text(encoding="utf-8")

        for phrase in (
            "class PreparedOptixPointProbeColumns2D",
            "prepare_point_probe_columns_2d_optix",
            "count_device_filtered_prepared_points",
            "rtdl.optix.prepared_point_probe_columns_2d.v1",
            "prepared_points_device_filtered_count",
            "true_zero_copy_claim_authorized",
        ):
            self.assertIn(phrase, runtime)

        self.assertIn("PreparedOptixPointProbeColumns2D", init_text)
        self.assertIn("prepare_point_probe_columns_2d_optix", init_text)

    def test_rayjoin_runner_can_select_validated_prepared_points_mode(self) -> None:
        app = APP.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        for text in (app, runner):
            self.assertIn("device_filtered_prepared_points_validated", text)

        self.assertIn("prepare_query_points_sec", app)
        self.assertIn("prepared_point_probe_columns", app)
        self.assertIn("prepare_query_points_ms", runner)
        self.assertIn("validated device-side count was not validated against exact count", runner)

    def test_report_and_artifacts_record_modest_repeated_query_win(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        prepared = json.loads(PREPARED_ARTIFACT.read_text(encoding="utf-8"))
        baseline = json.loads(BASELINE_ARTIFACT.read_text(encoding="utf-8"))

        for phrase in (
            "modest repeated-query win",
            "not a one-shot improvement",
            "RTDL-beats-RayJoin claims",
            "persistent launch parameter/count buffers",
        ):
            self.assertIn(phrase, text)

        self.assertEqual(prepared["rtdl_commit"], "7890701c9d70dffc4a281d0a4ff5f207606859d2")
        self.assertEqual(baseline["rtdl_commit"], prepared["rtdl_commit"])
        self.assertFalse(any(prepared["claim_boundary"].values()))
        self.assertFalse(any(baseline["claim_boundary"].values()))

        prepared_pip = prepared["rtdl"]["pip"]
        baseline_pip = baseline["rtdl"]["pip"]
        self.assertEqual(prepared_pip["count_mode"], "device_filtered_prepared_points_validated")
        self.assertEqual(baseline_pip["count_mode"], "device_filtered_validated")
        self.assertEqual(prepared_pip["counts"]["last"], 1430)
        self.assertEqual(baseline_pip["counts"]["last"], 1430)

        self.assertLess(
            prepared_pip["prepared_query_ms"]["median"],
            baseline_pip["prepared_query_ms"]["median"],
        )
        self.assertGreater(prepared_pip["prepare_query_points_ms"]["median"], 0.0)
        self.assertEqual(prepared_pip["native_phase_samples"][0]["mode"], "prepared_points_device_filtered_count")
        self.assertEqual(prepared_pip["native_phase_samples"][0]["point_upload"], 0.0)
        self.assertEqual(baseline_pip["native_phase_samples"][0]["mode"], "device_filtered_count")
        self.assertGreater(baseline_pip["native_phase_samples"][0]["point_upload"], 0.0)


if __name__ == "__main__":
    unittest.main()
