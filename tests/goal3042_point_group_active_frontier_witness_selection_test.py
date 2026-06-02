from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3042_point_group_active_frontier_witness_selection_2026-06-02.md"
PERF_ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3042_active_frontier_perf_a4000_2026-06-02.json"
OPTIX_RUNTIME = REPO_ROOT / "src" / "rtdsl" / "optix_runtime.py"
OPTIX_API = REPO_ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_CORE = REPO_ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
OPTIX_PRELUDE = REPO_ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_WORKLOADS = REPO_ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
HAUSDORFF_APP = (
    REPO_ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "hausdorff_xhd"
    / "rtdl_hausdorff_v2_function.py"
)
HAUSDORFF_LAB = (
    REPO_ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "hausdorff_xhd"
    / "rtdl_hausdorff_v2_language_lab.py"
)
HAUSDORFF_README = (
    REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "README.md"
)


class Goal3042PointGroupActiveFrontierWitnessSelectionTest(unittest.TestCase):
    def test_report_records_generic_contract_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3042",
            "device-resident active frontier",
            "rtdl_optix_reduce_prepared_point_group_nearest_max_distance_active_frontier_2d",
            "not Hausdorff-specific",
            "materializes_frontier_on_host = False",
            "not a true-zero-copy claim",
            "A4000 pod timing collected",
            "6.536x over CuPy",
            "Public speedup claim: false",
            "App-specific native-engine logic: false",
        ):
            self.assertIn(phrase, text)

    def test_a4000_perf_artifact_records_bounded_positive_result(self) -> None:
        data = json.loads(PERF_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], "Goal3042")
        self.assertEqual(data["source_commit"], "f0b42a1828943de8751084a0d2438b174299fb4b")
        self.assertEqual(data["gpu"], "NVIDIA RTX A4000")
        self.assertEqual(data["cupy_version"], "14.1.1")
        self.assertTrue(data["build_passed"])
        self.assertTrue(data["focused_tests_passed"])
        self.assertTrue(data["runtime_smoke_matched_openmp_witness"])
        self.assertTrue(data["all_rows_match_exact_reference"])
        self.assertGreater(data["best_active_speedup_vs_cupy"], 6.5)
        self.assertFalse(data["v2_6_release_authorized"])
        self.assertFalse(data["public_speedup_claim_authorized"])
        self.assertFalse(data["rt_core_speedup_claim_authorized"])
        self.assertFalse(data["true_zero_copy_claim_authorized"])

        rows = data["rows"]
        self.assertEqual([row["points_a"] for row in rows], [4096, 8192, 16384, 32768, 65536, 131072])
        self.assertGreater(rows[0]["active_vs_cupy_ratio"], 1.0)
        self.assertGreater(rows[1]["active_vs_cupy_ratio"], 1.0)
        self.assertLess(rows[2]["active_vs_cupy_ratio"], 1.0)
        self.assertLess(rows[-1]["active_vs_cupy_ratio"], 0.16)
        for row in rows:
            self.assertTrue(row["all_methods_ok"])
            self.assertTrue(row["all_methods_match_exact_reference"])
            self.assertIn("goal3042_active_frontier_perf_a4000_2026-06-02", row["artifact"])

    def test_native_export_is_generic_and_filters_rows_on_device(self) -> None:
        symbol = "rtdl_optix_reduce_prepared_point_group_nearest_max_distance_active_frontier_2d"
        api = OPTIX_API.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        core = OPTIX_CORE.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        self.assertIn(symbol, api)
        self.assertIn(symbol, prelude)
        self.assertIn("reduce_prepared_point_group_nearest_max_distance_active_frontier_2d_optix", workloads)
        self.assertIn("const uint32_t* active_flags", core)
        self.assertIn("uint32_t* active_query_count", core)
        self.assertIn("atomicAdd(params.active_query_count, 1u)", core)
        self.assertIn("params.output[idx] = {q.id, 0xffffffffu, -1.0f}", core)
        self.assertIn("if (row.distance < 0.0f)", core)

        for source in (api, prelude, core, workloads):
            lowered = source.lower()
            self.assertNotIn("hausdorff", lowered)
            self.assertNotIn("x-hd", lowered)
            self.assertNotIn("xhd", lowered)

    def test_python_runtime_binding_and_closed_claims(self) -> None:
        source = OPTIX_RUNTIME.read_text(encoding="utf-8")
        class_block = source[
            source.index("class PreparedOptixPointGroupNearestWitness2D"):
            source.index("def prepare_optix_point_group_nearest_witness_2d")
        ]
        binding = source[
            source.index("optional_reduce_point_group_active_frontier"):
            source.index("optional_destroy_point_group")
        ]

        self.assertIn("def nearest_max_distance_active_frontier_row", class_block)
        self.assertIn("materializes_frontier_on_host", class_block)
        self.assertIn('"native_reduction": "point_group_nearest_max_distance_active_frontier"', class_block)
        self.assertIn("ctypes.POINTER(_RtdlFixedRadiusNeighborRow)", binding)
        self.assertIn("ctypes.POINTER(ctypes.c_size_t)", binding)
        self.assertIn("optional_reduce_point_group_active_frontier.restype = ctypes.c_int", binding)

    def test_hausdorff_app_uses_native_active_frontier_without_host_flag_subset(self) -> None:
        source = HAUSDORFF_APP.read_text(encoding="utf-8")
        helper = source[
            source.index("def _directed_rt_grouped_active_frontier_nearest_witness"):
            source.index("def _directed_rt_grouped_adaptive_nearest_witness")
        ]

        self.assertIn("nearest_max_distance_active_frontier_row", helper)
        self.assertIn('"point_group_nearest_max_distance_active_frontier"', helper)
        self.assertIn('"materializes_frontier_on_host"', helper)
        self.assertIn("_reduce_nearest_max_distance_row(source_columns, target_columns", helper)
        self.assertNotIn("prepared.threshold_flags", helper)
        self.assertNotIn("_subset_point_columns", helper)

    def test_language_lab_and_readme_expose_method_and_knobs(self) -> None:
        lab = HAUSDORFF_LAB.read_text(encoding="utf-8")
        readme = HAUSDORFF_README.read_text(encoding="utf-8")

        self.assertIn('"rtdl_rt_grouped_active_frontier_nearest_witness"', lab)
        self.assertIn('"cupy_grouped_grid_rawkernel"', lab)
        self.assertIn("--seed-sample-count", lab)
        self.assertIn("--target-points-per-group", lab)
        self.assertIn("rtdl_rt_grouped_active_frontier_nearest_witness", readme)
        self.assertIn("native device-resident active frontier", readme)

    def test_v2_6_roadmap_indexes_goal3042_without_claims(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)

        self.assertEqual(roadmap["point_group_active_frontier_goal"], "Goal3042")
        self.assertIn("generic_optix_active_frontier", roadmap["point_group_active_frontier_status"])
        self.assertIn("a4000_positive_perf_evidence", roadmap["point_group_active_frontier_status"])
        self.assertIn("external_review_pending", roadmap["point_group_active_frontier_status"])
        self.assertIn("not_public_speedup_evidence", roadmap["point_group_active_frontier_status"])
        self.assertEqual(
            roadmap["point_group_active_frontier_artifact"],
            "docs/reports/goal3042_active_frontier_perf_a4000_2026-06-02.json",
        )
        self.assertFalse(roadmap["release_authorized"])
        self.assertFalse(roadmap["public_speedup_claim_authorized"])
        self.assertFalse(roadmap["rt_core_speedup_claim_authorized"])
        self.assertFalse(roadmap["true_zero_copy_claim_authorized"])
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()
