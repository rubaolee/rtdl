from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2934_current_packet_after_cupy_vector_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2934_current_packet_after_cupy_vector_pod"
SUMMARY = ARTIFACT_DIR / "goal2855_summary.json"
TRIAGE = ARTIFACT_DIR / "goal2934_triage.json"


class Goal2934CurrentPacketAfterCupyVectorTest(unittest.TestCase):
    def test_packet_passes_cleanly_after_cupy_vector_selection(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertEqual("34b4f241e9bc235a4ffcd65a04067cc63211eea1", summary["source_commit"])
        self.assertTrue(summary["source_commit_consistent"])
        self.assertEqual({}, summary["dirty_artifacts"])
        self.assertEqual({}, summary["claim_boundary_violations"])
        self.assertFalse(summary["claim_boundary"]["v2_5_release_authorized"])
        self.assertFalse(summary["claim_boundary"]["public_speedup_claim_authorized"])

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

    def test_barnes_hut_selects_cupy_for_measured_vector_continuation(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "goal2803_barnes_hut.json").read_text(encoding="utf-8"))
        vector = payload["vector_sum"]

        self.assertEqual("pass", payload["status"])
        self.assertTrue(all(row["rows_match_between_backends"] for row in payload["membership_rows"]))
        self.assertTrue(all(row["optix_rt_core_accelerated"] for row in payload["membership_rows"]))
        self.assertGreater(payload["max_optix_membership_speedup_vs_embree"], 100.0)
        self.assertEqual("cupy", vector["selected_partner"])
        self.assertTrue(vector["cupy_matches_torch"])
        self.assertLess(vector["cupy_over_torch_ratio"], 0.5)
        self.assertGreater(vector["triton_over_torch_ratio"], 1.0)
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["native_engine_customization"])

    def test_other_tier_b_rows_remain_current_path_acceptable(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))
        apps = {row["app"]: row for row in triage["apps"]}

        self.assertEqual("pass", triage["status"])
        self.assertEqual([], triage["performance_targets"])
        self.assertIsNone(triage["top_priority"])
        self.assertEqual("current_path_acceptable", apps["rtnn"]["performance_status"])
        self.assertGreater(apps["rtnn"]["min_cupy_over_rtdl_ratio"], 1.0)
        self.assertEqual("current_path_acceptable_near_parity", apps["hausdorff_xhd"]["performance_status"])
        self.assertLess(apps["hausdorff_xhd"]["rtdl_over_cupy_ratio"], 1.1)
        self.assertEqual("current_path_acceptable", apps["rt_dbscan"]["performance_status"])
        self.assertGreater(apps["rt_dbscan"]["min_speedup_vs_prepared_cupy_grid"], 4.0)
        self.assertEqual("cupy", apps["barnes_hut"]["selected_vector_sum_partner"])

    def test_readiness_index_points_to_goal2934_packet(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        runner = packet["current_canonical_runner"]

        self.assertIn("goal2934_current_packet_after_cupy_vector_pod", runner["summary_path"])
        self.assertEqual("pass", runner["status"])
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2934_current_packet_after_cupy_vector_2026-06-01.md"
            ]
        )
        self.assertIn("keep_goal2934_current_packet_after_cupy_vector_green", packet["allowed_next_actions"])
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])

    def test_report_documents_boundaries_and_partner_selection_lesson(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2934",
            "CuPy selected for vector-sum continuation",
            "performance targets: `[]`",
            "RTDL/CuPy ratio `1.012x`",
            "RTDL/OptiX provides generic RT traversal",
            "not a v2.5 release authorization",
            "automatic CuPy-selection claim",
            "fresh 3-AI release consensus",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
