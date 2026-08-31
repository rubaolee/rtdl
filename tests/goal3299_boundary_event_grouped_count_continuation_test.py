from __future__ import annotations

import json
import os
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal3299_boundary_event_grouped_count_continuation_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3299_boundary_event_grouped_count_continuation_pod_2026-06-04.json"


class Goal3299BoundaryEventGroupedCountContinuationTest(unittest.TestCase):
    def test_runtime_adds_generic_grouped_count_continuation(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("def grouped_count_by_point_id_device_columns", runtime)
        self.assertIn("OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_DEVICE_COLUMNS_WITH_CAPACITY_SYMBOL", runtime)
        self.assertIn('name = b"point_id"', runtime)
        self.assertNotIn("closest_eid", runtime.lower())

    def test_report_records_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "pod validated for continuation correctness",
            "generic grouped-count continuation",
            "No new native app-specific kernel was added",
            "does not encode RayJoin polygon assignment",
            "does not prove true zero-copy",
            "RayJoin-specific native logic added: false",
        ):
            self.assertIn(phrase, text)

    def test_pod_artifact_records_resident_continuation_without_claim_authorization(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["goal"], 3299)
        self.assertEqual(artifact["focused_unittest"]["status"], "pass")
        self.assertEqual(artifact["focused_unittest"]["skipped"], 0)
        self.assertTrue(artifact["live_smoke"]["event_device_resident"])
        self.assertTrue(artifact["live_smoke"]["count_device_resident"])
        self.assertEqual(artifact["live_smoke"]["point_10_count"], 1)
        self.assertEqual(artifact["live_smoke"]["point_20_count"], 0)
        self.assertEqual(artifact["live_smoke"]["event_timing_mode"], "boundary_event_device_columns")
        self.assertEqual(artifact["live_smoke"]["count_output_residency"], "device_resident_dense_grouped_count_column")
        self.assertFalse(any(artifact["claim_boundaries"].values()))

    @unittest.skipUnless(
        os.environ.get("RTDL_OPTIX_LIBRARY") or (ROOT / "build" / "librtdl_optix.so").exists(),
        "requires rebuilt OptiX library",
    )
    def test_live_boundary_event_grouped_count_stays_on_device(self) -> None:
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
        prepared = rt.prepare_point_closed_shape_membership_2d_optix(shapes)
        event_columns = None
        count_columns = None
        try:
            event_columns = prepared.first_boundary_crossing_device_columns(points, max_rows=4)
            count_columns = event_columns.grouped_count_by_point_id_device_columns(group_capacity=32)
            cp.cuda.Stream.null.synchronize()
            counts = count_columns.as_cupy_counts().get()
            event_metadata = event_columns.to_metadata()
            count_metadata = count_columns.to_metadata()
        finally:
            if count_columns is not None:
                count_columns.close()
            if event_columns is not None:
                event_columns.close()
            prepared.close()

        self.assertEqual(event_metadata["runtime"]["output_residency"], "device_resident_boundary_event_columns")
        self.assertEqual(int(counts[10]), 1)
        self.assertEqual(int(counts[20]), 0)
        self.assertEqual(count_metadata["output_residency"], "device_resident_dense_grouped_count_column")
        self.assertFalse(count_metadata["true_zero_copy_authorized"])


if __name__ == "__main__":
    unittest.main()
