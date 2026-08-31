from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest import mock

import rtdsl as rt
from rtdsl import aabb_index


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "embree" / "rtdl_embree_prelude.h"
SCENE = ROOT / "src" / "native" / "embree" / "rtdl_embree_scene.cpp"
API = ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "embree_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal4340_embree_native_aabb_index_route_2026-06-11.md"
SUMMARY = ROOT / "docs" / "reports" / "goal4340_embree_native_aabb_index_local_linux" / "summary.json"


class _FakeNativeEmbreeAabbIndex:
    native_aabb_index = True

    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def count(self, *, point_queries=(), box_queries=(), operation: str) -> int:
        if operation == "point_contains":
            self.calls.append((operation, len(tuple(point_queries))))
            return 2
        self.calls.append((operation, len(tuple(box_queries))))
        return 30 if operation == "range_contains" else 300


class _FakeEmbree3Library:
    def rtdl_embree_get_version(self, major, minor, patch) -> int:
        major._obj.value = 3
        minor._obj.value = 13
        patch._obj.value = 5
        return 0

    def rtdl_embree_prepare_aabb_index_2d(self, *_: object) -> int:
        return 0

    def rtdl_embree_count_prepared_aabb_index_2d(self, *_: object) -> int:
        return 0

    def rtdl_embree_destroy_prepared_aabb_index_2d(self, *_: object) -> None:
        return None


class Goal4340EmbreeNativeAabbIndexRouteTest(unittest.TestCase):
    def test_native_abi_and_collision_route_are_present(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        scene = SCENE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")

        for symbol in (
            "rtdl_embree_prepare_aabb_index_2d",
            "rtdl_embree_count_prepared_aabb_index_2d",
            "rtdl_embree_destroy_prepared_aabb_index_2d",
        ):
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)
            self.assertIn(symbol, runtime)
        self.assertIn("struct RtdlAabb2D", prelude)
        self.assertIn("void aabb2d_bounds", scene)
        self.assertIn("rtcCollide", api)
        self.assertIn("std::atomic<size_t> count", api)
        self.assertIn("fetch_add(1, std::memory_order_relaxed)", api)
        self.assertIn("prepare_embree_aabb_index_2d", rt.__all__)
        self.assertIn("PreparedEmbreeAabbIndex2D", rt.__all__)

    def test_availability_requires_embree4_collision_support(self) -> None:
        from rtdsl import embree_runtime

        fake = _FakeEmbree3Library()
        with mock.patch.object(embree_runtime, "_load_embree_library", return_value=fake):
            self.assertFalse(embree_runtime.embree_aabb_index_2d_available())
            with self.assertRaisesRegex(RuntimeError, "requires Embree 4 collision support"):
                embree_runtime.PreparedEmbreeAabbIndex2D([(0.0, 0.0, 1.0, 1.0)])

    def test_high_level_embree_aabb_uses_native_batch_when_available(self) -> None:
        fake = _FakeNativeEmbreeAabbIndex()
        boxes = (
            aabb_index.Aabb2D(0.0, 0.0, 1.0, 1.0),
            aabb_index.Aabb2D(2.0, 2.0, 3.0, 3.0),
        )
        with mock.patch("rtdsl.embree_runtime.embree_aabb_index_2d_available", return_value=True):
            with mock.patch("rtdsl.embree_runtime.prepare_embree_aabb_index_2d", return_value=fake):
                prepared = aabb_index._prepare_embree_aabb_index_2d(boxes, row_ids=(10, 11))

        result = prepared.count(
            point_queries=((0.5, 0.5), (2.5, 2.5)),
            box_queries=((0.0, 0.0, 0.25, 0.25), (2.0, 2.0, 2.5, 2.5), (4.0, 4.0, 5.0, 5.0)),
            operation="all",
        )

        self.assertEqual(result["counts"], {"point_contains": 2, "range_contains": 30, "range_intersects": 300})
        self.assertEqual(
            fake.calls,
            [("point_contains", 2), ("range_contains", 3), ("range_intersects", 3)],
        )
        self.assertEqual(result["index"]["native_index"], "embree_native_aabb_collision_index")
        self.assertFalse(result["rt_core_accelerated"])
        self.assertFalse(result["native_engine_customization"])

    def test_report_and_linux_summary_record_the_speedup_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertIn("Goal4340", report)
        self.assertIn("AABB_INDEX_QUERY_2D", report)
        self.assertIn("3740.9x", report)
        self.assertIn("does not authorize public release", report)
        self.assertTrue(summary["small_validated"]["matches_cpu_reference"])
        self.assertEqual(summary["large_1024_skip_counts"]["native_index"], "embree_native_aabb_collision_index")
        self.assertGreater(summary["query_median_speedup_vs_columnar_fallback"], 1000.0)


if __name__ == "__main__":
    unittest.main()
