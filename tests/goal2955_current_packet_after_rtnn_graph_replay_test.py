from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2955_current_packet_after_rtnn_graph_replay_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2955_current_packet_after_rtnn_graph_pod"
SUMMARY = ARTIFACT_DIR / "goal2855_summary.json"
TRIAGE = ARTIFACT_DIR / "goal2955_triage.json"
EXPECTED_COMMIT = "747716c7141341b43a4bed37f66c53d0ff2bcc14"


class Goal2955CurrentPacketAfterRtnnGraphReplayTest(unittest.TestCase):
    def test_packet_summary_is_clean_and_bounded(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertEqual(EXPECTED_COMMIT, summary["source_commit"])
        self.assertEqual({}, summary["claim_boundary_violations"])
        self.assertEqual({}, summary["dirty_artifacts"])
        self.assertFalse(summary["claim_boundary"]["v2_5_release_authorized"])
        self.assertFalse(summary["claim_boundary"]["public_speedup_claim_authorized"])
        for artifact in summary["artifacts"].values():
            self.assertEqual("pass", artifact["status"])
            self.assertEqual(EXPECTED_COMMIT, artifact["source_commit"])
            self.assertEqual([], artifact["source_dirty"])

    def test_perf_triage_has_zero_current_targets(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))

        self.assertEqual("pass", triage["status"])
        self.assertEqual([], triage["performance_targets"])
        self.assertIsNone(triage["top_priority"])
        rtnn = next(app for app in triage["apps"] if app["app"] == "rtnn")
        self.assertEqual(
            "optix_prepared_query_cuda_graph_ranked_summary_aggregate_vs_cupy_grid",
            rtnn["route"],
        )
        self.assertEqual(
            ["ranked-summary-aggregate-prepared-query-batch-graph-float32"],
            rtnn["result_modes"],
        )
        self.assertGreater(float(rtnn["min_cupy_over_rtdl_ratio"]), 1.0)

    def test_key_rows_record_expected_improvements_without_claims(self) -> None:
        rtnn = json.loads((ARTIFACT_DIR / "goal2800_rtnn.json").read_text(encoding="utf-8"))
        hausdorff = json.loads((ARTIFACT_DIR / "goal2801_hausdorff_xhd.json").read_text(encoding="utf-8"))
        barnes = json.loads((ARTIFACT_DIR / "goal2803_barnes_hut.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", rtnn["status"])
        ratios = {row["distribution"]: float(row["cupy_grid_over_rtdl_elapsed_ratio"]) for row in rtnn["rows"]}
        self.assertGreater(ratios["uniform"], 1.0)
        self.assertGreater(ratios["clustered"], 2.0)
        self.assertGreater(ratios["shell"], 7.0)
        self.assertTrue(all(row["ranked_aggregate_matches_cupy_grid"] for row in rtnn["rows"]))
        self.assertFalse(rtnn["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])

        self.assertEqual("pass", hausdorff["status"])
        self.assertTrue(hausdorff["matches_exact_baseline"])
        self.assertLess(float(hausdorff["rtdl_over_cupy_grid_elapsed_ratio"]), 1.0)
        self.assertFalse(hausdorff["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])

        self.assertEqual("pass", barnes["status"])
        self.assertGreater(float(barnes["max_optix_membership_speedup_vs_embree"]), 100.0)
        self.assertEqual("cupy", barnes["vector_sum"]["selected_partner"])
        self.assertFalse(barnes["claim_boundary"]["public_speedup_claim_authorized"])

    def test_readiness_keeps_release_blocked_after_goal2955(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        self.assertEqual(0, validation["current_packet_perf_target_count"])
        self.assertEqual(0, packet["current_packet_perf_triage"]["performance_target_count"])
        self.assertIn("keep_goal2955_current_packet_zero_perf_targets_green", packet["allowed_next_actions"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])

    def test_report_documents_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2955",
            "Performance targets | `0`",
            "`1.147x`",
            "`0.901x`",
            "internal engineering evidence",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
