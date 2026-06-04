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
REPORT = ROOT / "docs" / "reports" / "goal3298_closed_shape_boundary_event_device_columns_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3298_closed_shape_boundary_event_device_columns_pod_2026-06-04.json"


class Goal3298ClosedShapeBoundaryEventDeviceColumnsTest(unittest.TestCase):
    def test_native_abi_adds_generic_boundary_event_device_columns(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")

        self.assertIn("RtdlNativeClosedShapeBoundaryEventDeviceColumns", prelude)
        for symbol in (
            "rtdl_optix_prepared_point_closed_shape_first_boundary_crossing_device_columns_2d",
            "rtdl_optix_release_point_closed_shape_boundary_event_device_columns_2d",
        ):
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)
        self.assertNotIn("rayjoin", prelude.lower())

    def test_kernel_supports_soa_boundary_event_columns(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        for field in (
            "point_ids_out",
            "shape_ids_out",
            "boundary_ids_out",
            "crossing_t_out",
            "crossing_x_out",
            "crossing_y_out",
            "event_kinds_out",
        ):
            self.assertIn(field, core)
            self.assertIn(field, workloads)
        self.assertIn("NativeClosedShapeBoundaryEventDeviceColumnsOwner", workloads)
        self.assertIn("reset_closed_shape_membership_phase_timings(7u)", workloads)
        self.assertNotIn("closest_eid", core.lower())
        self.assertNotIn("rayjoin", core.lower())

    def test_python_runtime_exposes_device_column_surface(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("OPTIX_CLOSED_SHAPE_FIRST_BOUNDARY_CROSSING_DEVICE_COLUMNS_SYMBOL", runtime)
        self.assertIn("_RtdlNativeClosedShapeBoundaryEventDeviceColumns", runtime)
        self.assertIn("OptixClosedShapeBoundaryEventDeviceColumnOutput", runtime)
        self.assertIn("def first_boundary_crossing_device_columns", runtime)
        self.assertIn('"boundary_event_device_columns"', runtime)
        self.assertIn('"device_resident_boundary_event_columns"', runtime)

    def test_report_records_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "pod validated for device-column correctness",
            "device-resident boundary-event columns",
            "does not yet add the grouped/count continuation",
            "does not prove true zero-copy",
            "RayJoin-specific native logic added: false",
            "does not authorize RayJoin reproduction",
        ):
            self.assertIn(phrase, text)

    def test_pod_artifact_records_device_columns_without_claim_authorization(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["goal"], 3298)
        self.assertEqual(artifact["build"]["status"], "pass")
        self.assertEqual(artifact["focused_unittest"]["status"], "pass")
        self.assertEqual(artifact["focused_unittest"]["skipped"], 0)
        self.assertTrue(artifact["live_smoke"]["all_match_cpu_reference"])
        self.assertTrue(artifact["live_smoke"]["device_resident"])
        self.assertTrue(all(artifact["live_smoke"]["device_ptrs_nonzero"].values()))
        self.assertEqual(artifact["live_smoke"]["phase_timings"]["mode"], "boundary_event_device_columns")
        self.assertEqual(artifact["live_smoke"]["phase_timings"]["candidate_download"], 0.0)
        self.assertFalse(any(artifact["claim_boundaries"].values()))

    @unittest.skipUnless(
        os.environ.get("RTDL_OPTIX_LIBRARY") or (ROOT / "build" / "librtdl_optix.so").exists(),
        "requires rebuilt OptiX library",
    )
    def test_live_device_columns_match_cpu_reference_when_cupy_available(self) -> None:
        try:
            import cupy as cp  # type: ignore
        except Exception as exc:  # pragma: no cover - depends on pod image
            self.skipTest(f"requires CuPy to inspect CUDA columns: {exc}")

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
        columns = None
        try:
            try:
                columns = prepared.first_boundary_crossing_device_columns(points, max_rows=4)
            except RuntimeError as exc:
                if "does not export" in str(exc):
                    self.skipTest(str(exc))
                raise
            self.assertTrue(columns.device_resident)
            metadata = columns.to_metadata()
            cupy_columns = columns.as_cupy_columns()
            cp.cuda.Stream.null.synchronize()
            observed = tuple(
                {
                    "point_id": int(cupy_columns["point_id"].get()[index]),
                    "shape_id": int(cupy_columns["shape_id"].get()[index]),
                    "boundary_id": int(cupy_columns["boundary_id"].get()[index]),
                    "crossing_t": float(cupy_columns["crossing_t"].get()[index]),
                    "crossing_x": float(cupy_columns["crossing_x"].get()[index]),
                    "crossing_y": float(cupy_columns["crossing_y"].get()[index]),
                    "event_kind": int(cupy_columns["event_kind"].get()[index]),
                }
                for index in range(columns.row_count)
            )
            timings = prepared.last_phase_timings()
        finally:
            if columns is not None:
                columns.close()
            prepared.close()

        self.assertEqual(observed, expected)
        self.assertEqual(timings["mode"], "boundary_event_device_columns")
        self.assertEqual(timings["emitted_count"], len(expected))
        self.assertEqual(
            metadata["v2_8_typed_producer_metadata"]["producer_output_residency"],
            "device_resident_boundary_event_columns",
        )
        self.assertFalse(metadata["runtime"]["true_zero_copy_authorized"])


if __name__ == "__main__":
    unittest.main()
