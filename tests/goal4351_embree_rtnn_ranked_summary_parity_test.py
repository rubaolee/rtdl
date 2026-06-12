from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
EMBREE_RUNTIME = ROOT / "src" / "rtdsl" / "embree_runtime.py"
EMBREE_API = ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp"
EMBREE_PRELUDE = ROOT / "src" / "native" / "embree" / "rtdl_embree_prelude.h"


class Goal4351EmbreeRtnnRankedSummaryParityTest(unittest.TestCase):
    def test_embree_exports_prepared_3d_ranked_summary_surface(self) -> None:
        prelude = EMBREE_PRELUDE.read_text(encoding="utf-8")
        api = EMBREE_API.read_text(encoding="utf-8")
        runtime = EMBREE_RUNTIME.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")

        for symbol in (
            "RtdlFixedRadiusRankedNeighborSummary",
            "rtdl_embree_fixed_radius_neighbors_3d_create",
            "rtdl_embree_fixed_radius_neighbors_3d_ranked_summary_run",
            "rtdl_embree_fixed_radius_neighbors_3d_destroy",
        ):
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)
            self.assertIn(symbol, runtime)

        self.assertIn("class PreparedEmbreeFixedRadiusNeighbors3D", runtime)
        self.assertIn("def run_ranked_summary_raw(self, query_points", runtime)
        self.assertIn("prepare_embree_fixed_radius_neighbors_3d", init)

    def test_rtnn_embree_batched_path_uses_native_prepared_summary_rows(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("prepared = rt.prepare_embree_fixed_radius_neighbors_3d(search)", source)
        self.assertIn("rows = prepared.run_ranked_summary_raw(batch, radius=radius, k_max=k_max)", source)
        self.assertIn('"mode": "embree_prepared_fixed_radius_ranked_summary_rows"', source)
        self.assertIn('"materializes_neighbor_rows": False', source)
        self.assertIn('"prepared_search_structure": backend in {"optix", "embree"}', source)
        self.assertNotIn("embree_fixed_radius_rows_to_ranked_summary_rows", source)

    def test_human_scale_packet_rejects_stale_rtnn_embree_artifacts(self) -> None:
        source = (ROOT / "scripts" / "rtdl_human_scale_rt_vs_embree_comparison.py").read_text(encoding="utf-8")
        self.assertIn("def _artifact_matches_current_spec(spec: RunSpec, payload: dict[str, Any]) -> bool:", source)
        self.assertIn('if spec.app == "rtnn" and spec.backend == "embree":', source)
        self.assertIn('claim.get("materializes_neighbor_rows")', source)
        self.assertIn('phase.get("mode") == "embree_fixed_radius_rows_to_ranked_summary_rows"', source)


if __name__ == "__main__":
    unittest.main()
