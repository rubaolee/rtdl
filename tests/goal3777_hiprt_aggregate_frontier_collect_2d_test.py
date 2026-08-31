from __future__ import annotations

import json
import pathlib
import unittest

import rtdsl as rt
from rtdsl import hiprt_runtime
from rtdsl.engine_feature_matrix import NATIVE
from rtdsl.primitive_hierarchy import find_primitive_hierarchy_node
from rtdsl.v2_10_amd_hiprt_benchmark_parity import V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION
from rtdsl.v2_10_amd_hiprt_benchmark_parity import summarize_v2_10_amd_hiprt_benchmark_parity
from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_PRELUDE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_prelude.h"
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
HIPRT_RUNTIME = ROOT / "src" / "rtdsl" / "hiprt_runtime.py"
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"
REPORT = ROOT / "docs" / "reports" / "goal3777_hiprt_aggregate_frontier_collect_2d_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3777_hiprt_aggregate_frontier_collect_2d_a5000.json"


def _native_collect_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return getattr(lib, "rtdl_hiprt_collect_aggregate_frontier_2d", None) is not None


def _fixture():
    points = tuple(
        {"id": index, "x": float(index % 8), "y": float(index // 8), "mass": 1.0}
        for index in range(32)
    )
    tree = rt.build_bucketized_aggregate_tree_2d(points, bucket_size=4)
    expected = rt.collect_aggregate_frontier_2d(points, tree["nodes"], theta=0.5)
    return points, tree, expected


class Goal3777HiprtAggregateFrontierPortableTest(unittest.TestCase):
    def test_native_symbol_is_generic_and_app_free(self) -> None:
        prelude = HIPRT_PRELUDE.read_text(encoding="utf-8")
        api = HIPRT_API.read_text(encoding="utf-8")
        runtime = HIPRT_RUNTIME.read_text(encoding="utf-8")

        self.assertIn("struct RtdlAggregateFrontierSource2D", prelude)
        self.assertIn("struct RtdlAggregateFrontierNode2D", prelude)
        self.assertIn("rtdl_hiprt_collect_aggregate_frontier_2d", api)
        self.assertIn("collect_aggregate_frontier_2d_hiprt", runtime)
        self.assertIn("fail_closed_overflow", runtime)
        source = "\n".join((prelude, api, runtime)).lower()
        for forbidden in ("barnes", "inverse-square", "contact_manifold", "dbscan"):
            self.assertNotIn(forbidden, source)

    def test_contract_lowering_plan_and_feature_matrix_include_hiprt(self) -> None:
        contract = rt.validate_aggregate_frontier_collect_native_abi_contract()
        self.assertTrue(contract["executable"])
        self.assertIn("rtdl_hiprt_collect_aggregate_frontier_2d", contract["required_native_symbols"])
        self.assertEqual(rt.engine_feature_support("aggregate_frontier_collect_2d", "hiprt").status, NATIVE)

        plan = rt.plan_aggregate_frontier_collect_lowering("hiprt")
        self.assertTrue(plan["executable"])
        self.assertEqual(plan["native_abi_status"], "implemented_for_hiprt")
        self.assertEqual(plan["required_native_symbol"], "rtdl_hiprt_collect_aggregate_frontier_2d")
        self.assertIn("NVIDIA CUDA/Orochi", plan["claim_boundary"])
        self.assertIn("not authorize AMD", plan["claim_boundary"])

    def test_barnes_hut_parity_gap_is_closed_after_goal3780(self) -> None:
        self.assertEqual(
            V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION,
            "rtdl.v2_10.amd_hiprt_benchmark_parity_after_goal3782.v1",
        )
        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        barnes = rows["barnes_hut"]
        self.assertIn("aggregate_frontier_collect_2d", barnes["required_engine_features"])
        self.assertIn("grouped_vector_sum_f64x2", barnes["required_engine_features"])
        self.assertEqual(barnes["hiprt_feature_statuses"]["aggregate_frontier_collect_2d"], NATIVE)
        self.assertEqual(barnes["hiprt_feature_statuses"]["grouped_vector_sum_f64x2"], NATIVE)
        self.assertEqual(barnes["missing_generic_contracts"], ())
        self.assertEqual(barnes["parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("Goal3777", barnes["rationale"])
        self.assertIn("Goal3780", barnes["rationale"])

        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 10)
        self.assertEqual(summary["stage_counts"]["needs_generic_hiprt_extension"], 0)

    def test_catalog_backends_include_hiprt_without_force_claim(self) -> None:
        row_node = find_primitive_hierarchy_node("rows.aggregate_frontier_collect")
        traversal_node = find_primitive_hierarchy_node("candidate.aggregate_frontier_traversal")
        self.assertIn("hiprt", row_node.backends)
        self.assertIn("hiprt", traversal_node.backends)
        self.assertIn("Force laws", row_node.boundary)

        catalog = CATALOG.read_text(encoding="utf-8")
        self.assertIn("rows.aggregate_frontier_collect", catalog)
        self.assertIn("candidate.aggregate_frontier_traversal", catalog)
        self.assertIn("backends: `cpu_python_reference`, `cpu`, `embree`, `optix`, `hiprt`", catalog)

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3777", report)
        self.assertIn("rtdl_hiprt_collect_aggregate_frontier_2d", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("does not authorize", report)
        self.assertIn("grouped vector-force", report)

    def test_artifact_records_clean_pod_evidence_when_present(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3777 pod artifact not generated yet")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample"]["rows_match_reference"])
        self.assertTrue(artifact["sample"]["overflow_fail_closed"])
        self.assertEqual(artifact["barnes_hut_missing_generic_contracts"], ["grouped_vector_force_reduction"])
        self.assertEqual(artifact["barnes_hut_parity_stage"], "needs_generic_hiprt_extension")
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_collect_available(), "HIPRT aggregate-frontier symbol unavailable")
class Goal3777HiprtAggregateFrontierNativeTest(unittest.TestCase):
    def test_native_collect_matches_cpu_reference(self) -> None:
        points, tree, expected = _fixture()
        actual = rt.collect_aggregate_frontier_2d_hiprt(
            points,
            tree["nodes"],
            theta=0.5,
            max_total_rows=expected["summary"]["frontier_row_count"],
        )

        self.assertEqual(actual["frontier_i64_rows"], expected["frontier_i64_rows"])
        self.assertEqual(actual["row_offsets"], expected["row_offsets"])
        self.assertEqual(actual["source_ids"], expected["source_ids"])
        self.assertEqual(actual["metadata"]["native_symbol"], "rtdl_hiprt_collect_aggregate_frontier_2d")
        self.assertFalse(actual["metadata"]["native_engine_app_specific"])

    def test_native_overflow_fails_closed(self) -> None:
        points, tree, _expected = _fixture()
        with self.assertRaisesRegex(rt.AggregateFrontierOverflowError, "partial_result_returned=False"):
            rt.collect_aggregate_frontier_2d_hiprt(
                points,
                tree["nodes"],
                theta=0.5,
                max_total_rows=0,
            )


if __name__ == "__main__":
    unittest.main()
