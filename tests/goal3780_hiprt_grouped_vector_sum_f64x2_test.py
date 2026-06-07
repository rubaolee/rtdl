from __future__ import annotations

import json
import math
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
REPORT = ROOT / "docs" / "reports" / "goal3780_hiprt_grouped_vector_sum_f64x2_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3780_hiprt_grouped_vector_sum_f64x2_a5000.json"


def _native_grouped_vector_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return getattr(lib, "rtdl_hiprt_grouped_vector_sum_f64x2", None) is not None


def _symbol_body(source: str, symbol: str) -> str:
    start = source.index(symbol)
    end = source.index("\nextern \"C\"", start + len(symbol))
    return source[start:end]


class Goal3780HiprtGroupedVectorSumPortableTest(unittest.TestCase):
    def test_native_symbol_is_generic_and_app_free(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        runtime = HIPRT_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_grouped_vector_sum_f64x2", api)
        self.assertIn("grouped_vector_sum_f64x2_hiprt", runtime)
        body = _symbol_body(api, "rtdl_hiprt_grouped_vector_sum_f64x2")
        self.assertIn("values_x", body)
        self.assertIn("values_y", body)
        self.assertIn("group_id out of dense group_count range", body)
        for forbidden in ("barnes", "force", "mass", "theta", "inverse", "body"):
            self.assertNotIn(forbidden, body.lower())

    def test_feature_matrix_records_generic_vector_sum_hiprt(self) -> None:
        support = rt.engine_feature_support("grouped_vector_sum_f64x2", "hiprt")
        self.assertEqual(support.status, NATIVE)
        self.assertIn("Goal3780", support.note)

    def test_barnes_hut_parity_gap_is_closed_for_functional_amd_pod(self) -> None:
        self.assertEqual(
            V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION,
            "rtdl.v2_10.amd_hiprt_benchmark_parity_after_goal3782.v1",
        )
        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        barnes = rows["barnes_hut"]
        self.assertIn("grouped_vector_sum_f64x2", barnes["required_engine_features"])
        self.assertEqual(barnes["hiprt_feature_statuses"]["grouped_vector_sum_f64x2"], NATIVE)
        self.assertEqual(barnes["missing_generic_contracts"], ())
        self.assertEqual(barnes["parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("Goal3780", barnes["rationale"])

        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 10)
        self.assertEqual(summary["stage_counts"]["compatibility_only_not_amd_perf_ready"], 0)
        self.assertEqual(summary["stage_counts"]["needs_generic_hiprt_extension"], 0)
        self.assertIn("barnes_hut", summary["ready_for_amd_functional_pod_apps"])

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3780", report)
        self.assertIn("rtdl_hiprt_grouped_vector_sum_f64x2", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("does not authorize", report)
        self.assertIn("force laws remain app code", report)

    def test_artifact_records_clean_pod_evidence_when_present(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3780 pod artifact not generated yet")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample"]["rows_match_reference"])
        self.assertEqual(artifact["barnes_hut_missing_generic_contracts"], [])
        self.assertEqual(artifact["barnes_hut_parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_grouped_vector_available(), "HIPRT grouped vector sum symbol unavailable")
class Goal3780HiprtGroupedVectorSumNativeTest(unittest.TestCase):
    def test_direct_grouped_vector_sum_matches_reference(self) -> None:
        result = rt.grouped_vector_sum_f64x2_hiprt(
            (2, 0, 2, 1, 0, 2),
            (1.5, 2.0, -0.5, 7.0, 3.25, 4.5),
            (0.25, -1.0, 2.5, 8.0, 4.0, -0.75),
            group_count=4,
        )
        self.assertTrue(all(math.isclose(a, b) for a, b in zip(result["sum_x"], (5.25, 7.0, 5.5, 0.0))))
        self.assertTrue(all(math.isclose(a, b) for a, b in zip(result["sum_y"], (3.0, 8.0, 2.0, 0.0))))
        self.assertFalse(result["metadata"]["release_authorized"])
        self.assertTrue(result["metadata"]["not_amd_hardware_evidence"])

    def test_out_of_range_group_fails_closed(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "group_id out of dense group_count range"):
            rt.grouped_vector_sum_f64x2_hiprt((0, 3), (1.0, 2.0), (1.0, 2.0), group_count=2)


if __name__ == "__main__":
    unittest.main()
