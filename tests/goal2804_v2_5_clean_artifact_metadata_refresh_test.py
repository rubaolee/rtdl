from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2804_v2_5_clean_artifact_metadata_refresh_2026-05-31.md"

CLEAN_ARTIFACTS = {
    "rtnn": ROOT
    / "docs"
    / "reports"
    / "goal2800_pod_artifacts"
    / "rtnn_v25_live_ranked_summary_65536_clean_from_git.json",
    "hausdorff_xhd": ROOT
    / "docs"
    / "reports"
    / "goal2801_pod_artifacts"
    / "hausdorff_xhd_v25_canonical_entrypoint_4096_clean_from_git.json",
    "rt_dbscan": ROOT
    / "docs"
    / "reports"
    / "goal2802_pod_artifacts"
    / "rt_dbscan_v25_live_grouped_stream_32768_65536_131072_clean_from_git.json",
    "barnes_hut": ROOT
    / "docs"
    / "reports"
    / "goal2803_pod_artifacts"
    / "barnes_hut_v25_consolidated_harness_clean_from_git.json",
}


class Goal2804V25CleanArtifactMetadataRefreshTest(unittest.TestCase):
    def test_tier_b_clean_artifacts_record_source_metadata(self) -> None:
        for app_id, path in CLEAN_ARTIFACTS.items():
            with self.subTest(app_id=app_id):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["status"], "pass")
                self.assertRegex(payload["source_commit"], r"^[0-9a-f]{40}$")
                self.assertEqual(payload["source_dirty"], [])
                self.assertIn("NVIDIA", payload["gpu"])
                claim_boundary = payload["claim_boundary"]
                self.assertFalse(claim_boundary["public_speedup_claim_authorized"])
                self.assertFalse(claim_boundary["whole_app_speedup_claim_authorized"])
                self.assertFalse(claim_boundary["native_engine_customization"])

    def test_v2_5_manifest_is_full_and_not_a_release_gate(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        validation = rt.validate_v2_5_tiered_benchmark_manifest()

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(manifest["benchmark_app_count"], 10)
        self.assertEqual(manifest["tier_counts"], {"A": 3, "B": 4, "C": 3})
        self.assertFalse(manifest["public_speedup_claim_authorized"])
        self.assertFalse(manifest["true_zero_copy_claim_authorized"])
        for row in manifest["apps"]:
            with self.subTest(app_id=row["app_id"]):
                self.assertTrue(str(row["canonical_harness_status"]).startswith("ready"))
                self.assertNotIn("needs_", str(row["canonical_harness_status"]))

    def test_supporting_v2_5_boundaries_still_validate(self) -> None:
        self.assertEqual(rt.validate_v2_5_partner_continuation_contract()["status"], "accept")
        self.assertEqual(rt.validate_v2_5_partner_preview_gate()["status"], "accept")
        self.assertEqual(rt.validate_v2_5_partner_support_matrix()["status"], "accept")
        self.assertEqual(rt.validate_v2_5_partner_selection_guidance()["status"], "accept")
        self.assertEqual(rt.validate_v2_5_continuation_determinism_policies()["status"], "accept")

        seam = rt.describe_v2_5_hit_stream_neutral_seam_reconciliation()
        self.assertFalse(seam["torch_is_neutral_protocol"])
        self.assertFalse(seam["silent_cross_partner_torch_coercion_allowed"])
        self.assertIn("zero-copy proof", seam["claim_boundary"])
        self.assertIn("public speedup claim", seam["claim_boundary"])

    def test_report_records_metadata_refresh_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2804", text)
        self.assertIn("source_dirty: []", text)
        self.assertIn("not a release authorization", text)
        self.assertIn("not a public speedup claim", text)
        self.assertIn("not a true-zero-copy claim", text)


if __name__ == "__main__":
    unittest.main()
