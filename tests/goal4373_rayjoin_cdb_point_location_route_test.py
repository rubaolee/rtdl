from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal4373RayjoinCdbPointLocationRouteTest(unittest.TestCase):
    def test_cdb_adapter_preserves_face_ids(self) -> None:
        datasets = (ROOT / "src" / "rtdsl" / "datasets.py").read_text(encoding="utf-8")
        self.assertIn("def chains_to_rayjoin_cdb_segments", datasets)
        self.assertIn('"left_face_id": chain.left_face_id', datasets)
        self.assertIn('"right_face_id": chain.right_face_id', datasets)

    def test_optix_route_exports_prepared_cdb_point_location(self) -> None:
        prelude = (ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h").read_text(encoding="utf-8")
        core = (ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        self.assertIn("RtdlRayjoinCdbSegment", prelude)
        self.assertIn("RtdlRayjoinCdbPointLocationRow", prelude)
        self.assertIn("RtdlDirectedSegmentFace2D", prelude)
        self.assertIn("RtdlDirectedSegmentPointLocationRow2D", prelude)
        self.assertIn("rtdl_optix_prepare_directed_segment_point_location_2d", prelude)
        self.assertIn("rtdl_optix_write_prepared_directed_segment_point_location_2d_device_segment_ids", prelude)
        self.assertIn("rtdl_optix_write_prepared_directed_segment_point_location_2d_device_face_ids", prelude)
        self.assertIn("rtdl_optix_prepare_rayjoin_cdb_point_location_2d", prelude)
        self.assertIn("rtdl_optix_write_prepared_rayjoin_cdb_point_location_2d_device_segment_ids", prelude)
        self.assertIn("rtdl_optix_write_prepared_rayjoin_cdb_point_location_2d_device_face_ids", prelude)
        self.assertIn("kRayjoinCdbPointLocationKernelSrc", core)
        self.assertIn("__closesthit__rayjoin_cdb_point_location", core)
        self.assertIn("GpuRayjoinCdbSegmentRange", core)
        self.assertIn("const GpuRayjoinCdbSegmentRange range = params.ranges", core)
        self.assertIn("params.canonical_segment_ids[p3]", core)
        self.assertIn("params.canonical_face_ids[p3]", core)
        self.assertIn("params.output[idx].segment_id = segment_id;", core)
        self.assertIn("params.segment_id_output[idx] = segment_id;", core)
        self.assertIn("params.face_id_output[idx] = face_id;", core)
        self.assertIn("face_for_segment_direction", core)
        self.assertIn("static __forceinline__ __device__ double cdb_absd", core)
        self.assertIn("const double point_x = static_cast<double>(point.x);", core)
        self.assertIn("optixSetPayload_3(best_segment_index)", core)
        self.assertIn("directed_segment_sos_segment_is_better", core)
        self.assertNotIn("directed_segment_sos_direction_is_preferred", core)
        self.assertIn("directed_segment_sos_tie_breaker", core)
        self.assertIn("directed_segment_sos_report_t", core)
        self.assertIn("atan(slope)", core)
        self.assertIn("query_map_id == 0u ? current_slope > best_slope : current_slope < best_slope", core)
        self.assertIn("factor * (1.0 - tie_breaker) * 1.0e-14", core)
        self.assertNotIn("directed_segment_sos_direction_is_preferred(segment, query_map_id) ? 0u : 1u", core)
        self.assertIn("RayjoinCdbGroupMode::BlockMerge64", workloads)
        self.assertIn("rayjoin_cdb_duplicate_key_for_segment", workloads)
        self.assertIn("canonical_segment_ids[segment_index] = canonical_id;", workloads)
        self.assertIn("canonical_face_ids[segment_index] = canonical_face_id;", workloads)
        self.assertIn("RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER", workloads)
        self.assertIn("optixReportIntersection(accepted_t, 0u)", core)
        self.assertIn("static constexpr size_t kSegmentsPerRange = 8", workloads)
        self.assertIn("RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE", workloads)
        self.assertIn("RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_SIZE", workloads)
        self.assertIn("RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE", workloads)
        self.assertIn("lp.ranges = reinterpret_cast<const GpuRayjoinCdbSegmentRange*>", workloads)
        self.assertIn('"__intersection__rayjoin_cdb_point_location",\n            nullptr,\n            "__closesthit__rayjoin_cdb_point_location",\n            4).release();', workloads)
        self.assertIn("class PreparedOptixRayjoinCdbPointLocation2D", runtime)
        self.assertIn("PreparedOptixDirectedSegmentPointLocation2D", runtime)
        self.assertIn("prepare_directed_segment_point_location_2d_optix", runtime)
        self.assertIn("write_segment_ids_device_points", runtime)
        self.assertIn("write_face_ids_device_points", runtime)
        self.assertIn("face_ids_device_points", runtime)
        self.assertIn("def prepare_rayjoin_cdb_point_location_2d_optix", runtime)
        self.assertIn("OPTIX_DIRECTED_SEGMENT_POINT_LOCATION_COUNT_SYMBOL", runtime)
        self.assertIn("OPTIX_DIRECTED_SEGMENT_POINT_LOCATION_WRITE_DEVICE_SEGMENT_IDS_SYMBOL", runtime)
        self.assertIn("OPTIX_DIRECTED_SEGMENT_POINT_LOCATION_WRITE_DEVICE_FACE_IDS_SYMBOL", runtime)
        self.assertIn("OPTIX_RAYJOIN_CDB_POINT_LOCATION_COUNT_SYMBOL", runtime)
        self.assertIn("OPTIX_RAYJOIN_CDB_POINT_LOCATION_WRITE_DEVICE_FACE_IDS_SYMBOL", runtime)

    def test_embree_route_uses_prepared_bvh_intersect_not_bruteforce(self) -> None:
        prelude = (ROOT / "src" / "native" / "embree" / "rtdl_embree_prelude.h").read_text(encoding="utf-8")
        scene = (ROOT / "src" / "native" / "embree" / "rtdl_embree_scene.cpp").read_text(encoding="utf-8")
        api = (ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp").read_text(encoding="utf-8")
        runtime = (ROOT / "src" / "rtdsl" / "embree_runtime.py").read_text(encoding="utf-8")
        self.assertIn("RtdlRayjoinCdbSegment", prelude)
        self.assertIn("RtdlRayjoinCdbPointLocationRow", prelude)
        self.assertIn("RtdlDirectedSegmentFace2D", prelude)
        self.assertIn("RtdlDirectedSegmentPointLocationRow2D", prelude)
        self.assertIn("rtdl_embree_prepare_directed_segment_point_location_2d", prelude)
        self.assertIn("rtdl_embree_prepare_rayjoin_cdb_point_location_2d", prelude)
        self.assertIn("kRayjoinCdbPointLocation", scene)
        self.assertIn("rayjoin_cdb_point_location_intersect", scene)
        self.assertIn("double* best_slope", scene)
        self.assertIn("constexpr double eps = 1.0e-7;", scene)
        self.assertIn("static_cast<double>(static_cast<float>(point.p.x))", scene)
        self.assertIn("current_slope_gt = slope > best_slope", scene)
        self.assertIn("state->query_map_id == 0u ? !current_slope_gt : current_slope_gt", scene)
        self.assertIn("kRayjoinCdbBoundsPad", scene)
        self.assertIn("static_cast<float>(min_x) - kRayjoinCdbBoundsPad", scene)
        self.assertIn("std::nextafter(static_cast<float>(hit_t)", scene)
        self.assertIn("rayhit->ray.tfar = next_t", scene)
        self.assertIn("rtcSetGeometryIntersectFunction(holder.geometry, rayjoin_cdb_point_location_intersect)", api)
        self.assertIn("run_query_ranges<RtdlRayjoinCdbPointLocationRow>", api)
        self.assertIn("class PreparedEmbreeRayjoinCdbPointLocation2D", runtime)
        self.assertIn("PreparedEmbreeDirectedSegmentPointLocation2D", runtime)
        self.assertIn("prepare_directed_segment_point_location_2d_embree", runtime)
        self.assertIn("def prepare_rayjoin_cdb_point_location_2d_embree", runtime)
        self.assertIn("EMBREE_DIRECTED_SEGMENT_POINT_LOCATION_COUNT_SYMBOL", runtime)
        self.assertIn("EMBREE_RAYJOIN_CDB_POINT_LOCATION_COUNT_SYMBOL", runtime)

    def test_public_exports_include_rayjoin_cdb_route(self) -> None:
        init = (ROOT / "src" / "rtdsl" / "__init__.py").read_text(encoding="utf-8")
        for name in (
            "chains_to_rayjoin_cdb_segments",
            "pack_rayjoin_cdb_segments",
            "pack_directed_segment_faces",
            "prepare_directed_segment_point_location_2d_optix",
            "prepare_directed_segment_point_location_2d_embree",
            "prepare_rayjoin_cdb_point_location_2d_optix",
            "prepare_rayjoin_cdb_point_location_2d_embree",
        ):
            self.assertIn(name, init)


if __name__ == "__main__":
    unittest.main()
