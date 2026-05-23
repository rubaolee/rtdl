from __future__ import annotations

import pathlib
import unittest
import json

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    DEFAULT_BLOCKED_GROUPED_SEGMENT_TARGET_HITS,
    cluster_signature,
    cpu_spatial_bucket_dbscan,
    fixed_radius_pairs_and_neighbor_counts_3d,
    make_rt_dbscan_points,
    plan_rt_dbscan_blocked_grouped_continuation_design,
    simulate_fixed_radius_blocked_grouped_component_continuation_3d,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal2467_blocked_grouped_continuation_design_2026-05-20.md"
POD_REPORT = ROOT / "docs" / "reports" / "goal2467_grouped_stream_baseline_pod_2026-05-20.md"
POD_SUMMARY = ROOT / "docs" / "reports" / "goal2467_grouped_stream_baseline_pod" / "summary.json"
POD_RUNNER = ROOT / "scripts" / "goal2467_grouped_stream_baseline_pod_runner.py"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2467_gemini_blocked_grouped_design_review_2026-05-20.md"
CONSENSUS = ROOT / "docs" / "reviews" / "goal2467_codex_gemini_consensus_blocked_grouped_design_2026-05-20.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal2467BlockedGroupedContinuationDesignTest(unittest.TestCase):
    def test_design_plan_is_not_executable_or_a_hidden_dispatcher(self) -> None:
        plan = plan_rt_dbscan_blocked_grouped_continuation_design("clustered3d", 65536)

        self.assertEqual(plan["design_status"], "needs-more-evidence")
        self.assertFalse(plan["runtime_executable"])
        self.assertFalse(plan["release_claim_authorized"])
        self.assertFalse(plan["performance_claim_authorized"])
        self.assertTrue(plan["pod_validation_required"])
        self.assertTrue(plan["not_hidden_dispatcher"])
        self.assertEqual(
            plan["target_primitive"],
            "generic_fixed_radius_blocked_grouped_component_continuation_3d",
        )
        self.assertGreater(plan["estimated_segment_count"], 1)
        self.assertEqual(plan["segment_target_hits"], DEFAULT_BLOCKED_GROUPED_SEGMENT_TARGET_HITS)

    def test_design_boundary_forbids_app_specific_native_vocabulary(self) -> None:
        plan = plan_rt_dbscan_blocked_grouped_continuation_design("clustered3d", 32768)

        self.assertTrue(plan["app_independent_engine_required"])
        self.assertEqual(plan["forbidden_native_vocabulary"], ["dbscan", "cluster", "min_neighbors"])
        self.assertNotIn("dbscan", str(plan["target_primitive"]).lower())
        self.assertNotIn("dbscan", str(plan["candidate_native_contract"]).lower())

    def test_report_and_todo_record_goal2467_as_design_only(self) -> None:
        app = APP.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        todo = TODO.read_text(encoding="utf-8")

        self.assertIn("plan_rt_dbscan_blocked_grouped_continuation_design", app)
        self.assertIn("generic_fixed_radius_blocked_grouped_component_continuation_3d", report)
        self.assertIn("No native ABI was added", report)
        self.assertIn("No performance claim is authorized", report)
        self.assertIn("proposal_rejection_rate", report)
        self.assertIn("global_parent_atomic_attempts", report)
        self.assertIn("fallback_to_unblocked_grouped_union", report)
        self.assertIn("fixed-budget", report)
        self.assertIn("simulate_fixed_radius_blocked_grouped_component_continuation_3d", report)
        self.assertIn("simulated segmented parent", report)
        self.assertIn("workspace, not from a separate all-pairs shortcut", report)
        self.assertIn("Reference-only local sample", report)
        self.assertIn("hit_stream_pair_count = 562", report)
        self.assertIn("This is not performance evidence", report)
        self.assertIn("Mac-local CPU simulator", todo)
        self.assertIn("Goal2467", todo)
        self.assertIn("blocked/segmented grouped continuation", todo)

    def test_gemini_review_and_consensus_record_design_start_boundary(self) -> None:
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("accept-with-fixes", gemini)
        self.assertIn("Metric Definition", gemini)
        self.assertIn("Memory Bounds", gemini)
        self.assertIn("accept-as-design-start", consensus)
        self.assertIn("no performance", consensus.lower())
        self.assertIn("needs-more-evidence", consensus)

    def test_local_simulator_matches_cpu_reference_and_records_telemetry(self) -> None:
        points = make_rt_dbscan_points("clustered3d", point_count=96, seed=20260520)
        pairs, counts = fixed_radius_pairs_and_neighbor_counts_3d(points, radius=0.055)
        flags = tuple(count >= 12 for count in counts)

        rows, metadata = simulate_fixed_radius_blocked_grouped_component_continuation_3d(
            points,
            radius=0.055,
            predicate_flags=flags,
            neighbor_counts=counts,
            segment_target_hits=64,
        )
        reference_rows, _ = cpu_spatial_bucket_dbscan(points, radius=0.055, min_neighbors=12)

        self.assertEqual(cluster_signature(rows), cluster_signature(reference_rows))
        self.assertGreater(len(pairs), 0)
        self.assertTrue(metadata["reference_only"])
        self.assertFalse(metadata["native_abi_added"])
        self.assertFalse(metadata["runtime_route_authorized"])
        self.assertFalse(metadata["performance_claim_authorized"])
        self.assertFalse(metadata["fallback_to_unblocked_grouped_union"])
        self.assertGreater(metadata["segment_count"], 1)
        self.assertLessEqual(
            metadata["global_parent_atomic_attempts"],
            metadata["baseline_global_parent_atomic_attempts"],
        )
        self.assertIn("proposal_rejection_rate", metadata)

    def test_local_simulator_fails_closed_on_segment_capacity_overflow(self) -> None:
        points = make_rt_dbscan_points("clustered3d", point_count=64, seed=20260520)
        _, counts = fixed_radius_pairs_and_neighbor_counts_3d(points, radius=0.055)
        flags = tuple(count >= 12 for count in counts)

        rows, metadata = simulate_fixed_radius_blocked_grouped_component_continuation_3d(
            points,
            radius=0.055,
            predicate_flags=flags,
            neighbor_counts=counts,
            segment_target_hits=16,
            segment_capacity_hits=4,
        )
        reference_rows, _ = cpu_spatial_bucket_dbscan(points, radius=0.055, min_neighbors=12)

        self.assertEqual(cluster_signature(rows), cluster_signature(reference_rows))
        self.assertTrue(metadata["fallback_to_unblocked_grouped_union"])
        self.assertGreater(metadata["overflow_segment_count"], 0)
        self.assertEqual(metadata["global_parent_atomic_attempts"], 0)
        self.assertEqual(metadata["deduplicated_union_proposals"], 0)

    def test_blackwell_pod_baseline_is_recorded_without_goal2467_claim(self) -> None:
        report = POD_REPORT.read_text(encoding="utf-8")
        summary = json.loads(POD_SUMMARY.read_text(encoding="utf-8"))

        self.assertIn("NVIDIA RTX PRO 4000 Blackwell", report)
        self.assertIn("not a native", report)
        self.assertIn("Goal2467 implementation", report)
        self.assertIn("No Goal2467 performance claim is authorized", report)
        self.assertIn("Replayable runner smoke", report)
        self.assertIn("tiny_smoke_matches_reference = true", report)
        self.assertTrue(summary["claim_boundary"]["goal2465_compatible_baseline_only"])
        self.assertFalse(summary["claim_boundary"]["native_goal2467_implementation"])
        self.assertFalse(summary["claim_boundary"]["goal2467_performance_claim_authorized"])
        self.assertTrue(summary["tiny_smoke_matches_reference"])
        self.assertEqual([row["point_count"] for row in summary["summaries"]], [32768, 65536])
        for row in summary["summaries"]:
            self.assertTrue(row["signatures_match"])
            self.assertGreater(row["grouped_native_tail_median_sec"], 0.0)

    def test_pod_baseline_runner_preserves_claim_boundary(self) -> None:
        runner = POD_RUNNER.read_text(encoding="utf-8")

        self.assertIn("Collect Goal2467 grouped-stream pod baseline", runner)
        self.assertIn("goal2465_compatible_baseline_only", runner)
        self.assertIn("\"native_goal2467_implementation\": False", runner)
        self.assertIn("simulate_fixed_radius_blocked_grouped_component_continuation_3d", runner)


if __name__ == "__main__":
    unittest.main()
