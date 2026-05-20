from __future__ import annotations

import pathlib
import json
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
OLD_SUMMARY = ROOT / "docs" / "reports" / "goal2457_grouped_stream_pod" / "summary.json"
NEW_SUMMARY = ROOT / "docs" / "reports" / "goal2459_grouped_stream_threshold_capped_pod" / "summary.json"


class Goal2459GroupedStreamThresholdCappedCoreFlagsTest(unittest.TestCase):
    def test_grouped_stream_uses_threshold_capped_core_flags(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        start = adapters.index("class PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D")
        end = adapters.index("def prepare_optix_cupy_radius_graph_components_3d", start)
        grouped_stream_class = adapters[start:end]

        self.assertNotIn("threshold=self.point_count", grouped_stream_class)
        self.assertIn("threshold=min_neighbors", grouped_stream_class)
        self.assertIn("core_flag_cache_reused", grouped_stream_class)
        self.assertIn("threshold_capped_at_min_neighbors_not_exact_full_degree", grouped_stream_class)
        self.assertIn("self._cached_core_threshold == min_neighbors", grouped_stream_class)

    def test_app_metadata_reports_threshold_capped_counts(self) -> None:
        app = APP.read_text(encoding="utf-8")
        start = app.index('elif mode == "optix_rt_core_grouped_stream_cupy_components_3d"')
        end = app.index('elif mode == "optix_rt_core_flags_cupy_microcell_graph_components_3d"', start)
        grouped_mode = app[start:end]

        self.assertIn("optix_rt_core_grouped_stream_cupy_components_3d", grouped_mode)
        self.assertIn("threshold_capped_at_min_neighbors_not_exact_full_degree", grouped_mode)
        self.assertNotIn("exact_full_degree_from_prepared_rt_count_threshold_with_threshold_equal_point_count", grouped_mode)

    def test_pod_evidence_cuts_count_threshold_work(self) -> None:
        old = json.loads(OLD_SUMMARY.read_text(encoding="utf-8"))
        new = json.loads(NEW_SUMMARY.read_text(encoding="utf-8"))

        old_count_native = {}
        for row in old["summaries"]:
            for result in row["results"]:
                if result["mode"] == "grouped_stream":
                    metadata = result["rows"][0]["metadata"]["count_metadata"]
                    old_count_native[int(row["point_count"])] = float(
                        metadata["native_metadata"]["native_elapsed_sec"]
                    )

        for row in new["summaries"]:
            point_count = int(row["point_count"])
            first = row["repeat_rows"][0]
            self.assertTrue(row["signatures_match"])
            self.assertEqual(first["count_threshold"], 12)
            self.assertLess(float(first["count_native_elapsed_sec"]), old_count_native[point_count])

        self.assertTrue(new["tiny_smoke"]["matches_reference"])
        self.assertEqual(
            new["planned_65536"]["selected_mode"],
            "optix_rt_core_grouped_stream_cupy_components_3d",
        )


if __name__ == "__main__":
    unittest.main()
