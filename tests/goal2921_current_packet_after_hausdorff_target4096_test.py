from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2921_current_packet_after_hausdorff_target4096_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2921_current_packet_after_hd4096_pod"
SUMMARY = ARTIFACT_DIR / "goal2855_summary.json"
TRIAGE = ARTIFACT_DIR / "goal2921_triage.json"


class Goal2921CurrentPacketAfterHausdorffTarget4096Test(unittest.TestCase):
    def test_packet_passes_cleanly_at_hausdorff_target4096_commit(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertEqual("fe628f4faec8e7d43521f11afd395b29462fba8b", summary["source_commit"])
        self.assertEqual({}, summary["dirty_artifacts"])
        self.assertEqual({}, summary["claim_boundary_violations"])
        self.assertFalse(summary["claim_boundary"]["v2_5_release_authorized"])

    def test_hausdorff_row_uses_target4096_and_is_green(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "goal2801_hausdorff_xhd.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertTrue(payload["matches_exact_baseline"])
        self.assertTrue(payload["rtdl"]["uses_rt_cores"])
        self.assertEqual(4096, payload["rtdl"]["reduced_target_points_per_group"])
        self.assertLess(payload["rtdl_over_cupy_grid_elapsed_ratio"], 1.0)
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["native_engine_customization"])

    def test_triage_has_no_current_performance_targets(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))
        apps = {row["app"]: row for row in triage["apps"]}

        self.assertEqual("pass", triage["status"])
        self.assertEqual([], triage["performance_targets"])
        self.assertIsNone(triage["top_priority"])
        self.assertEqual("current_path_acceptable", apps["hausdorff_xhd"]["performance_status"])
        self.assertLess(apps["hausdorff_xhd"]["rtdl_over_cupy_ratio"], 1.0)
        self.assertEqual("current_path_acceptable", apps["rtnn"]["performance_status"])
        self.assertGreater(apps["rtnn"]["min_cupy_over_rtdl_ratio"], 1.0)
        self.assertEqual("torch", apps["barnes_hut"]["selected_vector_sum_partner"])

    def test_toolchain_metadata_survives_packet_rerun(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        toolchain = summary["runner_metadata"]["toolchain"]

        self.assertEqual("rtdl.goal2916.toolchain_provenance.v1", toolchain["metadata_version"])
        self.assertEqual("compute_86", toolchain["rtdl_optix_ptx_arch"])
        self.assertEqual("nvcc", toolchain["rtdl_optix_ptx_compiler"])
        self.assertTrue(toolchain["rtdl_optix_library_exists"])
        self.assertTrue(toolchain["optix_header_exists"])
        self.assertFalse(toolchain["claim_boundary"]["compiler_fairness_claim_authorized"])

    def test_readiness_index_points_to_goal2921_packet(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        runner = packet["current_canonical_runner"]

        self.assertIn("goal2921_current_packet_after_hd4096_pod", runner["summary_path"])
        self.assertEqual("pass", runner["status"])
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])

    def test_report_documents_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2921",
            "performance targets: `[]`",
            "target `4096`",
            "RTDL/CuPy ratio `0.915x`",
            "not a v2.5 release authorization",
            "second-architecture or multivendor",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
