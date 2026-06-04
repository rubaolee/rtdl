from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3256ClosedShapeZPointProbeModeTest(unittest.TestCase):
    def test_default_probe_axis_remains_vertical(self) -> None:
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("const uint32_t query_axis_z_point = 0u;", core)
        self.assertIn("Bounded vertical probe through the point", core)
        self.assertIn("make_float3(px, py - query_half_extent, 0.0f)", core)
        self.assertIn("make_float3(0.0f, 1.0f, 0.0f)", core)

    def test_opt_in_z_point_probe_traverses_point_containing_aabbs(self) -> None:
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("Point-axis probe", core)
        self.assertIn("make_float3(px, py, -1.0f)", core)
        self.assertIn("make_float3(0.0f, 0.0f, 1.0f)", core)
        self.assertIn("let the generic closed-shape predicate decide", core)

    def test_pipeline_specializes_axis_from_generic_environment_variable(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        start = workloads.index("static void ensure_pip_pipeline()")
        end = workloads.index("static void run_pip_optix(", start)
        body = workloads[start:end]

        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS", body)
        self.assertIn('axis == "z_point"', body)
        self.assertIn('axis == "vertical"', body)
        self.assertIn("failed to specialize closed-shape membership query axis", body)
        self.assertIn("const uint32_t query_axis_z_point = 1u;", body)
        self.assertIn("const uint32_t query_axis_z_point = 0u;", body)

    def test_axis_mode_is_app_agnostic(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        start = workloads.index("static void ensure_pip_pipeline()")
        end = workloads.index("static void run_pip_optix(", start)
        body = workloads[start:end].lower()

        for forbidden in ("rayjoin", "county", "soil", "brazil", "app-specific"):
            self.assertNotIn(forbidden, body)


if __name__ == "__main__":
    unittest.main()
