from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2475_same_root_grouped_union_intersection_culling_2026-05-21.md"
POD_SUMMARY = ROOT / "docs" / "reports" / "goal2475_same_root_culling_pod" / "summary.json"
POD_TELEMETRY = ROOT / "docs" / "reports" / "goal2475_same_root_culling_atomic_scale_pod.json"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2475_gemini_review_same_root_culling_pod_2026-05-21.md"
CONSENSUS = ROOT / "docs" / "reviews" / "goal2475_codex_gemini_consensus_same_root_culling_pod_2026-05-21.md"


class Goal2475SameRootGroupedUnionIntersectionCullingTest(unittest.TestCase):
    def test_intersection_skips_same_root_parent_candidates_before_report(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        start = core.index('extern "C" __global__ void __intersection__frn3d_grouped_union_isect()')
        end = core.index('extern "C" __global__ void __anyhit__frn3d_grouped_union_anyhit()', start)
        intersection = core[start:end]

        self.assertIn("bool parent_union_candidate = false", intersection)
        self.assertIn("parent_union_candidate = true", intersection)
        self.assertIn("find_grouped_union_root_readonly(params.parent_out, (int)source)", intersection)
        self.assertIn("find_grouped_union_root_readonly(params.parent_out, (int)prim)", intersection)
        self.assertIn("if (source_root == target_root)", intersection)
        self.assertLess(intersection.index("const float radius_sq"), intersection.index("source_root"))
        self.assertLess(intersection.index("source_root"), intersection.index("optixReportIntersection"))
        self.assertNotIn("dbscan", intersection.lower())
        self.assertNotIn("cluster", intersection.lower())

    def test_runtime_metadata_names_same_root_policy(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("grouped_union_same_root_culling_policy", runtime)
        self.assertIn("parent_union_same_root_before_anyhit", runtime)
        self.assertIn("grouped_union_intersection_culling_policy", runtime)

    def test_report_keeps_pod_gate_and_generic_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("pod validated on 2026-05-21", report)
        self.assertIn("No DBSCAN-specific native ABI or vocabulary was added", report)
        self.assertIn("same-root culling", report)
        self.assertIn("Public performance claims remain blocked", report)
        self.assertIn("1.249x", report)
        self.assertIn("signatures match", report)

    def test_pod_artifacts_record_positive_internal_evidence(self) -> None:
        summary = POD_SUMMARY.read_text(encoding="utf-8")
        telemetry = POD_TELEMETRY.read_text(encoding="utf-8")

        self.assertIn('"NVIDIA RTX A5000, 570.211.01"', summary)
        self.assertIn('"signatures_match": true', summary)
        self.assertIn('"prepared_rt_core_grouped_union_3d_all_items_self_query"', summary)
        self.assertIn('"goal": "Goal2473"', telemetry)
        self.assertIn('"tail_median_parent_attempts_per_point"', telemetry)

    def test_external_review_and_consensus_accept_internal_engineering_direction(self) -> None:
        review = GEMINI_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Blocking Issues: None", review)
        self.assertIn("Approved", review)
        self.assertIn("accepted as a correct and beneficial internal engineering", consensus)
        self.assertIn("Public performance wording remains unauthorized", consensus)


if __name__ == "__main__":
    unittest.main()
