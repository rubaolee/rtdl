from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class OptixAabbIndexNativeSymbolTest(unittest.TestCase):
    def test_optix_aabb_index_exports_are_app_agnostic(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        wrapper = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")

        for symbol in (
            "RtdlAabb2D",
            "RtdlAabbPairRow",
            "rtdl_optix_prepare_aabb_index_2d",
            "rtdl_optix_count_prepared_aabb_index_2d",
            "rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows",
            "rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows",
            "rtdl_optix_prepare_aabb_point_queries_2d",
            "rtdl_optix_prepare_aabb_box_queries_2d",
            "rtdl_optix_prepare_aabb_point_query_columns_f32_2d",
            "rtdl_optix_prepare_aabb_box_query_columns_f32_2d",
            "rtdl_optix_count_prepared_aabb_index_2d_packed_queries",
            "rtdl_optix_destroy_prepared_aabb_index_2d",
        ):
            self.assertIn(symbol, prelude + api)
        self.assertIn("PreparedAabbIndex2DOptix", workloads)
        self.assertIn("PreparedAabbIndexQueries2DOptix", workloads)
        self.assertIn("DevPtr d_query_hit_counts", workloads)
        self.assertIn("DevPtr d_total_hit_count", workloads)
        self.assertIn("DevPtr d_launch_params", workloads)
        self.assertIn("prepared_queries->d_query_hit_counts.ptr", workloads)
        self.assertIn("prepared_queries->d_total_hit_count.ptr", workloads)
        self.assertIn("prepared_queries->d_launch_params.ptr", workloads)
        self.assertIn("prepare_optix_aabb_index_2d", wrapper)
        self.assertIn("collect_aabb_intersection_pair_rows_2d_optix", wrapper)
        self.assertIn("prepare_optix_aabb_point_queries_2d", wrapper)
        self.assertIn("prepare_optix_aabb_box_queries_2d", wrapper)
        self.assertIn("prepare_optix_aabb_point_query_columns_f32_2d", wrapper)
        self.assertIn("prepare_optix_aabb_box_query_columns_f32_2d", wrapper)
        self.assertIn("range_intersects_ready", workloads)
        self.assertNotIn("librts", (prelude + api + workloads).lower())

    def test_optix_range_intersects_is_supported_by_contract_and_wrapper(self) -> None:
        self.assertIn("range_intersects", rt.AABB_INDEX_2D_OPERATIONS)
        self.assertIn("range_intersects", rt.AABB_INDEX_2D_CONTRACT["operations"])
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        wrapper = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        self.assertIn("kAabbIndexOpRangeIntersects", workloads)
        self.assertIn("count_prepared_aabb_index_2d_range_intersects_optix", workloads)
        self.assertIn("OPTIX_AABB_INDEX_RANGE_INTERSECTS = 3", wrapper)

    def test_prepared_index_materializes_pipeline_before_return(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )
        constructor = workloads[
            workloads.index("struct PreparedAabbIndex2DOptix"):
            workloads.index("static void require_prepared_aabb_index_2d_valid")
        ]
        self.assertIn("ensure_aabb_index_count_2d_pipeline();", constructor)
        self.assertLess(
            constructor.index("ensure_aabb_index_count_2d_pipeline();"),
            constructor.index("if (count == 0) return;"),
        )

    def test_prepared_query_count_returns_only_a_device_scalar(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )
        kernel = workloads[
            workloads.index('extern "C" __global__ void __intersection__aabb_index_exact'):
            workloads.index('extern "C" __global__ void __anyhit__aabb_index_count')
        ]
        self.assertIn("atomicAdd(params.query_hit_counts + qidx, 1u)", kernel)
        self.assertIn("rtdl_device_u32_sum_u64", workloads)
        self.assertIn("reduce_device_u32_sum_u64", workloads)
        packed = workloads[
            workloads.index("static void count_prepared_aabb_index_2d_packed_queries_optix"):
            workloads.index("static unsigned long long count_prepared_aabb_index_2d_with_scratch_optix")
        ]
        self.assertIn("prepared_queries->d_total_hit_count.ptr", packed)

    def test_typed_query_columns_remain_soa_through_optix_launch(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )
        prepared = workloads[
            workloads.index("struct PreparedAabbIndexQueries2DOptix"):
            workloads.index("static uint32_t validate_aabb_index_operation")
        ]
        kernel = workloads[
            workloads.index("static const char* kAabbIndexCountKernelSrc"):
            workloads.index("static void ensure_aabb_index_count_2d_pipeline")
        ]

        self.assertIn("bool query_columns_f32 = false", prepared)
        for field in ("d_query_min_x", "d_query_min_y", "d_query_max_x", "d_query_max_y"):
            self.assertIn(f"DevPtr {field}", prepared)
        self.assertIn("query_columns_f32(true)", prepared)
        self.assertIn("query_columns_f32(!build_query_accel)", prepared)
        self.assertIn("upload(d_query_min_x.ptr, point_x, point_query_count)", prepared)
        self.assertIn("upload(d_query_max_y.ptr, maximum_y, box_query_count)", prepared)
        self.assertIn("if (params.query_columns_f32 != 0u)", kernel)
        self.assertIn("const GpuPoint q = load_query_point(idx)", kernel)
        self.assertIn("const GpuAabb2D q = load_query_box(idx)", kernel)
        self.assertIn("return params.point_queries[index]", kernel)
        self.assertIn("return params.box_queries[index]", kernel)
        self.assertIn("point query columns contain nonfinite coordinates", prepared)
        self.assertIn("box query columns contain nonfinite coordinates", prepared)
        self.assertIn("box query columns contain inverted bounds", prepared)

    def test_contract_documents_optix_row_output_boundary(self) -> None:
        wrapper = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        self.assertEqual(
            rt.AABB_INDEX_2D_CONTRACT["backend_status"]["optix"],
            "native_count_point_contains_range_contains_range_intersects_point_contains_rows_and_range_intersection_rows",
        )
        self.assertIn("collect_aabb_intersection_pair_rows_2d_optix", rt.__all__)
        self.assertIn("collect_aabb_point_membership_pair_rows_2d_optix", rt.__all__)
        self.assertIn("prepare_optix_aabb_index_2d", rt.__all__)
        self.assertIn("prepare_optix_aabb_point_queries_2d", rt.__all__)
        self.assertIn("prepare_optix_aabb_box_queries_2d", rt.__all__)
        self.assertIn("prepare_optix_aabb_point_query_columns_f32_2d", rt.__all__)
        self.assertIn("prepare_optix_aabb_box_query_columns_f32_2d", rt.__all__)
        self.assertIn(
            "prepared OptiX AABB query layout does not match the operation",
            wrapper,
        )
        self.assertIn("PreparedOptixAabbIndex2D", rt.__all__)
        self.assertIn("PreparedOptixAabbQueries2D", rt.__all__)


if __name__ == "__main__":
    unittest.main()
