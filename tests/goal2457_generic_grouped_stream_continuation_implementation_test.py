from __future__ import annotations

import pathlib
import json
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
POD_SUMMARY = ROOT / "docs" / "reports" / "goal2457_grouped_stream_pod" / "summary.json"
TINY_FINAL = ROOT / "docs" / "reports" / "goal2457_grouped_stream_pod" / "tiny_final.json"
PLANNED_65536_FINAL = ROOT / "docs" / "reports" / "goal2457_grouped_stream_pod" / "planned_65536_final.json"


class Goal2457GenericGroupedStreamContinuationImplementationTest(unittest.TestCase):
    def test_native_abi_is_generic_and_app_agnostic(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        combined = "\n".join((core, api, prelude, workloads))

        self.assertIn("kFixedRadiusGroupedUnion3DRtKernelSrc", core)
        self.assertIn("rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs", combined)
        self.assertIn("predicate_flags", combined)
        self.assertIn("fallback_candidate_out", combined)
        self.assertIn("workspaces must cover every prepared search item", combined)
        self.assertIn("prepared_rt_core_grouped_union_3d", OPTIX_RUNTIME.read_text(encoding="utf-8"))
        self.assertNotIn("rtdl_optix_dbscan", combined.lower())

    def test_python_partner_surface_is_first_class_and_visible(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")

        self.assertIn("apply_device_grouped_union", runtime)
        self.assertIn("grouped-union workspaces must cover every prepared search item", runtime)
        self.assertIn("PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D", adapters)
        self.assertIn("generic_prepared_optix_cupy_grouped_stream_component_labels_3d", adapters)
        self.assertIn("materializes_directed_adjacency_stream\": False", adapters)
        self.assertIn("prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d", init_text)
        self.assertIn("radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns", init_text)
        self.assertIn("optix_rt_core_grouped_stream_cupy_components_3d", app)

    def test_boundary_flags_block_release_and_hidden_dispatch_claims(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")

        self.assertIn("\"automatic_hidden_dispatcher\": False", adapters)
        self.assertIn("\"rt_core_speedup_claim_authorized\": False", adapters)
        self.assertIn("\"whole_app_speedup_claim_authorized\": False", adapters)
        self.assertIn("\"v2_0_release_authorized\": False", adapters)
        self.assertIn("\"materializes_bounded_directed_adjacency_chunks\": False", app)

    def test_pod_evidence_supports_planner_boundary(self) -> None:
        summary = json.loads(POD_SUMMARY.read_text(encoding="utf-8"))
        by_count = {int(row["point_count"]): row for row in summary["summaries"]}

        row_32768 = by_count[32768]
        row_65536 = by_count[65536]
        self.assertTrue(row_32768["signatures_match"])
        self.assertTrue(row_65536["signatures_match"])

        timings_32768 = {
            result["mode"]: float(result["tail_median_sec"])
            for result in row_32768["results"]
            if result.get("tail_median_sec") is not None
        }
        timings_65536 = {
            result["mode"]: float(result["tail_median_sec"])
            for result in row_65536["results"]
            if result.get("tail_median_sec") is not None
        }

        self.assertLess(timings_32768["full_adjacency"], timings_32768["grouped_stream"])
        self.assertLess(timings_32768["grouped_stream"], timings_32768["chunked_adjacency"])
        self.assertLess(timings_65536["grouped_stream"], timings_65536["chunked_adjacency"])

    def test_planned_mode_selects_grouped_stream_when_full_stream_exceeds_budget(self) -> None:
        payload = json.loads(PLANNED_65536_FINAL.read_text(encoding="utf-8"))
        plan = payload["metadata"]["execution_plan"]

        self.assertEqual(payload["mode"], "planned_rt_dbscan_continuation")
        self.assertEqual(payload["selected_mode"], "optix_rt_core_grouped_stream_cupy_components_3d")
        self.assertEqual(plan["selected_mode"], "optix_rt_core_grouped_stream_cupy_components_3d")
        self.assertFalse(plan["full_stream_fits_budget"])
        self.assertEqual(payload["metadata"]["native_execution_path"], "prepared_rt_core_grouped_union_3d")
        self.assertFalse(payload["metadata"]["materializes_directed_adjacency_stream"])

    def test_final_pod_smoke_preserves_tiny_correctness(self) -> None:
        payload = json.loads(TINY_FINAL.read_text(encoding="utf-8"))

        self.assertEqual(payload["mode"], "optix_rt_core_grouped_stream_cupy_components_3d")
        self.assertTrue(payload["matches_reference"])
        self.assertEqual(payload["metadata"]["native_execution_path"], "prepared_rt_core_grouped_union_3d")


if __name__ == "__main__":
    unittest.main()
