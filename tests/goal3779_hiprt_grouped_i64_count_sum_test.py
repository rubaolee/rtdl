from __future__ import annotations

import json
import pathlib
import unittest

import rtdsl as rt
from rtdsl import hiprt_runtime
from rtdsl.engine_feature_matrix import COMPATIBILITY_FALLBACK
from rtdsl.engine_feature_matrix import NATIVE
from rtdsl.primitive_hierarchy import find_primitive_hierarchy_node
from rtdsl.v2_10_amd_hiprt_benchmark_parity import V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION
from rtdsl.v2_10_amd_hiprt_benchmark_parity import summarize_v2_10_amd_hiprt_benchmark_parity
from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
HIPRT_RUNTIME = ROOT / "src" / "rtdsl" / "hiprt_runtime.py"
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"
REPORT = ROOT / "docs" / "reports" / "goal3779_hiprt_grouped_i64_count_sum_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3779_hiprt_grouped_i64_count_sum_a5000.json"


def _native_grouped_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return getattr(lib, "rtdl_hiprt_grouped_i64_count_sum", None) is not None


def _symbol_body(source: str, symbol: str) -> str:
    start = source.index(symbol)
    end = source.index("\nextern \"C\"", start + len(symbol))
    return source[start:end]


class Goal3779HiprtGroupedI64CountSumPortableTest(unittest.TestCase):
    def test_native_symbol_is_generic_and_app_free(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        runtime = HIPRT_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_grouped_i64_count_sum", api)
        self.assertIn("grouped_i64_count_sum_hiprt", runtime)
        body = _symbol_body(api, "rtdl_hiprt_grouped_i64_count_sum")
        self.assertIn("group_ids", body)
        self.assertIn("group_id out of dense group_count range", body)
        for forbidden in ("raydb", "database", "sql", "conjunctive", "query", "predicate"):
            self.assertNotIn(forbidden, body.lower())

    def test_feature_matrix_and_catalog_record_generic_grouped_reduction_hiprt(self) -> None:
        support = rt.engine_feature_support("grouped_i64_count_sum", "hiprt")
        self.assertEqual(support.status, NATIVE)
        self.assertIn("Goal3779", support.note)
        self.assertEqual(
            rt.engine_feature_support("bounded_db_conjunctive_scan", "hiprt").status,
            COMPATIBILITY_FALLBACK,
        )
        node = find_primitive_hierarchy_node("reduction.grouped")
        self.assertIn("hiprt", node.backends)
        catalog = CATALOG.read_text(encoding="utf-8")
        self.assertIn("reduction.grouped", catalog)
        self.assertIn("backends: `cpu_python_reference`, `cpu`, `optix`, `hiprt`", catalog)

    def test_raydb_parity_gap_is_closed_after_goal3781(self) -> None:
        self.assertEqual(
            V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION,
            "rtdl.v2_10.amd_hiprt_benchmark_parity_after_goal3782.v1",
        )
        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        raydb = rows["raydb_style"]
        self.assertIn("columnar_i64_predicate_scan", raydb["required_engine_features"])
        self.assertIn("grouped_i64_count_sum", raydb["required_engine_features"])
        self.assertEqual(raydb["hiprt_feature_statuses"]["columnar_i64_predicate_scan"], NATIVE)
        self.assertEqual(raydb["hiprt_feature_statuses"]["grouped_i64_count_sum"], NATIVE)
        self.assertNotIn("native_hiprt_grouped_i64_count_sum_fastpath", raydb["missing_generic_contracts"])
        self.assertNotIn("native_hiprt_columnar_predicate_scan_fastpath", raydb["missing_generic_contracts"])
        self.assertEqual(raydb["missing_generic_contracts"], ())
        self.assertEqual(raydb["parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("Goal3779", raydb["rationale"])
        self.assertIn("Goal3781", raydb["rationale"])

        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 10)
        self.assertEqual(summary["stage_counts"]["compatibility_only_not_amd_perf_ready"], 0)
        self.assertEqual(summary["stage_counts"]["needs_generic_hiprt_extension"], 0)

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3779", report)
        self.assertIn("rtdl_hiprt_grouped_i64_count_sum", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("does not authorize", report)
        self.assertIn("native_hiprt_columnar_predicate_scan_fastpath", report)

    def test_artifact_records_clean_pod_evidence_when_present(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3779 pod artifact not generated yet")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample"]["rows_match_reference"])
        self.assertEqual(artifact["raydb_style_missing_generic_contracts"], ["native_hiprt_columnar_predicate_scan_fastpath"])
        self.assertEqual(artifact["raydb_style_parity_stage"], "compatibility_only_not_amd_perf_ready")
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_grouped_available(), "HIPRT grouped i64 count/sum symbol unavailable")
class Goal3779HiprtGroupedI64CountSumNativeTest(unittest.TestCase):
    def test_direct_grouped_count_sum_matches_reference(self) -> None:
        result = rt.grouped_i64_count_sum_hiprt(
            (2, 0, 2, 1, 0, 2),
            (5, 10, -1, 7, 3, 4),
            group_count=4,
        )
        self.assertEqual(result["counts"], (2, 1, 3, 0))
        self.assertEqual(result["sums"], (13, 7, 8, 0))
        self.assertFalse(result["metadata"]["release_authorized"])
        self.assertTrue(result["metadata"]["not_amd_hardware_evidence"])

    def test_out_of_range_group_fails_closed(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "group_id out of dense group_count range"):
            rt.grouped_i64_count_sum_hiprt((0, 3), (1, 2), group_count=2)


if __name__ == "__main__":
    unittest.main()
