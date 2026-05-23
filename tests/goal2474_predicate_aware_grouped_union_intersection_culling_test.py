from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2474_predicate_aware_grouped_union_intersection_culling_2026-05-21.md"


class Goal2474PredicateAwareGroupedUnionIntersectionCullingTest(unittest.TestCase):
    def test_intersection_culls_predicated_noop_hits_before_anyhit(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        start = core.index('extern "C" __global__ void __intersection__frn3d_grouped_union_isect()')
        end = core.index('extern "C" __global__ void __anyhit__frn3d_grouped_union_anyhit()', start)
        intersection = core[start:end]

        self.assertIn("params.predicate_flags[source]", intersection)
        self.assertIn("params.predicate_flags[prim]", intersection)
        self.assertIn("if (prim <= source || !target_predicate)", intersection)
        self.assertIn("} else if (!target_predicate) {", intersection)
        self.assertIn("optixReportIntersection", intersection)
        self.assertLess(intersection.index("params.predicate_flags[source]"), intersection.index("optixReportIntersection"))
        self.assertNotIn("dbscan", intersection.lower())
        self.assertNotIn("cluster", intersection.lower())

    def test_anyhit_keeps_safety_checks_after_intersection_culling(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        start = core.index('extern "C" __global__ void __anyhit__frn3d_grouped_union_anyhit()')
        end = core.index(")CUDA\";", start)
        anyhit = core[start:end]

        self.assertIn("const bool source_predicate", anyhit)
        self.assertIn("target > source && target_predicate", anyhit)
        self.assertIn("atomicMin(params.fallback_candidate_out + source", anyhit)

    def test_runtime_metadata_names_generic_culling_policy(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("grouped_union_intersection_culling_policy", runtime)
        self.assertIn("all_items_target_gt_source_before_anyhit", runtime)
        self.assertIn("predicate_aware_connectivity_and_fallback_before_anyhit", runtime)

    def test_report_keeps_boundary_and_pod_gate(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("pod validated as part of Goal2475", report)
        self.assertIn("No native DBSCAN ABI or vocabulary was added", report)
        self.assertIn("Performance claims are blocked", report)
        self.assertIn("Goal2473", report)
        self.assertIn("optixReportIntersection", report)
        self.assertIn("61 tests OK", report)


if __name__ == "__main__":
    unittest.main()
