from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "current" / "research_benchmarks" / "triangle_counting" / "rtdl_triangle_counting_benchmark_app.py"
EMBREE_RUNTIME = ROOT / "src" / "rtdsl" / "embree_runtime.py"
EMBREE_API = ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp"
EMBREE_PRELUDE = ROOT / "src" / "native" / "embree" / "rtdl_embree_prelude.h"


class Goal4350EmbreeTriangleWeightedSumParityTest(unittest.TestCase):
    def test_embree_exports_prepared_ray_any_hit_weighted_sum(self) -> None:
        symbol = "rtdl_embree_static_triangle_scene_3d_ray_any_hit_weighted_sum"
        self.assertIn(symbol, EMBREE_PRELUDE.read_text(encoding="utf-8"))
        self.assertIn(symbol, EMBREE_API.read_text(encoding="utf-8"))
        runtime = EMBREE_RUNTIME.read_text(encoding="utf-8")
        self.assertIn(symbol, runtime)
        self.assertIn("def ray_any_hit_weighted_sum(self, rays, ray_weights)", runtime)
        self.assertIn('"rows_materialized": False', runtime)

    def test_triangle_counting_embree_summary_uses_native_weighted_sum(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn('normalized_backend == "embree" and detail == "summary"', source)
        self.assertIn("rt.prepare_embree_static_triangle_scene_3d(triangles)", source)
        self.assertIn("summary_result = scene.ray_any_hit_weighted_sum(rays, ray_weights)", source)
        self.assertIn(
            '"generic_prepared_triangle_scene_3d_any_hit_weighted_sum_embree"',
            source,
        )


if __name__ == "__main__":
    unittest.main()
