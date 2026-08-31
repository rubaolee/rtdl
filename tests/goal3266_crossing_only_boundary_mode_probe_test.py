from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
RUNNER = ROOT / "scripts" / "goal3244_rayjoin_same_slice_repeated_count_runner.py"

SPEC = importlib.util.spec_from_file_location("goal3244_runner_for_goal3266", RUNNER)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Goal3266CrossingOnlyBoundaryModeProbeTest(unittest.TestCase):
    def test_native_boundary_check_is_launch_param_and_defaults_inclusive(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("uint32_t boundary_check;", core)
        self.assertIn("if (params.boundary_check != 0u)", core)
        self.assertIn("uint32_t         boundary_check;", workloads)
        self.assertIn("closed_shape_membership_boundary_check_enabled", workloads)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_BOUNDARY_MODE", workloads)
        self.assertIn("crossing_only", workloads)
        self.assertGreaterEqual(
            workloads.count("lp.boundary_check = closed_shape_membership_boundary_check_enabled();"),
            4,
        )

    def test_app_validates_inclusive_exact_before_experimental_filtered_lane(self) -> None:
        text = APP.read_text(encoding="utf-8")

        self.assertIn("_PIP_DEVICE_FILTER_BOUNDARY_MODES = (\"inclusive\", \"crossing_only\")", text)
        self.assertIn("_run_prepared_count_with_boundary_mode(prepared, packed_points, None)", text)
        self.assertIn("_run_prepared_device_filtered_count_with_boundary_mode(", text)
        self.assertIn("device_filtered_boundary_mode", text)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_BOUNDARY_MODE", text)

    def test_runner_records_boundary_mode_and_passes_it_to_app(self) -> None:
        calls: list[dict[str, object]] = []

        def fake_run(*args, **kwargs):
            calls.append({"args": args, "kwargs": dict(kwargs)})
            return {
                "phases_sec": {
                    "prepared_query_sec": 0.0004,
                    "validation_exact_query_sec": 0.0008,
                    "query_pack_sec": 0.0001,
                    "prepare_static_scene_sec": 0.0002,
                },
                "summary": {
                    "positive_assignment_count": 1430,
                    "device_filtered_count_matches_exact": True,
                },
                "row_count": 1430,
                "native_phase_timings": {"mode": "device_filtered_count"},
            }

        with mock.patch.object(MODULE.rayjoin_app, "run_rayjoin_prepared_optix_workload", side_effect=fake_run):
            row = MODULE.run_rtdl_samples(
                workload="pip",
                dataset="fake.cdb",
                warmup=1,
                repeat=2,
                count_mode="device_filtered_validated",
                query_axis="z_point",
                boundary_mode="crossing_only",
            )

        self.assertEqual(row["device_filtered_boundary_mode"], "crossing_only")
        self.assertEqual(row["prepared_query_ms"]["samples"], [0.4, 0.4])
        self.assertTrue(
            all(call["kwargs"]["device_filtered_boundary_mode"] == "crossing_only" for call in calls)
        )

    def test_runner_cli_surface_documents_validation_boundary(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("--rtdl-pip-boundary-mode", text)
        self.assertIn("device_filtered_boundary_mode", text)
        self.assertIn("exact validation count with inclusive boundary checks", text)


if __name__ == "__main__":
    unittest.main()
