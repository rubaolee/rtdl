from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

import rtdsl as rt
from rtdsl import embree_runtime
from rtdsl import optix_runtime

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
        self.assertIn('timing_mode = "embree_prepared_fixed_radius_ranked_summary_rows"', source)
        self.assertIn('"mode": timing_mode', source)
        self.assertIn('"materializes_neighbor_rows": False', source)
        self.assertIn('"prepared_search_structure": backend in {"optix", "embree"}', source)
        self.assertNotIn("embree_fixed_radius_rows_to_ranked_summary_rows", source)

    def test_human_scale_packet_rejects_stale_rtnn_embree_artifacts(self) -> None:
        source = (ROOT / "scripts" / "rtdl_human_scale_rt_vs_embree_comparison.py").read_text(encoding="utf-8")
        self.assertIn("def _artifact_matches_current_spec(spec: RunSpec, payload: dict[str, Any]) -> bool:", source)
        self.assertIn('if spec.app == "rtnn" and spec.backend == "embree":', source)
        self.assertIn('claim.get("materializes_neighbor_rows")', source)
        self.assertIn('phase.get("mode") == "embree_fixed_radius_rows_to_ranked_summary_rows"', source)

    def test_embree_prepared_ranked_summary_handle_caches_hot_symbols(self) -> None:
        lookup_counts: dict[str, int] = {}
        calls: list[str] = []

        def create_symbol(_records, _count, handle_out, _error, _error_size):
            calls.append("create")
            handle_out._obj.value = 123
            return 0

        def run_symbol(_handle, _records, _count, _radius, _k_max, _rows_out, row_count_out, traversal_out, _error, _error_size):
            calls.append("run")
            row_count_out._obj.value = 0
            traversal_out._obj.value = 0.0
            return 0

        def destroy_symbol(_handle):
            calls.append("destroy")
            return 0

        symbols = {
            "rtdl_embree_fixed_radius_neighbors_3d_create": create_symbol,
            "rtdl_embree_fixed_radius_neighbors_3d_ranked_summary_run": run_symbol,
            "rtdl_embree_fixed_radius_neighbors_3d_destroy": destroy_symbol,
        }

        def fake_symbol(_library, symbol_name: str):
            lookup_counts[symbol_name] = lookup_counts.get(symbol_name, 0) + 1
            return symbols.get(symbol_name)

        points = (
            {"id": 1, "x": 0.0, "y": 0.0, "z": 0.0},
            {"id": 2, "x": 1.0, "y": 0.0, "z": 0.0},
        )
        library = SimpleNamespace(rtdl_embree_free_rows=lambda _rows: None)
        with (
            mock.patch.object(embree_runtime, "_load_configured_embree_library", return_value=library),
            mock.patch.object(embree_runtime, "_require_optional_embree_symbol", side_effect=fake_symbol),
        ):
            with rt.prepare_embree_fixed_radius_neighbors_3d(points) as prepared:
                first = prepared.run_ranked_summary_raw(points, radius=0.5, k_max=4)
                second = prepared.run_ranked_summary_raw(points, radius=0.5, k_max=4)
                first.close()
                second.close()

        self.assertEqual(
            lookup_counts,
            {
                "rtdl_embree_fixed_radius_neighbors_3d_create": 1,
                "rtdl_embree_fixed_radius_neighbors_3d_ranked_summary_run": 1,
                "rtdl_embree_fixed_radius_neighbors_3d_destroy": 1,
            },
        )
        self.assertEqual(calls, ["create", "run", "run", "destroy"])

    def test_optix_prepared_ranked_summary_handle_caches_hot_symbols(self) -> None:
        lookup_counts: dict[str, int] = {}
        calls: list[str] = []

        def prepare_symbol(_records, _count, _max_radius, handle_out, _error, _error_size):
            calls.append("prepare")
            handle_out._obj.value = 456
            return 0

        def run_symbol(_handle, _records, _count, _radius, _k_max, _rows_out, row_count_out, _error, _error_size):
            calls.append("run")
            row_count_out._obj.value = 0
            return 0

        def destroy_symbol(_handle):
            calls.append("destroy")
            return 0

        symbols = {
            "rtdl_optix_prepare_fixed_radius_neighbors_3d": prepare_symbol,
            "rtdl_optix_run_prepared_ranked_fixed_radius_neighbor_summaries_3d": run_symbol,
            "rtdl_optix_destroy_prepared_fixed_radius_neighbors_3d": destroy_symbol,
        }
        library = SimpleNamespace(rtdl_optix_free_rows=lambda _rows: None)

        def fake_symbol(_library, symbol_name: str):
            lookup_counts[symbol_name] = lookup_counts.get(symbol_name, 0) + 1
            return symbols.get(symbol_name)

        points = (
            {"id": 1, "x": 0.0, "y": 0.0, "z": 0.0},
            {"id": 2, "x": 1.0, "y": 0.0, "z": 0.0},
        )
        with (
            mock.patch.object(optix_runtime, "_load_optix_library", return_value=library),
            mock.patch.object(optix_runtime, "_find_optional_backend_symbol", side_effect=fake_symbol),
        ):
            with rt.prepare_optix_fixed_radius_neighbors_3d(points, max_radius=1.0) as prepared:
                first = prepared.run_ranked_summary_raw(points, radius=0.5, k_max=4)
                second = prepared.run_ranked_summary_raw(points, radius=0.5, k_max=4)
                first.close()
                second.close()

        self.assertEqual(
            lookup_counts,
            {
                "rtdl_optix_prepare_fixed_radius_neighbors_3d": 1,
                "rtdl_optix_run_prepared_ranked_fixed_radius_neighbor_summaries_3d": 1,
                "rtdl_optix_destroy_prepared_fixed_radius_neighbors_3d": 1,
            },
        )
        self.assertEqual(calls, ["prepare", "run", "run", "destroy"])


if __name__ == "__main__":
    unittest.main()
