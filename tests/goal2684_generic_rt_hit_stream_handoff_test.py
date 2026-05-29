from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.reference import Ray3D
from rtdsl.reference import Triangle3D

from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb


ROOT = Path(__file__).resolve().parents[1]


def _rays() -> tuple[Ray3D, ...]:
    return (
        Ray3D(10, 0.25, 0.25, -1.0, 0.0, 0.0, 1.0, 2.0),
        Ray3D(11, 0.20, 0.20, -1.0, 0.0, 0.0, 1.0, 2.0),
        Ray3D(12, 2.25, 0.25, -1.0, 0.0, 0.0, 1.0, 2.0),
    )


def _triangles() -> tuple[Triangle3D, ...]:
    return (
        Triangle3D(100, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
        Triangle3D(101, 2.0, 0.0, 0.0, 3.0, 0.0, 0.0, 2.0, 1.0, 0.0),
    )


class Goal2684GenericRtHitStreamHandoffTest(unittest.TestCase):
    def test_cpu_hit_stream_contract_dedupes_primitives_fail_closed(self) -> None:
        result = rt.run_generic_ray_triangle_hit_stream_3d(
            _rays(),
            _triangles(),
            backend="cpu",
            deduplicate_primitives=True,
        )
        self.assertEqual(result["primitive"], rt.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE)
        self.assertEqual(result["row_schema"], rt.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA)
        self.assertFalse(result["overflow"])
        self.assertEqual(result["hit_event_count_before_dedup"], 3)
        self.assertEqual(
            tuple(row["primitive_id"] for row in result["rows"]),
            (0, 1),
        )

        overflow = rt.run_generic_ray_triangle_hit_stream_3d(
            _rays(),
            _triangles(),
            backend="cpu",
            max_rows=1,
            deduplicate_primitives=True,
        )
        self.assertTrue(overflow["overflow"])
        self.assertEqual(overflow["rows"], ())
        self.assertEqual(overflow["row_count"], 0)
        self.assertEqual(overflow["attempted_row_count"], 2)

    def test_cpu_hit_stream_can_reproduce_grouped_reduction_input(self) -> None:
        hit_stream = rt.run_generic_ray_triangle_hit_stream_3d(
            _rays(),
            _triangles(),
            backend="cpu",
            deduplicate_primitives=True,
        )
        group_ids = (7, 9)
        values = (3, 5)
        gathered_groups = tuple(group_ids[int(row["primitive_id"])] for row in hit_stream["rows"])
        gathered_values = tuple(values[int(row["primitive_id"])] for row in hit_stream["rows"])
        self.assertEqual(gathered_groups, (7, 9))
        self.assertEqual(gathered_values, (3, 5))

        grouped = rt.run_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
            _rays(),
            _triangles(),
            primitive_group_ids=group_ids,
            primitive_values=values,
            reduction="sum_count",
            deduplicate_primitives=True,
            backend="cpu",
        )
        self.assertEqual(grouped["rows"], ({"group_id": 7, "sum": 3, "count": 1}, {"group_id": 9, "sum": 5, "count": 1}))

    def test_native_abi_is_app_free_hit_stream(self) -> None:
        files = (
            ROOT / "src/native/embree/rtdl_embree_prelude.h",
            ROOT / "src/native/optix/rtdl_optix_prelude.h",
            ROOT / "src/native/embree/rtdl_embree_api.cpp",
            ROOT / "src/native/optix/rtdl_optix_api.cpp",
            ROOT / "src/native/optix/rtdl_optix_workloads.cpp",
        )
        text = "\n".join(path.read_text() for path in files)
        self.assertIn("RtdlRayTriangleHitStreamRow", text)
        self.assertIn("rtdl_embree_static_triangle_scene_3d_ray_triangle_hit_stream", text)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream", text)
        self.assertIn("deduplicate_primitives", text)
        self.assertNotIn("RayDB", text)
        self.assertNotIn("SQL", text)

    def test_raydb_full_path_mapping_is_correct_with_reference_continuation(self) -> None:
        fixture = raydb.make_fixture(copies=1)
        plan = raydb.make_plan("sum")
        result = raydb._run_paper_rt_hit_stream_triton_result_mode(
            fixture=fixture,
            plan=plan,
            mode="sum",
            copies=1,
            backend="cpu",
            backend_label="paper_rt_cpu_hit_stream_reference",
            allow_reference_fallback=True,
        )
        self.assertTrue(result["matches_cpu_reference"])
        metadata = result["metadata"]
        self.assertEqual(metadata["hit_stream_row_schema"], list(rt.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA))
        self.assertEqual(metadata["continuation_execution_path"], "reference_fallback")
        self.assertIn("No RayDB, SQL, table, or database semantics", metadata["engine_boundary"])


if __name__ == "__main__":
    unittest.main()
