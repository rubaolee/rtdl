from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3274_closed_shape_scalar_count_pipeline_probe_2026-06-03.md"


class Goal3274ClosedShapeScalarCountPipelineProbeTest(unittest.TestCase):
    def test_scalar_count_pipeline_is_gated_and_generic(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("static PipPipeline         g_pip_scalar_count;", core)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_USE_SCALAR_COUNT_PIPELINE", workloads)
        self.assertIn("point_closed_shape_scalar_count_kernel.cu", workloads)
        self.assertIn("closed-shape scalar-count intersection block not found", workloads)
        self.assertIn("__intersection__pip_isect", workloads)
        self.assertIn("point_in_polygon(px, py, poly)", workloads)
        self.assertNotIn("rayjoin", workloads[workloads.index("static void ensure_pip_scalar_count_pipeline"):workloads.index("static void run_pip_optix")].lower())

    def test_scalar_count_pipeline_omits_anyhit_program(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        body = workloads[
            workloads.index("static void ensure_pip_scalar_count_pipeline"):
            workloads.index("static void run_pip_optix")
        ]

        self.assertIn("nullptr,\n            nullptr, 4).release();", body)
        self.assertIn("optixSetPayload_2(optixGetPayload_2() + 1u);", body)
        self.assertNotIn("__anyhit__pip_anyhit\",\n            nullptr", body)

    def test_prepared_device_filtered_count_selects_gated_pipeline(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        body = workloads[
            workloads.index("static void count_prepared_point_closed_shape_membership_device_filtered_2d_optix"):
            workloads.index("static void run_prepared_point_closed_shape_membership_candidate_device_columns_2d_optix")
        ]

        self.assertIn("const bool use_scalar_count_pipeline", body)
        self.assertIn("ensure_pip_scalar_count_pipeline();", body)
        self.assertIn("? g_pip_scalar_count.pipe", body)
        self.assertIn(": g_pip.pipe", body)

    def test_report_records_probe_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "gated scalar-count pipeline probe",
            "not a default behavior change",
            "not a RayJoin-specific native primitive",
            "pod verdict pending",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()

