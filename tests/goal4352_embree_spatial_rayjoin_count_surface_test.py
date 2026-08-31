from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "rtdl_human_scale_rt_vs_embree_comparison.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
EMBREE_RUNTIME = ROOT / "src" / "rtdsl" / "embree_runtime.py"
EMBREE_API = ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp"
EMBREE_PRELUDE = ROOT / "src" / "native" / "embree" / "rtdl_embree_prelude.h"


class Goal4352EmbreeSpatialRayjoinCountSurfaceTest(unittest.TestCase):
    def test_embree_exports_lsi_and_pip_count_only_symbols(self) -> None:
        prelude = EMBREE_PRELUDE.read_text(encoding="utf-8")
        api = EMBREE_API.read_text(encoding="utf-8")
        runtime = EMBREE_RUNTIME.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")

        for symbol in (
            "rtdl_embree_count_segment_pair_intersections",
            "rtdl_embree_count_point_primitive_anyhit_packet",
            "rtdl_embree_segment_pair_intersections_2d_create",
            "rtdl_embree_segment_pair_intersections_2d_count",
            "rtdl_embree_segment_pair_intersections_2d_destroy",
            "rtdl_embree_point_primitive_anyhit_2d_create",
            "rtdl_embree_point_primitive_anyhit_2d_count",
            "rtdl_embree_point_primitive_anyhit_2d_destroy",
        ):
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)
            self.assertIn(symbol, runtime)

        self.assertIn("def run_embree_count(kernel_fn_or_compiled, **inputs) -> int:", runtime)
        self.assertIn("def count(self, *, require_prepared: bool = False) -> int:", runtime)
        self.assertIn("return _count_lsi_embree_packed", runtime)
        self.assertIn("return _count_pip_embree_packed", runtime)
        self.assertIn("class _PreparedEmbreeSegmentPairCountHandle:", runtime)
        self.assertIn("class _PreparedEmbreePointPrimitiveCountHandle:", runtime)
        self.assertIn("from .embree_runtime import run_embree_count", init)
        self.assertIn('"run_embree_count"', init)
        self.assertIn("RTDL_EMBREE_EXPORT int rtdl_embree_point_primitive_anyhit_2d_count", api)
        self.assertIn("run_query_index_ranges_with_worker(point_values.size()", api)
        self.assertIn("geos_workers", api)
        self.assertIn("total_count.fetch_add(local_count, std::memory_order_relaxed)", api)

    def test_prepared_lsi_count_does_not_bruteforce_zero_hit_queries(self) -> None:
        api = EMBREE_API.read_text(encoding="utf-8")
        start = api.index("RTDL_EMBREE_EXPORT int rtdl_embree_segment_pair_intersections_2d_count")
        end = api.index("RTDL_EMBREE_EXPORT void rtdl_embree_segment_pair_intersections_2d_destroy", start)
        body = api[start:end]

        self.assertIn("append_shared_endpoint_segment_hits", body)
        self.assertIn("Do not fall back to scanning every", body)
        self.assertNotIn("for (size_t right_index = 0; right_index < impl->right_segments.size(); ++right_index)", body)

    def test_human_scale_rayjoin_embree_probe_uses_native_count_surface(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("with rt.prepare_embree(kernel).bind(**case.inputs) as prepared:", source)
        self.assertIn("row_count = prepared.count(require_prepared=True)", source)
        self.assertNotIn("result = rt.run_embree(kernel, **case.inputs)", source)
        self.assertNotIn('"row_count": len(result)', source)
        self.assertIn('"output_contract": "native_embree_prepared_scalar_count_no_row_materialization"', source)
        self.assertIn('"prepared_count_required": True', source)
        self.assertIn('payload.get("output_contract") == "generic_row_count_raw_view_no_python_dicts"', source)
        self.assertIn('payload.get("output_contract") == "native_embree_scalar_count_no_row_materialization"', source)


if __name__ == "__main__":
    unittest.main()
