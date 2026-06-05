from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3486_overlay_area_cupy_tiled_prototype_2026-06-05.md"


def _fixture_payloads():
    concave_l = ((0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0))
    square = ((0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5))
    left = rt.prepare_simple_polygon_component_payload((concave_l,))
    right = rt.prepare_simple_polygon_component_payload((square,))
    rows = rt.prepare_overlay_area_pair_rows(left, right, ((0, 0),))
    return left, right, rows


def _cupy_available() -> tuple[bool, str]:
    try:
        import cupy as cp  # type: ignore

        if int(cp.cuda.runtime.getDeviceCount()) <= 0:
            return False, "no CUDA device"
        return True, ""
    except Exception as exc:  # pragma: no cover - depends on optional CUDA stack.
        return False, str(exc)


class Goal3486OverlayAreaCupyTiledPrototypeTest(unittest.TestCase):
    def test_cupy_prototype_rejects_invalid_scratch_capacity_before_import_requirement(self) -> None:
        left, right, rows = _fixture_payloads()

        with self.assertRaisesRegex(ValueError, "scratch capacity must fail closed"):
            rt.evaluate_prepared_overlay_area_scalar_tiled_cupy(
                left,
                right,
                rows,
                max_triangle_pairs_per_tile=0,
            )

    def test_cupy_version_is_exported(self) -> None:
        self.assertEqual(
            rt.V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_CUPY_VERSION,
            "rtdl.v2_8.simple_polygon_overlay_area_prepared_payload_cupy_tiled.v1",
        )

    def test_cupy_tiled_prototype_matches_cpu_when_cuda_is_available(self) -> None:
        available, reason = _cupy_available()
        if not available:
            self.skipTest(f"CuPy/CUDA unavailable: {reason}")
        import cupy as cp  # type: ignore

        left, right, rows = _fixture_payloads()
        cpu = rt.evaluate_prepared_overlay_area_scalar_tiled(
            left,
            right,
            rows,
            max_triangle_pairs_per_tile=3,
        )
        gpu = rt.evaluate_prepared_overlay_area_scalar_tiled_cupy(
            left,
            right,
            rows,
            max_triangle_pairs_per_tile=3,
        )
        metadata = gpu.to_metadata()

        self.assertAlmostEqual(float(cp.asnumpy(gpu.row_areas)[0]), cpu.total_area)
        self.assertEqual(int(cp.asnumpy(gpu.processed_pairs)[0]), cpu.triangle_pair_count)
        self.assertEqual(int(cp.asnumpy(gpu.tile_counts)[0]), cpu.tile_count)
        self.assertEqual(int(cp.asnumpy(gpu.row_status)[0]), 0)
        self.assertEqual(metadata["status_counts"], {"0": 1})
        self.assertEqual(metadata["processed_triangle_pair_count"], 8)
        self.assertEqual(metadata["tile_count"], 3)
        self.assertTrue(metadata["completed_without_truncation"])
        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "runtime_kernel_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(metadata[field])

    def test_report_documents_cupy_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "CuPy RawKernel",
            "prepared simple polygon component payload",
            "bounded triangle-pair tiles",
            "not the final native runtime path",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
