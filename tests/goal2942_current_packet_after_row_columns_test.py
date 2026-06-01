from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2942_current_packet_after_row_columns_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2942_current_packet_after_row_columns_pod"
SUMMARY = ARTIFACT_DIR / "goal2855_summary.json"
TRIAGE = ARTIFACT_DIR / "goal2942_triage.json"
ROW_COLUMN_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2941_rayjoin_row_view_partner_columns_scale_probe_pod"
    / "goal2941_rayjoin_row_view_partner_columns_large.json"
)


class Goal2942CurrentPacketAfterRowColumnsTest(unittest.TestCase):
    def test_packet_passes_cleanly_after_row_column_bridge(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertEqual("74f6c66ef9cb44b0af0cec8c8c67113dffac2831", summary["source_commit"])
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
        self.assertEqual("current_path_acceptable_near_parity", apps["hausdorff_xhd"]["performance_status"])
        self.assertLess(apps["hausdorff_xhd"]["rtdl_over_cupy_ratio"], 1.1)
        self.assertEqual("current_path_acceptable", apps["rt_dbscan"]["performance_status"])
        self.assertGreater(apps["rt_dbscan"]["min_speedup_vs_prepared_cupy_grid"], 3.5)
        self.assertEqual("cupy", apps["barnes_hut"]["selected_vector_sum_partner"])

    def test_row_column_scale_evidence_remains_bounded_and_green(self) -> None:
        payload = json.loads(ROW_COLUMN_ARTIFACT.read_text(encoding="utf-8"))
        rows = {row["workload"]: row for row in payload["rows"]}

        self.assertEqual("pass", payload["status"])
        self.assertEqual("large", payload["scale"])
        self.assertEqual("cupy", payload["partner"])
        self.assertEqual(4096, rows["pip"]["expected_row_count"])
        self.assertEqual(65536, rows["lsi"]["expected_row_count"])
        self.assertEqual(262144, rows["overlay_seed"]["expected_row_count"])
        self.assertFalse(rows["pip"]["python_dict_row_materialization_used"])
        self.assertLess(rows["overlay_seed"]["typed_columns_over_count_only_ratio"], 1.05)
        self.assertLess(rows["lsi"]["typed_columns_over_count_only_ratio"], 1.35)
        self.assertFalse(payload["claim_boundary"]["device_resident_handoff_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])

    def test_readiness_index_points_to_goal2942_packet(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        runner = packet["current_canonical_runner"]

        self.assertIn("goal2942_current_packet_after_row_columns_pod", runner["summary_path"])
        self.assertEqual("pass", runner["status"])
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2942_current_packet_after_row_columns_2026-06-01.md"
            ]
        )
        self.assertIn("keep_goal2942_current_packet_after_row_columns_green", packet["allowed_next_actions"])
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])

    def test_report_documents_boundary_and_design_lesson(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2942",
            "typed partner-column bridge",
            "performance targets: `[]`",
            "Overlay seed rows | `262144`",
            "row-stream handoff is still",
            "not a v2.5 release authorization",
            "true-zero-copy claim",
            "user-requested release packet",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
