from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
OPTIX_CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
BASELINE_SUMMARY = ROOT / "docs" / "reports" / "goal2463_grouped_union_baseline_pod" / "summary.json"
ALL_ITEMS_SUMMARY = ROOT / "docs" / "reports" / "goal2463_grouped_union_all_items_pod" / "summary.json"


class Goal2463GroupedUnionAllItemsPathTest(unittest.TestCase):
    def test_native_grouped_union_has_generic_all_items_mode(self) -> None:
        core = OPTIX_CORE.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("uint32_t all_predicate", core)
        self.assertIn("params.all_predicate != 0u", core)
        self.assertIn("target > source", core)
        self.assertIn("union_grouped_min_root(params.parent_out", core)
        self.assertIn("lp.all_predicate = (predicate_flags == nullptr) ? 1u : 0u", workloads)
        self.assertIn("predicate and fallback pointers must both be null only for all-items mode", workloads)
        native_slice = core[core.index("kFixedRadiusGroupedUnion3DRtKernelSrc"):core.index(")CUDA\";", core.index("kFixedRadiusGroupedUnion3DRtKernelSrc"))]
        self.assertNotIn("dbscan", native_slice.lower())

    def test_python_runtime_exposes_all_items_self_path_without_new_app_abi(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")

        self.assertIn("def apply_device_grouped_union_all_self(", runtime)
        self.assertIn("all_items_true_no_fallback_candidates", runtime)
        self.assertIn("generic_prepared_fixed_radius_grouped_union_3d_all_items_self_device_parent_workspace", runtime)
        self.assertIn("prepared_rt_core_grouped_union_3d_all_items_self_query", runtime)
        self.assertIn("ctypes.c_void_p(0)", runtime)
        self.assertIn("_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_SYMBOL", runtime)

    def test_grouped_stream_adapter_uses_all_items_mode_only_when_predicate_is_uniform_true(self) -> None:
        adapters = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        start = adapters.index("class PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D")
        end = adapters.index("def prepare_optix_cupy_radius_graph_components_3d", start)
        grouped_stream_class = adapters[start:end]

        self.assertIn("self._cached_all_core_flags_true", grouped_stream_class)
        self.assertIn("self.cupy.all(self._cached_core_flags).item()", grouped_stream_class)
        self.assertIn("if all_core_flags_true:", grouped_stream_class)
        self.assertIn("apply_device_grouped_union_all_self", grouped_stream_class)
        self.assertIn("apply_device_grouped_union_self", grouped_stream_class)
        self.assertIn("not_needed_all_items_satisfy_predicate", grouped_stream_class)
        self.assertNotIn("dbscan", grouped_stream_class.lower())

    def test_pod_evidence_improves_all_core_clustered_row_and_preserves_correctness(self) -> None:
        baseline = json.loads(BASELINE_SUMMARY.read_text(encoding="utf-8"))
        all_items = json.loads(ALL_ITEMS_SUMMARY.read_text(encoding="utf-8"))
        baseline_by_count = {int(row["point_count"]): row for row in baseline["summaries"]}
        all_items_by_count = {int(row["point_count"]): row for row in all_items["summaries"]}

        self.assertTrue(all_items["tiny_smoke"]["matches_reference"])
        row_32768 = all_items_by_count[32768]
        self.assertTrue(row_32768["signatures_match"])
        self.assertIsNone(row_32768["repeat_rows"][1]["grouped_predicate_mode"])
        self.assertEqual(
            row_32768["repeat_rows"][1]["grouped_transfer_mode"],
            "prepared_device_search_points_self_grouped_union_workspaces",
        )

        row_65536 = all_items_by_count[65536]
        baseline_65536 = baseline_by_count[65536]
        self.assertTrue(row_65536["signatures_match"])
        self.assertEqual(
            row_65536["repeat_rows"][1]["grouped_predicate_mode"],
            "all_items_true_no_fallback_candidates",
        )
        self.assertEqual(
            row_65536["repeat_rows"][1]["grouped_transfer_mode"],
            "prepared_device_search_points_self_grouped_union_all_items_parent_workspace",
        )
        self.assertLess(row_65536["tail_median_sec"], baseline_65536["tail_median_sec"] * 0.92)
        self.assertLess(
            row_65536["grouped_native_tail_median_sec"],
            baseline_65536["grouped_native_tail_median_sec"] * 0.92,
        )


if __name__ == "__main__":
    unittest.main()
