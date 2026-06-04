from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3274_closed_shape_scalar_count_pipeline_probe_2026-06-03.md"
DEFAULT_ARTIFACT = ROOT / "docs" / "reports" / "goal3274_pod" / "goal3274_default_control_same_slice.json"
SCALAR_ARTIFACT = ROOT / "docs" / "reports" / "goal3274_pod" / "goal3274_scalar_count_pipeline_same_slice.json"


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
            "not promoted to default",
            "not a clear performance win",
        ):
            self.assertIn(phrase, report)

    def test_pod_artifacts_record_neutral_negative_probe(self) -> None:
        self.assertTrue(DEFAULT_ARTIFACT.exists())
        self.assertTrue(SCALAR_ARTIFACT.exists())

        default = json.loads(DEFAULT_ARTIFACT.read_text(encoding="utf-8"))
        scalar = json.loads(SCALAR_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(default["rtdl_commit"], scalar["rtdl_commit"])
        self.assertEqual(default["source_dirty"], [])
        self.assertEqual(scalar["source_dirty"], [])
        self.assertEqual(default["rtdl"]["pip"]["counts"]["last"], 1430)
        self.assertEqual(scalar["rtdl"]["pip"]["counts"]["last"], 1430)
        self.assertLess(
            scalar["rtdl"]["pip"]["prepared_query_ms"]["median"],
            default["rtdl"]["pip"]["prepared_query_ms"]["median"],
        )
        default_phase = default["rtdl"]["pip"]["native_phase_samples"]
        scalar_phase = scalar["rtdl"]["pip"]["native_phase_samples"]
        default_count_pass = sorted(row["candidate_count_pass"] for row in default_phase)[len(default_phase) // 2]
        scalar_count_pass = sorted(row["candidate_count_pass"] for row in scalar_phase)[len(scalar_phase) // 2]
        self.assertGreater(scalar_count_pass, default_count_pass)
        for artifact in (default, scalar):
            boundary = artifact["claim_boundary"]
            self.assertFalse(boundary["release_authorized"])
            self.assertFalse(boundary["public_speedup_claim_authorized"])
            self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
