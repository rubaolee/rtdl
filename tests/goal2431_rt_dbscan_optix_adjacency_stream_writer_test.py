from __future__ import annotations

import json
import pathlib
import statistics
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
OPTIX_CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPEAT = ROOT / "scripts" / "goal2403_rt_dbscan_repeat_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal2431_rt_dbscan_optix_adjacency_stream_writer_2026-05-19.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2431_rt_dbscan_optix_adjacency_stream_pod"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal2431RtDbscanOptixAdjacencyStreamWriterTest(unittest.TestCase):
    def test_native_symbol_is_generic_and_bound_to_python(self) -> None:
        core = OPTIX_CORE.read_text(encoding="utf-8")
        api = OPTIX_API.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")

        symbol = "rtdl_optix_write_prepared_fixed_radius_adjacency_3d_device_outputs"
        self.assertIn("kFixedRadiusAdjacency3DRtKernelSrc", core)
        self.assertIn("__anyhit__frn3d_adjacency_anyhit", core)
        self.assertIn("edge_offsets", core)
        self.assertIn("neighbor_indices_out", core)
        self.assertIn(symbol, api)
        self.assertIn(symbol, prelude)
        self.assertIn("_OPTIX_PREPARED_FIXED_RADIUS_ADJACENCY_3D_DEVICE_OUTPUT_SYMBOL", runtime)
        self.assertIn("write_device_adjacency_columns", runtime)
        self.assertIn("generic_fixed_radius_adjacency_3d_device_columns", runtime)

        touched_native = "\n".join((core, api, prelude)).lower()
        self.assertNotIn("rtdl_optix_dbscan", touched_native)
        self.assertNotIn("dbscan_adjacency", touched_native)

    def test_partner_adapter_and_app_mode_are_wired(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        repeat = REPEAT.read_text(encoding="utf-8")

        self.assertIn("PreparedOptixCupyRadiusGraphAdjacency3D", adapters)
        self.assertIn("prepare_optix_cupy_radius_graph_adjacency_3d", adapters)
        self.assertIn("radius_graph_components_3d_optix_cupy_prepared_adjacency_partner_columns", adapters)
        self.assertIn("exact_full_degree_from_prepared_rt_count_threshold", adapters)
        self.assertIn("generic_prepared_optix_cupy_directed_radius_graph_adjacency_component_labels_3d", adapters)
        self.assertIn("PreparedOptixCupyRadiusGraphAdjacency3D", init_text)
        self.assertIn("prepare_optix_cupy_radius_graph_adjacency_3d", init_text)
        self.assertIn("optix_rt_core_adjacency_cupy_components_3d", app)
        self.assertIn("optix_rt_core_adjacency_cupy_components_3d", readme)
        self.assertIn("PREPARED_OPTIX_ADJACENCY_MODE", repeat)

    def test_pod_artifacts_validate_correctness_and_boundary(self) -> None:
        tiny = json.loads((ARTIFACT_DIR / "tiny_app.json").read_text(encoding="utf-8"))
        self.assertTrue(tiny["matches_reference"])
        self.assertTrue(tiny["claim_boundary"]["rt_core_accelerated"])
        self.assertFalse(tiny["claim_boundary"]["native_dbscan_abi_added"])
        self.assertEqual(
            tiny["metadata"]["native_adjacency_metadata"]["native_symbol"],
            "rtdl_optix_write_prepared_fixed_radius_adjacency_3d_device_outputs",
        )
        self.assertEqual(
            tiny["metadata"]["native_engine_row_contract"],
            "generic_prepared_fixed_radius_adjacency_3d_device_columns",
        )

        for artifact_name in (
            "clustered4096_repeat.json",
            "clustered8192_repeat.json",
            "road8192_repeat.json",
        ):
            with self.subTest(artifact=artifact_name):
                payload = json.loads((ARTIFACT_DIR / artifact_name).read_text(encoding="utf-8"))
                self.assertTrue(payload["signatures_match"])
                optix_rows = [
                    row for row in payload["rows"]
                    if row["mode"] == "optix_rt_core_adjacency_cupy_components_3d"
                ]
                cupy_rows = [
                    row for row in payload["rows"]
                    if row["mode"] == "partner_cupy_prepared_adjacency_components_3d"
                ]
                self.assertGreaterEqual(len(optix_rows), 3)
                self.assertEqual(len(optix_rows), len(cupy_rows))
                self.assertTrue(all(row["rt_core_accelerated"] for row in optix_rows))
                self.assertGreater(int(optix_rows[0]["directed_edge_count"]), 0)
                optix_tail = statistics.median(float(row["outer_elapsed_sec"]) for row in optix_rows[1:])
                cupy_tail = statistics.median(float(row["outer_elapsed_sec"]) for row in cupy_rows[1:])
                self.assertLessEqual(optix_tail / cupy_tail, 1.05)

    def test_report_and_todo_keep_claims_bounded(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        todo = TODO.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("not yet the final", report)
        self.assertIn("performance leap", report)
        self.assertIn("No DBSCAN-native ABI was added", report)
        self.assertIn("not a broad speedup claim", report)
        self.assertIn("bounded/chunked", report)
        self.assertIn("Goal2431 added the generic prepared OptiX fixed-radius adjacency writer", todo)
        self.assertIn("DBSCAN-native", todo)
        self.assertIn("engine code", todo)


if __name__ == "__main__":
    unittest.main()
