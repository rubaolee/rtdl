from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2917_current_packet_with_toolchain_provenance_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2917_current_packet_with_toolchain_pod"
SUMMARY = ARTIFACT_DIR / "goal2855_summary.json"
TRIAGE = ARTIFACT_DIR / "goal2917_triage.json"


class Goal2917CurrentPacketToolchainProvenanceTest(unittest.TestCase):
    def test_packet_passes_cleanly_with_toolchain_metadata(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertEqual("b21ff72dbfdb0653cace6cd9e353269ae75bcaf0", summary["source_commit"])
        self.assertEqual({}, summary["dirty_artifacts"])
        self.assertEqual({}, summary["claim_boundary_violations"])

        toolchain = summary["runner_metadata"]["toolchain"]
        self.assertEqual("rtdl.goal2916.toolchain_provenance.v1", toolchain["metadata_version"])
        self.assertEqual("compute_86", toolchain["rtdl_optix_ptx_arch"])
        self.assertEqual("nvcc", toolchain["rtdl_optix_ptx_compiler"])
        self.assertTrue(toolchain["optix_header_exists"])
        self.assertTrue(toolchain["rtdl_optix_library_exists"])
        self.assertIn("12.8", toolchain["nvcc_version"])

    def test_packet_records_partner_versions_without_promoting_claims(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        toolchain = summary["runner_metadata"]["toolchain"]

        self.assertEqual("3.4.0", toolchain["triton_version"])
        self.assertEqual("2.8.0+cu128", toolchain["torch_version"])
        self.assertEqual("14.1.0", toolchain["cupy_version"])
        self.assertEqual("0.65.1", toolchain["numba_version"])
        self.assertFalse(toolchain["claim_boundary"]["compiler_fairness_claim_authorized"])
        self.assertFalse(toolchain["claim_boundary"]["multivendor_claim_authorized"])
        self.assertFalse(summary["claim_boundary"]["v2_5_release_authorized"])

    def test_triage_has_no_current_performance_targets(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))
        apps = {row["app"]: row for row in triage["apps"]}

        self.assertEqual("pass", triage["status"])
        self.assertEqual([], triage["performance_targets"])
        self.assertIsNone(triage["top_priority"])
        self.assertEqual("current_path_acceptable", apps["rtnn"]["performance_status"])
        self.assertGreater(apps["rtnn"]["min_cupy_over_rtdl_ratio"], 1.0)
        self.assertEqual(
            "current_path_acceptable_near_parity",
            apps["hausdorff_xhd"]["performance_status"],
        )
        self.assertLess(apps["hausdorff_xhd"]["rtdl_over_cupy_ratio"], 1.1)
        self.assertEqual("torch", apps["barnes_hut"]["selected_vector_sum_partner"])

    def test_report_documents_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2917",
            "toolchain provenance",
            "performance targets: `[]`",
            "not a compiler fairness proof",
            "not a second-architecture or multivendor result",
            "not a v2.5 release authorization",
        ):
            self.assertIn(phrase, text)

    def test_readiness_index_points_to_toolchain_packet(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        runner = packet["current_canonical_runner"]

        self.assertIn("goal2917_current_packet_with_toolchain_pod", runner["summary_path"])
        self.assertEqual("pass", runner["status"])
        self.assertEqual(
            "rtdl.goal2916.toolchain_provenance.v1",
            runner["runner_metadata"]["toolchain"]["metadata_version"],
        )
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])


if __name__ == "__main__":
    unittest.main()
