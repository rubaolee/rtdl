from __future__ import annotations

import json
import os
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal3297_optix_closed_shape_boundary_event_rows_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3297_optix_closed_shape_boundary_event_rows_pod_2026-06-04.json"


class Goal3297ClosedShapeBoundaryEventOptixRowsTest(unittest.TestCase):
    def test_native_abi_adds_generic_boundary_event_rows(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")

        symbol = "rtdl_optix_run_prepared_point_closed_shape_first_boundary_crossing_2d"
        for text in (prelude, api):
            self.assertIn("RtdlPointClosedShapeBoundaryEventRow", text)
            self.assertIn(symbol, text)
            self.assertNotIn("rayjoin", text.lower())

    def test_optix_kernel_scans_prepared_edges_and_reports_boundary_events(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("kPointClosedShapeBoundaryEventKernelSrc", core)
        self.assertIn("__raygen__point_closed_shape_boundary_event_probe", core)
        self.assertIn("__intersection__point_closed_shape_boundary_event_isect", core)
        self.assertIn("__anyhit__point_closed_shape_boundary_event_anyhit", core)
        self.assertIn("first_boundary_crossing", core)
        self.assertIn("params.prepared_edges[off + i]", core)
        self.assertIn("ensure_point_closed_shape_boundary_event_pipeline", workloads)
        self.assertIn("run_prepared_point_closed_shape_first_boundary_crossing_2d_optix", workloads)
        self.assertIn("reset_closed_shape_membership_phase_timings(6u)", workloads)
        self.assertNotIn("closest_eid", core.lower())
        self.assertNotIn("rayjoin", core.lower())

    def test_python_binding_exposes_prepared_boundary_event_method(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("OPTIX_CLOSED_SHAPE_FIRST_BOUNDARY_CROSSING_SYMBOL", runtime)
        self.assertIn("def first_boundary_crossing_raw", runtime)
        self.assertIn("def first_boundary_crossing(", runtime)
        self.assertIn("_RtdlPointClosedShapeBoundaryEventRow", runtime)
        self.assertIn('"boundary_event_rows"', runtime)
        self.assertIn('"point_id",\n                    "shape_id",\n                    "boundary_id"', runtime)

    def test_cpu_reference_matches_native_edge_numbering_convention(self) -> None:
        rows = rt.point_closed_shape_first_boundary_crossing_2d_cpu(
            (rt.Point(id=10, x=0.0, y=0.0),),
            (
                rt.Polygon(
                    id=7,
                    vertices=((-1.0, -1.0), (1.0, -1.0), (1.0, 2.0), (-1.0, 2.0)),
                ),
            ),
        )

        self.assertEqual(rows[0]["boundary_id"], 3)
        self.assertEqual(rows[0]["shape_id"], 7)

    def test_report_records_boundary_and_pod_status(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "pod validated for native correctness",
            "host-materialized generic boundary-event rows",
            "not device-resident boundary-event columns",
            "RayJoin-specific native logic added: false",
            "does not authorize release",
            "does not authorize RayJoin reproduction",
        ):
            self.assertIn(phrase, text)

    def test_pod_artifact_records_correctness_without_claim_authorization(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["goal"], 3297)
        self.assertEqual(artifact["build"]["status"], "pass")
        self.assertEqual(artifact["focused_unittest"]["status"], "pass")
        self.assertTrue(artifact["live_smoke"]["all_match_cpu_reference"])
        self.assertEqual(artifact["live_smoke"]["phase_timings"]["mode"], "boundary_event_rows")
        self.assertEqual(artifact["live_smoke"]["phase_timings"]["emitted_count"], 1)
        self.assertFalse(any(artifact["claim_boundaries"].values()))

    @unittest.skipUnless(
        os.environ.get("RTDL_OPTIX_LIBRARY") or (ROOT / "build" / "librtdl_optix.so").exists(),
        "requires rebuilt OptiX library",
    )
    def test_live_optix_boundary_event_rows_match_cpu_reference(self) -> None:
        shapes = (
            rt.Polygon(
                id=7,
                vertices=((-1.0, -1.0), (1.0, -1.0), (1.0, 2.0), (-1.0, 2.0)),
            ),
        )
        points = (
            rt.Point(id=10, x=0.0, y=0.0),
            rt.Point(id=20, x=2.0, y=0.0),
        )
        expected = rt.point_closed_shape_first_boundary_crossing_2d_cpu(points, shapes)
        prepared = rt.prepare_point_closed_shape_membership_2d_optix(shapes)
        metadata_view = None
        try:
            observed = prepared.first_boundary_crossing(points)
            metadata_view = prepared.first_boundary_crossing_raw(points)
            metadata = metadata_view.to_v2_8_typed_result_stream_metadata()
            timings = prepared.last_phase_timings()
        finally:
            if metadata_view is not None:
                metadata_view.close()
            prepared.close()

        self.assertEqual(observed, expected)
        self.assertEqual(timings["mode"], "boundary_event_rows")
        self.assertEqual(timings["emitted_count"], len(expected))
        self.assertEqual(
            metadata["v2_8_typed_producer_metadata"]["schema_id"],
            "point_closed_shape_boundary_event_2d_columns",
        )


if __name__ == "__main__":
    unittest.main()
