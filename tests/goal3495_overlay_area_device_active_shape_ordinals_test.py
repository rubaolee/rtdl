from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3495_overlay_area_device_active_shape_ordinals_2026-06-05.md"


def _cupy_available() -> tuple[bool, str]:
    try:
        import cupy as cp  # type: ignore

        if int(cp.cuda.runtime.getDeviceCount()) <= 0:
            return False, "no CUDA device"
        return True, ""
    except Exception as exc:  # pragma: no cover
        return False, str(exc)


class _FakeRelationColumns:
    overflow = False
    row_count = 6
    left_polygon_count = 5
    right_polygon_count = 4

    def __init__(self, cp):
        self._cp = cp

    def as_cupy_ordinal_columns(self) -> dict[str, object]:
        return {
            "left_ordinal": self._cp.asarray([3, 1, 3, 2, 1, 3], dtype=self._cp.uint32),
            "right_ordinal": self._cp.asarray([0, 2, 2, 1, 0, 2], dtype=self._cp.uint32),
        }


class Goal3495OverlayAreaDeviceActiveShapeOrdinalsTest(unittest.TestCase):
    def test_active_shape_ordinals_api_is_exported(self) -> None:
        self.assertTrue(hasattr(rt, "ShapePairActiveShapeOrdinalsCupyResult"))
        self.assertTrue(hasattr(rt, "shape_pair_relation_active_shape_ordinals_cupy"))
        self.assertTrue(hasattr(rt, "GEOMETRY_RELATION_ACTIVE_SHAPE_ORDINALS_CUPY_VERSION"))

    def test_active_shape_ordinals_match_expected_when_cupy_available(self) -> None:
        available, reason = _cupy_available()
        if not available:
            self.skipTest(f"CuPy/CUDA unavailable: {reason}")
        import cupy as cp  # type: ignore

        result = rt.shape_pair_relation_active_shape_ordinals_cupy(_FakeRelationColumns(cp))
        metadata = result.to_metadata()

        self.assertEqual(cp.asnumpy(result.left_unique_ordinals).tolist(), [1, 2, 3])
        self.assertEqual(cp.asnumpy(result.left_relation_counts).tolist(), [2, 1, 3])
        self.assertEqual(cp.asnumpy(result.right_unique_ordinals).tolist(), [0, 1, 2])
        self.assertEqual(cp.asnumpy(result.right_relation_counts).tolist(), [2, 1, 3])
        self.assertEqual(metadata["schema"], rt.GEOMETRY_RELATION_ACTIVE_SHAPE_ORDINALS_CUPY_VERSION)
        self.assertEqual(metadata["row_count"], 6)
        self.assertEqual(metadata["left_unique_shape_count"], 3)
        self.assertEqual(metadata["right_unique_shape_count"], 3)
        self.assertFalse(metadata["relation_row_ordinals_materialized"])
        self.assertTrue(metadata["unique_ordinals_device_resident"])
        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "full_overlay_area_claim_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(metadata[field])

    def test_runner_exposes_device_active_shape_ordinal_mode(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--device-active-shape-ordinals",
            "shape_pair_relation_active_shape_ordinals_cupy",
            "device_active_shape_ordinals_used",
            "active_shape_ordinal_metadata",
            "relation_ordinal_download",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_documents_remaining_host_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "unique active-shape discovery step to CuPy",
            "does not make tile-task planning device-resident",
            "does not authorize release",
            "shape_pair_relation_flags_with_ordinals_and_geometry_payload",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_spatial_rayjoin_gap_row_records_device_active_ordinals(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("Goal3495", spatial["evidence_refs"])
        self.assertIn("unique active shape ordinals", spatial["current_bottleneck"])
        self.assertFalse(spatial["release_authorized"])


if __name__ == "__main__":
    unittest.main()
