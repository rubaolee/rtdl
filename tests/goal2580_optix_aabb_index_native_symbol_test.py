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
            "rtdl_optix_prepare_aabb_index_2d",
            "rtdl_optix_count_prepared_aabb_index_2d",
            "rtdl_optix_prepare_aabb_point_queries_2d",
            "rtdl_optix_prepare_aabb_box_queries_2d",
            "rtdl_optix_count_prepared_aabb_index_2d_packed_queries",
            "rtdl_optix_destroy_prepared_aabb_index_2d",
        ):
            self.assertIn(symbol, prelude + api)
        self.assertIn("PreparedAabbIndex2DOptix", workloads)
        self.assertIn("PreparedAabbIndexQueries2DOptix", workloads)
        self.assertIn("prepare_optix_aabb_index_2d", wrapper)
        self.assertIn("prepare_optix_aabb_point_queries_2d", wrapper)
        self.assertIn("prepare_optix_aabb_box_queries_2d", wrapper)
        self.assertNotIn("librts", (prelude + api + workloads).lower())

    def test_optix_range_intersects_is_supported_by_contract_and_wrapper(self) -> None:
        self.assertIn("range_intersects", rt.AABB_INDEX_2D_OPERATIONS)
        self.assertIn("range_intersects", rt.AABB_INDEX_2D_CONTRACT["operations"])
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        wrapper = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        self.assertIn("kAabbIndexOpRangeIntersects", workloads)
        self.assertIn("count_prepared_aabb_index_2d_range_intersects_optix", workloads)
        self.assertIn("OPTIX_AABB_INDEX_RANGE_INTERSECTS = 3", wrapper)

    def test_contract_documents_count_only_optix_boundary(self) -> None:
        self.assertEqual(
            rt.AABB_INDEX_2D_CONTRACT["backend_status"]["optix"],
            "native_count_only_point_contains_range_contains_range_intersects",
        )
        self.assertIn("prepare_optix_aabb_index_2d", rt.__all__)
        self.assertIn("prepare_optix_aabb_point_queries_2d", rt.__all__)
        self.assertIn("prepare_optix_aabb_box_queries_2d", rt.__all__)
        self.assertIn("PreparedOptixAabbIndex2D", rt.__all__)
        self.assertIn("PreparedOptixAabbQueries2D", rt.__all__)


if __name__ == "__main__":
    unittest.main()
