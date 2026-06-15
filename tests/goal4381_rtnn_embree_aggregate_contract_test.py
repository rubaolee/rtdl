from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal4381RtnnEmbreeAggregateContractTest(unittest.TestCase):
    def test_embree_native_aggregate_symbol_is_exposed(self) -> None:
        prelude = (ROOT / "src" / "native" / "embree" / "rtdl_embree_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp").read_text(encoding="utf-8")
        runtime = (ROOT / "src" / "rtdsl" / "embree_runtime.py").read_text(encoding="utf-8")

        symbol = "rtdl_embree_fixed_radius_neighbors_3d_ranked_summary_aggregate_run"
        self.assertIn("struct RtdlFixedRadiusRankedNeighborAggregate", prelude)
        self.assertIn(symbol, prelude)
        self.assertIn(f"RTDL_EMBREE_EXPORT int {symbol}", api)
        self.assertIn("def aggregate_ranked_summary(self, query_points", runtime)
        self.assertIn(symbol, runtime)

    def test_rtnn_runner_allows_fair_embree_aggregate_mode(self) -> None:
        runner = (ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py").read_text(encoding="utf-8")

        self.assertIn('embree_supported_modes = {"ranked-summary-raw", "ranked-summary-aggregate"}', runner)
        self.assertIn('prepared.aggregate_ranked_summary(batch, radius=radius, k_max=k_max)', runner)
        self.assertIn('"embree_ranked_summary_aggregate"', runner)
        self.assertIn('"materializes_summary_rows": result_mode == "ranked-summary-raw"', runner)
        self.assertNotIn("Embree batched RTNN path currently supports result_mode='ranked-summary-raw')", runner)


if __name__ == "__main__":
    unittest.main()
