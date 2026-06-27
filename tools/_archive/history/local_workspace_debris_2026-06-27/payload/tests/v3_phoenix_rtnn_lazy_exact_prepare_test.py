import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class V3PhoenixRtnnLazyExactPrepareTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workloads = WORKLOADS.read_text(encoding="utf-8")

    def _function_body(self, signature: str, next_signature: str) -> str:
        start = self.workloads.index(signature)
        end = self.workloads.index(next_signature, start + len(signature))
        return self.workloads[start:end]

    def test_prepared_constructor_does_not_eagerly_upload_exact_search_buffer(self) -> None:
        constructor = self._function_body(
            "PreparedFixedRadiusNeighborsGrid3D(",
            "uint32_t exact_cell_for",
        )

        self.assertNotIn("sorted_search_exact", constructor)
        self.assertNotIn("d_search_exact = std::make_unique", constructor)
        self.assertNotIn("upload(d_search_exact->ptr", constructor)
        self.assertIn("upload(d_search->ptr", constructor)

    def test_lazy_exact_materialization_is_timed(self) -> None:
        self.assertIn("void ensure_exact_search_device()", self.workloads)
        self.assertIn(
            "static void ensure_exact_search_device_with_timing",
            self.workloads,
        )

        helper = self._function_body(
            "static void ensure_exact_search_device_with_timing",
            "static size_t count_prepared_fixed_radius_neighbors_grid_3d_optix",
        )
        self.assertIn("prepared->ensure_exact_search_device();", helper)
        self.assertIn("g_optix_last_fixed_radius_3d_prepare_s", helper)
        self.assertIn("seconds_between(t_start_exact_prepare, t_end_exact_prepare)", helper)

    def test_exact_routes_materialize_exact_buffer_before_kernel_args(self) -> None:
        exact_route_bounds = [
            (
                "static size_t count_prepared_fixed_radius_neighbors_grid_3d_optix",
                "static RtdlFixedRadiusNeighborSummary summarize_prepared_fixed_radius_neighbors_grid_3d_optix",
            ),
            (
                "static RtdlFixedRadiusNeighborSummary summarize_prepared_fixed_radius_neighbors_grid_3d_optix",
                "static void run_prepared_exact_fixed_radius_neighbors_grid_3d_optix",
            ),
            (
                "static void run_prepared_exact_fixed_radius_neighbors_grid_3d_optix",
                "static void run_prepared_ranked_fixed_radius_neighbors_grid_3d_optix",
            ),
            (
                "static void run_prepared_ranked_fixed_radius_neighbors_grid_3d_optix",
                "static void run_prepared_ranked_fixed_radius_neighbor_summaries_grid_3d_optix",
            ),
            (
                "static void run_prepared_ranked_fixed_radius_neighbor_summaries_grid_3d_optix",
                "static RtdlFixedRadiusRankedNeighborAggregate aggregate_prepared_ranked_fixed_radius_neighbor_summaries_grid_3d_optix",
            ),
        ]

        for start, end in exact_route_bounds:
            with self.subTest(route=start):
                body = self._function_body(start, end)
                ensure_index = body.index("ensure_exact_search_device_with_timing(prepared);")
                first_exact_use = body.index("&prepared->d_search_exact->ptr")
                self.assertLess(ensure_index, first_exact_use)

    def test_double_precision_aggregate_branch_keeps_lazy_exact_out_of_float32_paths(self) -> None:
        body = self._function_body(
            "static RtdlFixedRadiusRankedNeighborAggregate aggregate_prepared_ranked_fixed_radius_neighbor_summaries_grid_3d_optix",
            "static RtdlFixedRadiusRankedNeighborAggregate aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_optix",
        )

        self.assertIn("} else {\n        ensure_exact_search_device_with_timing(prepared);", body)
        direct_f32 = body.index("if (use_direct_float32_aggregate)")
        f32 = body.index("} else if (use_float32_precision)")
        exact = body.index("} else {\n        ensure_exact_search_device_with_timing(prepared);")
        self.assertLess(direct_f32, f32)
        self.assertLess(f32, exact)


if __name__ == "__main__":
    unittest.main()
