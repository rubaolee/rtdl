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
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
HIPRT_CORE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_core.cpp"
HIPRT_KERNELS = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_kernels.cpp"
HIPRT_RUNTIME = ROOT / "src" / "rtdsl" / "hiprt_runtime.py"
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"
REPORT = ROOT / "docs" / "reports" / "goal3782_hiprt_graph_cycle_count_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3782_hiprt_graph_cycle_count_a5000.json"


def _native_graph_cycle_count_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return (
        getattr(lib, "rtdl_hiprt_count_triangle_cycle_candidates", None) is not None
        and getattr(lib, "rtdl_hiprt_count_prepared_triangle_cycle_candidates", None) is not None
    )


def _symbol_body(source: str, symbol: str) -> str:
    start = source.index(symbol)
    end = source.find("\nextern \"C\"", start + len(symbol))
    return source[start:] if end == -1 else source[start:end]


def _graph_fixture() -> rt.CSRGraph:
    return rt.csr_graph(
        row_offsets=(0, 2, 4, 6, 7, 7),
        column_indices=(1, 2, 0, 2, 0, 1, 4),
    )


def _canonical_seeds() -> tuple[rt.EdgeSeed, ...]:
    return (rt.EdgeSeed(0, 1), rt.EdgeSeed(0, 2), rt.EdgeSeed(1, 2))


class Goal3782HiprtGraphCycleCountPortableTest(unittest.TestCase):
    def test_native_symbols_are_generic_and_app_free(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        core = HIPRT_CORE.read_text(encoding="utf-8")
        kernels = HIPRT_KERNELS.read_text(encoding="utf-8")
        runtime = HIPRT_RUNTIME.read_text(encoding="utf-8")

        self.assertIn("rtdl_hiprt_count_triangle_cycle_candidates", api)
        self.assertIn("rtdl_hiprt_count_prepared_triangle_cycle_candidates", api)
        self.assertIn("RtdlTriangleProbeCountKernel", kernels)
        self.assertIn("count_prepared_triangle_cycle_candidates", core)
        self.assertIn("triangle_cycle_count_hiprt", runtime)
        self.assertIn("canonical ascending edge seeds", core)

        for symbol in (
            "rtdl_hiprt_count_triangle_cycle_candidates",
            "rtdl_hiprt_count_prepared_triangle_cycle_candidates",
        ):
            body = _symbol_body(api, symbol)
            for forbidden in ("app", "benchmark", "analytics", "paper", "rayjoin", "dbscan"):
                self.assertNotIn(forbidden, body.lower())

    def test_feature_matrix_catalog_and_parity_close_last_hiprt_gap(self) -> None:
        support = rt.engine_feature_support("graph_triangle_count", "hiprt")
        self.assertEqual(support.status, NATIVE)
        self.assertIn("Goal3782", support.note)
        self.assertEqual(
            V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION,
            "rtdl.v2_10.amd_hiprt_benchmark_parity_after_goal3782.v1",
        )

        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        triangle = rows["triangle_counting"]
        self.assertEqual(triangle["required_engine_features"], ("graph_triangle_count",))
        self.assertEqual(triangle["missing_generic_contracts"], ())
        self.assertEqual(triangle["parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("Goal3782", triangle["rationale"])

        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 10)
        self.assertEqual(summary["stage_counts"]["compatibility_only_not_amd_perf_ready"], 0)
        self.assertEqual(summary["stage_counts"]["needs_generic_hiprt_extension"], 0)
        self.assertEqual(summary["compatibility_only_not_amd_perf_ready_apps"], ())
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["amd_perf_claim_authorized"])

        node = find_primitive_hierarchy_node("reduction.graph_cycle_count")
        self.assertIn("hiprt", node.backends)
        self.assertIn("rows.graph_triangle_witness_rows", node.considered_alternatives)
        catalog = CATALOG.read_text(encoding="utf-8")
        self.assertIn("reduction.graph_cycle_count", catalog)
        self.assertIn("canonical graph-cycle", catalog)

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3782", report)
        self.assertIn("rtdl_hiprt_count_prepared_triangle_cycle_candidates", report)
        self.assertIn("canonical ascending unique seed", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("does not authorize", report)

    def test_artifact_records_clean_pod_evidence_when_present(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3782 pod artifact not generated yet")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample"]["counts_match_reference"])
        self.assertEqual(artifact["triangle_counting_missing_generic_contracts"], [])
        self.assertEqual(artifact["triangle_counting_parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_graph_cycle_count_available(), "HIPRT graph-cycle scalar count symbols unavailable")
class Goal3782HiprtGraphCycleCountNativeTest(unittest.TestCase):
    def test_direct_graph_cycle_count_matches_row_reference(self) -> None:
        graph = _graph_fixture()
        seeds = _canonical_seeds()
        expected = len(rt.triangle_probe_cpu(graph, seeds, order="id_ascending", unique=True))
        self.assertEqual(rt.triangle_cycle_count_hiprt(graph, seeds), expected)

    def test_prepared_graph_cycle_count_matches_row_reference(self) -> None:
        graph = _graph_fixture()
        seeds = _canonical_seeds()
        expected = len(rt.triangle_probe_cpu(graph, seeds, order="id_ascending", unique=True))
        with rt.prepare_hiprt_graph_csr(graph) as prepared:
            self.assertEqual(prepared.triangle_cycle_count(seeds), expected)

    def test_noncanonical_or_duplicate_seeds_fail_closed(self) -> None:
        graph = _graph_fixture()
        with self.assertRaisesRegex(ValueError, "canonical ascending"):
            rt.triangle_cycle_count_hiprt(graph, (rt.EdgeSeed(1, 0),))
        with self.assertRaisesRegex(ValueError, "unique edge seeds"):
            rt.triangle_cycle_count_hiprt(graph, (rt.EdgeSeed(0, 1), rt.EdgeSeed(0, 1)))


if __name__ == "__main__":
    unittest.main()
