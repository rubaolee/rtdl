from __future__ import annotations

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


class Goal3306PreparedPointProbeColumnsScalarCountTest(unittest.TestCase):
    def test_native_exports_generic_prepared_point_probe_columns(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")

        for phrase in (
            "struct PreparedPointProbeColumns2D",
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

    def test_python_runtime_exposes_context_managed_prepared_points(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        init_text = (ROOT / "src" / "rtdsl" / "__init__.py").read_text(encoding="utf-8")

        for phrase in (
            "class PreparedOptixPointProbeColumns2D",
            "prepare_point_probe_columns_2d_optix",
            "count_device_filtered_prepared_points",
            "rtdl.optix.prepared_point_probe_columns_2d.v1",
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


if __name__ == "__main__":
    unittest.main()
