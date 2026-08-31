from __future__ import annotations

import json
import pathlib
import unittest

import rtdsl as rt
from rtdsl import hiprt_runtime
from rtdsl.engine_feature_matrix import NATIVE
from rtdsl.v2_10_amd_hiprt_benchmark_parity import V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION
from rtdsl.v2_10_amd_hiprt_benchmark_parity import summarize_v2_10_amd_hiprt_benchmark_parity
from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
HIPRT_RUNTIME = ROOT / "src" / "rtdsl" / "hiprt_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal3781_hiprt_columnar_i64_predicate_scan_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3781_hiprt_columnar_i64_predicate_scan_a5000.json"


def _native_scan_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return getattr(lib, "rtdl_hiprt_columnar_i64_predicate_scan", None) is not None


def _symbol_body(source: str, symbol: str) -> str:
    start = source.index(symbol)
    end = source.index("\nextern \"C\"", start + len(symbol))
    return source[start:end]


class Goal3781HiprtColumnarI64PredicateScanPortableTest(unittest.TestCase):
    def test_native_symbol_is_generic_and_app_free(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        runtime = HIPRT_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_columnar_i64_predicate_scan", api)
        self.assertIn("columnar_i64_predicate_scan_hiprt", runtime)
        body = _symbol_body(api, "rtdl_hiprt_columnar_i64_predicate_scan")
        self.assertIn("predicate op code", body)
        self.assertIn("column_values[column_index * row_count + row_index]", body)
        for forbidden in ("raydb", "database", "sql", "dbms", "table", "query"):
            self.assertNotIn(forbidden, body.lower())

    def test_feature_matrix_records_generic_columnar_scan_hiprt(self) -> None:
        support = rt.engine_feature_support("columnar_i64_predicate_scan", "hiprt")
        self.assertEqual(support.status, NATIVE)
        self.assertIn("Goal3781", support.note)

    def test_raydb_parity_gap_is_closed_for_functional_amd_pod(self) -> None:
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
        self.assertEqual(raydb["missing_generic_contracts"], ())
        self.assertEqual(raydb["parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("Goal3781", raydb["rationale"])

        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 10)
        self.assertEqual(summary["stage_counts"]["compatibility_only_not_amd_perf_ready"], 0)
        self.assertEqual(summary["stage_counts"]["needs_generic_hiprt_extension"], 0)
        self.assertEqual(summary["compatibility_only_not_amd_perf_ready_apps"], ())

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3781", report)
        self.assertIn("rtdl_hiprt_columnar_i64_predicate_scan", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("does not authorize", report)
        self.assertIn("not SQL", report)

    def test_artifact_records_clean_pod_evidence_when_present(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3781 pod artifact not generated yet")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample"]["rows_match_reference"])
        self.assertEqual(artifact["raydb_style_missing_generic_contracts"], [])
        self.assertEqual(artifact["raydb_style_parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_scan_available(), "HIPRT columnar i64 predicate-scan symbol unavailable")
class Goal3781HiprtColumnarI64PredicateScanNativeTest(unittest.TestCase):
    def test_direct_columnar_scan_matches_reference(self) -> None:
        result = rt.columnar_i64_predicate_scan_hiprt(
            (
                (10, 20, 30, 40, 50, 60),
                (1, 2, 1, 2, 1, 2),
                (7, 7, 9, 7, 11, 7),
            ),
            (
                {"column": 0, "op": "ge", "value": 30},
                {"column": 1, "op": "eq", "value": 2},
                {"column": 2, "op": "eq", "value": 7},
            ),
        )
        self.assertEqual(result["row_ids"], (3, 5))
        self.assertFalse(result["metadata"]["release_authorized"])
        self.assertTrue(result["metadata"]["not_amd_hardware_evidence"])

    def test_overflow_fails_closed(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "fail_closed_overflow"):
            rt.columnar_i64_predicate_scan_hiprt(((1, 2, 3),), ({"column": 0, "op": "gt", "value": 0},), row_capacity=2)


if __name__ == "__main__":
    unittest.main()
