from __future__ import annotations

from dataclasses import dataclass
import inspect
from pathlib import Path
import unittest

from examples.benchmark_apps.spatial_rayjoin import (
    rtdl_rayjoin_v2_spatial_join_app as rayjoin_app,
)
from rtdsl import embree_runtime
from rtdsl import optix_runtime


@dataclass(frozen=True)
class SegmentRow:
    id: int
    x0: float
    y0: float
    x1: float
    y1: float


def _packed_ids(packed) -> list[int]:
    return [int(packed.records[index].id) for index in range(int(packed.count))]


class Goal3285FusedSegmentPackOrderModeTest(unittest.TestCase):
    def test_embree_pack_segments_orders_records_without_separate_helper(self) -> None:
        segments = (
            SegmentRow(30, 2.0, 0.0, 4.0, 0.0),
            SegmentRow(10, 1.0, 3.0, 3.0, 3.0),
            SegmentRow(20, 1.0, 2.0, 1.0, 2.0),
        )

        packed = embree_runtime.pack_segments(records=segments, order_mode="x_then_y")

        self.assertEqual(_packed_ids(packed), [20, 10, 30])

    def test_optix_pack_segments_delegates_to_same_ordered_contract(self) -> None:
        segments = (
            {"id": 4, "x0": 1.0, "y0": 1.0, "x1": 1.0, "y1": 1.0},
            {"id": 1, "x0": 0.0, "y0": 0.0, "x1": 0.0, "y1": 0.0},
            {"id": 3, "x0": 1.0, "y0": 0.0, "x1": 1.0, "y1": 0.0},
            {"id": 2, "x0": 0.0, "y0": 1.0, "x1": 0.0, "y1": 1.0},
        )

        packed = optix_runtime.pack_segments(records=segments, order_mode="morton_xy")

        self.assertEqual(_packed_ids(packed), [1, 3, 2, 4])

    def test_ordered_pack_supports_column_inputs(self) -> None:
        packed = embree_runtime.pack_segments(
            ids=[30, 10, 20],
            x0=[2.0, 1.0, 1.0],
            y0=[0.0, 3.0, 2.0],
            x1=[4.0, 3.0, 1.0],
            y1=[0.0, 3.0, 2.0],
            order_mode="y_then_x",
        )

        self.assertEqual(_packed_ids(packed), [30, 20, 10])

    def test_invalid_order_mode_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "order_mode"):
            embree_runtime.pack_segments(records=(), order_mode="hilbert")

    def test_segment_ids_must_fit_packed_native_abi(self) -> None:
        too_large_id = (1 << 32)
        segments = (
            SegmentRow(too_large_id, 0.0, 0.0, 1.0, 1.0),
        )

        with self.assertRaisesRegex(ValueError, "uint32 packed segment ABI"):
            embree_runtime.pack_segments(records=segments)
        with self.assertRaisesRegex(ValueError, "uint32 packed segment ABI"):
            embree_runtime.pack_segments(records=segments, order_mode="x_then_y")

    def test_rayjoin_lsi_uses_fused_pack_order_path(self) -> None:
        source = inspect.getsource(rayjoin_app.run_rayjoin_prepared_optix_workload)

        self.assertIn("order_mode=segment_order_mode", source)
        self.assertIn("static_segment_pack_sec", source)
        self.assertNotIn("query_segment_order_sec", source)
        self.assertNotIn("static_segment_order_sec", source)

    def test_repeated_runner_summarizes_static_segment_pack_phase(self) -> None:
        root = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
        runner = root / "scripts" / "goal3244_rayjoin_same_slice_repeated_count_runner.py"
        source = runner.read_text(encoding="utf-8")

        self.assertIn("static_segment_pack_sec", source)
        self.assertIn("\"static_segment_pack_ms\"", source)


if __name__ == "__main__":
    unittest.main()
