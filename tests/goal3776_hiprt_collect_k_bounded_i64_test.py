from __future__ import annotations

import ctypes
import json
import pathlib
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.contact_manifold import (
    rtdl_contact_manifold_benchmark_app as contact_app,
)
from rtdsl import hiprt_runtime
from rtdsl.engine_feature_matrix import NATIVE
from rtdsl.primitive_hierarchy import find_primitive_hierarchy_node
from rtdsl.v2_10_amd_hiprt_benchmark_parity import V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION
from rtdsl.v2_10_amd_hiprt_benchmark_parity import summarize_v2_10_amd_hiprt_benchmark_parity
from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
HIPRT_NATIVE_DIR = ROOT / "src" / "native" / "hiprt"
CONTACT_APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "contact_manifold"
    / "rtdl_contact_manifold_benchmark_app.py"
)
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"
REPORT = ROOT / "docs" / "reports" / "goal3776_hiprt_collect_k_bounded_i64_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3776_hiprt_collect_k_bounded_i64_a5000.json"


def _native_collect_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return getattr(lib, "rtdl_hiprt_collect_k_bounded_i64", None) is not None


class Goal3776HiprtCollectKBoundedPortableTest(unittest.TestCase):
    def test_native_symbol_is_generic_and_app_free(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_collect_k_bounded_i64", api)
        self.assertIn("std::sort(rows.begin(), rows.end())", api)
        self.assertIn("std::unique(rows.begin(), rows.end())", api)
        self.assertIn("*overflowed_out = 1u", api)
        for path in HIPRT_NATIVE_DIR.glob("rtdl_hiprt_*"):
            if path.is_file():
                source = path.read_text(encoding="utf-8", errors="ignore").lower()
                self.assertNotIn("contact", source, path)
                self.assertNotIn("manifold", source, path)

    def test_contact_app_can_route_same_generic_symbol_to_hiprt(self) -> None:
        source = CONTACT_APP.read_text(encoding="utf-8")
        session = contact_app.describe_v2_4_bounded_witness_session(
            backend="hiprt",
            candidate_row_count=3,
            witness_capacity=3,
        )
        self.assertEqual(session["backend"], "hiprt")
        self.assertEqual(session["native_symbols"], ("rtdl_hiprt_collect_k_bounded_i64",))
        self.assertIn("RTDL_HIPRT_LIBRARY", source)
        self.assertIn("rtdl_{normalized_backend}_collect_k_bounded_i64", source)

    def test_feature_matrix_parity_and_catalog_advance_contact(self) -> None:
        self.assertEqual(rt.engine_feature_support("collect_k_bounded_i64", "hiprt").status, NATIVE)
        self.assertEqual(
            V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION,
            "rtdl.v2_10.amd_hiprt_benchmark_parity_after_goal3779.v1",
        )
        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        contact = rows["contact_manifold"]
        self.assertIn("collect_k_bounded_i64", contact["required_engine_features"])
        self.assertEqual(contact["hiprt_feature_statuses"]["collect_k_bounded_i64"], NATIVE)
        self.assertEqual(contact["missing_generic_contracts"], ())
        self.assertEqual(contact["parity_stage"], "ready_for_amd_functional_pod")
        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 7)
        self.assertEqual(summary["stage_counts"]["needs_generic_hiprt_extension"], 1)

        collect_node = find_primitive_hierarchy_node("materialization.collect_k_bounded")
        schema_node = find_primitive_hierarchy_node("materialization.row_schema_validation")
        self.assertIn("hiprt", collect_node.backends)
        self.assertIn("hiprt", schema_node.backends)
        catalog = CATALOG.read_text(encoding="utf-8")
        self.assertIn("materialization.collect_k_bounded", catalog)
        self.assertIn(
            "backends: `cpu_python_reference`, `cpu`, `embree`, `optix`, `hiprt`",
            catalog,
        )

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3776", report)
        self.assertIn("rtdl_hiprt_collect_k_bounded_i64", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("does not authorize", report)

    def test_artifact_records_clean_pod_evidence_when_present(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3776 pod artifact not generated yet")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample"]["rows_match_reference"])
        self.assertTrue(artifact["sample"]["overflow_fail_closed"])
        self.assertEqual(artifact["contact_manifold_missing_generic_contracts"], [])
        self.assertEqual(artifact["contact_manifold_parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_collect_available(), "HIPRT collect-k symbol unavailable")
class Goal3776HiprtCollectKBoundedNativeTest(unittest.TestCase):
    def test_direct_generic_collect_matches_python_reference(self) -> None:
        lib = hiprt_runtime._hiprt_lib()
        result = rt.collect_native_i64_rows_with_backend_symbol(
            ((2, 20, 3), (0, 10, 1), (0, 10, 1), (1, 11, 2)),
            capacity=3,
            row_width=3,
            backend="hiprt",
            library=lib,
            symbol_name="rtdl_hiprt_collect_k_bounded_i64",
            candidate_source_symbol="goal3776_python_tuple_fixture",
        )
        self.assertEqual(result["candidate_id_rows"], ((0, 10, 1), (1, 11, 2), (2, 20, 3)))
        self.assertEqual(result["valid_count"], 3)
        self.assertFalse(result["overflowed"])

    def test_contact_native_collect_route_matches_cpu_reference(self) -> None:
        payload = contact_app.native_collect_k_payload(dataset="tiny", witness_capacity=3, backend="hiprt")
        self.assertEqual(payload["native_generic_symbol"], "rtdl_hiprt_collect_k_bounded_i64")
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["candidate_id_rows"], contact_app.tiny_fixture().expected_witness_rows)

    def test_overflow_fails_closed(self) -> None:
        lib = hiprt_runtime._hiprt_lib()
        with self.assertRaisesRegex(RuntimeError, "overflowed"):
            rt.collect_native_i64_rows_with_backend_symbol(
                ((2, 20, 3), (0, 10, 1), (1, 11, 2)),
                capacity=2,
                row_width=3,
                backend="hiprt",
                library=lib,
                symbol_name="rtdl_hiprt_collect_k_bounded_i64",
                candidate_source_symbol="goal3776_overflow_fixture",
            )


if __name__ == "__main__":
    unittest.main()
