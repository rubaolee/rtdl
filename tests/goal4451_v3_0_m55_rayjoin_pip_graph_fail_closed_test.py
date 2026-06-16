from __future__ import annotations

from pathlib import Path
import inspect
import json
import os
import unittest

import rtdsl as rt
from rtdsl import optix_runtime as opt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4451_v3_0_m55_rayjoin_pip_graph_fail_closed_2026-06-16.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4451_v3_0_m55_rayjoin_pip_graph_fail_closed_2026-06-16.json"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
OPTIX_NATIVE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


def _has_live_optix_backend() -> bool:
    try:
        opt.optix_version()
    except Exception:
        return False
    return True


class Goal4451V30M55RayJoinPipGraphFailClosedTest(unittest.TestCase):
    def test_runtime_quarantines_graph_not_batch_executor(self) -> None:
        runtime_text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        native_text = OPTIX_NATIVE.read_text(encoding="utf-8")
        executor_signature = inspect.signature(
            opt.PreparedOptixPointClosedShapeBatchCountExecutor2D.__init__
        )
        graph_signature = inspect.signature(
            opt.PreparedOptixPointClosedShapeBatchCountGraph2D.__init__
        )

        self.assertIn("RTDL_OPTIX_ALLOW_UNVALIDATED_PREPARED_POINTS_BATCH_GRAPH", runtime_text)
        self.assertIn("prepared OptiX point/closed-shape batch CUDA graph replay is quarantined", runtime_text)
        self.assertNotIn("validate_on_prepare", executor_signature.parameters)
        self.assertIn("validate_on_prepare", graph_signature.parameters)
        self.assertIn("CU_STREAM_CAPTURE_MODE_GLOBAL", native_text)
        self.assertNotIn("CU_STREAM_CAPTURE_MODE_RELAXED", native_text)

    @unittest.skipUnless(_has_live_optix_backend(), "OptiX backend is not available in this environment")
    def test_live_optix_graph_fails_closed_without_breaking_executor(self) -> None:
        polygons = opt.pack_polygons(
            ids=[10],
            vertex_offsets=[0],
            vertex_counts=[4],
            vertices_xy=[0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0],
        )
        points = opt.pack_points(
            ids=[0, 1, 2],
            x=[0.5, 2.0, 0.25],
            y=[0.5, 2.0, 0.25],
            dimension=2,
        )

        prepared = opt.prepare_point_closed_shape_membership_2d_optix(polygons)
        prepared_points = prepared.prepare_point_probe_columns(points)

        try:
            self.assertEqual(prepared.count_device_filtered_prepared_points(prepared_points), 2)
            self.assertEqual(
                prepared.count_device_filtered_prepared_points_batch(prepared_points, 3),
                (2, 2, 2),
            )
            with prepared.prepare_device_filtered_prepared_points_batch_executor(
                prepared_points,
                3,
            ) as executor:
                self.assertEqual(executor.run(), (2, 2, 2))

            old_override = os.environ.pop(
                opt.OPTIX_PREPARED_POINTS_BATCH_GRAPH_UNVALIDATED_OVERRIDE_ENV,
                None,
            )
            try:
                with self.assertRaisesRegex(RuntimeError, "quarantined"):
                    prepared.prepare_device_filtered_prepared_points_batch_graph(
                        prepared_points,
                        3,
                        validate_on_prepare=False,
                    )
            finally:
                if old_override is not None:
                    os.environ[opt.OPTIX_PREPARED_POINTS_BATCH_GRAPH_UNVALIDATED_OVERRIDE_ENV] = old_override

            with self.assertRaises(RuntimeError) as failure:
                prepared.prepare_device_filtered_prepared_points_batch_graph(
                    prepared_points,
                    3,
                    validate_on_prepare=True,
                )
            message = str(failure.exception)
            self.assertIn("quarantined", message)
            self.assertIn("prepare_device_filtered_prepared_points_batch_executor", message)
        finally:
            prepared_points.close()
            prepared.close()

    def test_route_and_adequacy_guidance_record_goal4451(self) -> None:
        route = rt.explain_current_benchmark_route("spatial_rayjoin")
        spatial = {row["app"]: row for row in rt.current_benchmark_adequacy()}["spatial_rayjoin"]

        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4465.v1", rt.CURRENT_BENCHMARK_ROUTE_DECISION_VERSION)
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4465.v1", rt.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertIn("Goal4451", route["evidence_refs"])
        self.assertIn("Goal4451", spatial["evidence_refs"])
        self.assertIn("fail-closed", route["next_runtime_action"])
        self.assertIn("batch executor", route["next_runtime_action"])
        self.assertIn("fail-closes unsafe graph replay", spatial["next_generic_runtime_action"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(spatial["public_speedup_claim_authorized"])

    def test_evidence_artifact_and_report_document_non_claim_boundary(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")

        self.assertEqual(artifact["goal"], 4451)
        self.assertEqual(artifact["single_count"], 2)
        self.assertEqual(artifact["batch_counts"], [2, 2, 2])
        self.assertEqual(artifact["executor_counts"], [2, 2, 2])
        self.assertEqual(artifact["unvalidated_graph_status"], "failed_closed_before_native_prepare")
        self.assertIn("quarantined", artifact["unvalidated_graph_error"])
        self.assertIn(artifact["validated_graph_status"], {"failed_closed_native_prepare", "failed_closed_validation"})
        self.assertIn("quarantined", artifact["validated_graph_error"])
        self.assertFalse(any(artifact["claim_boundary"].values()))

        for phrase in (
            "batch executor remains the recommended repeated-PIP path",
            "unvalidated graph replay now fails closed before native prepare",
            "does not authorize a performance claim",
            "RELAXED capture did not fix the failure",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
