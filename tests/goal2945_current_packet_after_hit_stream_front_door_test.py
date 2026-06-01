from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2945_current_packet_after_hit_stream_front_door_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2945_current_packet_after_hit_stream_front_door_pod"
SUMMARY = ARTIFACT_DIR / "goal2855_summary.json"
TRIAGE = ARTIFACT_DIR / "goal2945_triage.json"
FRONT_DOOR_REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2943_generic_event_ordered_hit_stream_front_door_2026-06-01.md"
)


class Goal2945CurrentPacketAfterHitStreamFrontDoorTest(unittest.TestCase):
    def test_packet_passes_cleanly_after_hit_stream_front_door(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertEqual("5b6741fa7bf08a4934b283bd755a67af2b04ed7b", summary["source_commit"])
        self.assertTrue(summary["source_commit_consistent"])
        self.assertEqual({}, summary["dirty_artifacts"])
        self.assertEqual({}, summary["claim_boundary_violations"])
        self.assertFalse(summary["claim_boundary"]["v2_5_release_authorized"])
        self.assertFalse(summary["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(summary["claim_boundary"]["true_zero_copy_claim_authorized"])

    def test_toolchain_metadata_records_reachable_optix_library(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        toolchain = summary["runner_metadata"]["toolchain"]

        self.assertEqual("rtdl.goal2916.toolchain_provenance.v1", toolchain["metadata_version"])
        self.assertEqual("compute_86", toolchain["rtdl_optix_ptx_arch"])
        self.assertEqual("nvcc", toolchain["rtdl_optix_ptx_compiler"])
        self.assertTrue(toolchain["rtdl_optix_library_exists"])
        self.assertTrue(str(toolchain["rtdl_optix_library"]).endswith("build/librtdl_optix.so"))
        self.assertTrue(toolchain["optix_header_exists"])
        self.assertFalse(toolchain["claim_boundary"]["compiler_fairness_claim_authorized"])
        self.assertFalse(toolchain["claim_boundary"]["multivendor_claim_authorized"])

    def test_triage_has_no_current_perf_targets(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))
        apps = {row["app"]: row for row in triage["apps"]}

        self.assertEqual("pass", triage["status"])
        self.assertEqual([], triage["performance_targets"])
        self.assertIsNone(triage["top_priority"])
        self.assertEqual("current_path_acceptable", apps["rtnn"]["performance_status"])
        self.assertGreater(apps["rtnn"]["min_cupy_over_rtdl_ratio"], 1.0)
        self.assertEqual("current_path_acceptable", apps["hausdorff_xhd"]["performance_status"])
        self.assertLess(apps["hausdorff_xhd"]["rtdl_over_cupy_ratio"], 1.0)
        self.assertEqual("current_path_acceptable", apps["rt_dbscan"]["performance_status"])
        self.assertGreater(apps["rt_dbscan"]["min_speedup_vs_prepared_cupy_grid"], 3.5)
        self.assertEqual("cupy", apps["barnes_hut"]["selected_vector_sum_partner"])
        self.assertEqual(
            "current_path_acceptable_but_rows_overlay_deferred",
            apps["spatial_rayjoin"]["performance_status"],
        )

    def test_front_door_remains_generic_and_bounded(self) -> None:
        text = FRONT_DOOR_REPORT.read_text(encoding="utf-8")

        self.assertIn("run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d", text)
        self.assertIn("hit_stream_grouped_ray_id_primitive_i64", text)
        self.assertIn("event ordered", text)
        self.assertIn("not a public speedup claim", text)
        self.assertIn("true-zero-copy", text)

    def test_readiness_index_points_to_goal2945_packet(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        runner = packet["current_canonical_runner"]

        self.assertIn("goal2945_current_packet_after_hit_stream_front_door_pod", runner["summary_path"])
        self.assertEqual("pass", runner["status"])
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2945_current_packet_after_hit_stream_front_door_2026-06-01.md"
            ]
        )
        self.assertIn("keep_goal2945_current_packet_after_hit_stream_front_door_green", packet["allowed_next_actions"])
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])

    def test_report_documents_boundary_and_next_runtime_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2945",
            "generic event-ordered RT hit-stream front door",
            "performance targets: `[]`",
            "payload-mapped continuation",
            "App terms and app-specific logic",
            "not a v2.5 release authorization",
            "true-zero-copy claim",
            "fresh 3-AI release",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
