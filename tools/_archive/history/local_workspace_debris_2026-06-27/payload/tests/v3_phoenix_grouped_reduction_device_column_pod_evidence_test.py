import json
import unittest
from pathlib import Path

from scripts import v3_phoenix_grouped_reduction_device_column_pod_evidence as evidence


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.json"
)
PACKET_MD = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.md"
)
EVIDENCE_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_grouped_reduction_device_columns_20260621"
)


class V3PhoenixGroupedReductionDeviceColumnPodEvidenceTest(unittest.TestCase):
    def payload(self):
        return json.loads(PACKET_JSON.read_text(encoding="utf-8"))

    def test_packet_is_pending_review_not_release(self):
        payload = self.payload()
        self.assertEqual(
            payload["status"],
            "grouped_reduction_device_column_ray_batch_pod_evidence_pending_2ai_not_m7",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["m7_promoted"])
        self.assertTrue(payload["m7_reopen_candidate_pending_2ai_review"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(payload["checks"]["source_manifest_bound_to_packet"])
        self.assertTrue(payload["checks"]["raw_git_head_gap_acknowledged"])
        self.assertTrue(payload["checks"]["exact_row_identities_defined"])

    def test_device_column_route_is_real_and_removes_host_packed_rays(self):
        payload = self.payload()
        self.assertEqual(len(payload["scales"]), 2)
        self.assertTrue(payload["summary"]["all_cpu_reference_match"])
        self.assertTrue(payload["summary"]["all_host_packed_rays_eliminated_on_device_route"])
        for scale in payload["scales"]:
            self.assertIn("cupy_device_columns", scale["candidate_row_id"])
            self.assertEqual(scale["exact_row_identity"]["ray_batch_layout"], "cupy_device_columns")
            self.assertFalse(scale["exact_row_identity"]["replaces_existing_m7_row"])
            self.assertEqual(scale["exact_row_identity"]["warmup"], 3)
            self.assertEqual(scale["exact_row_identity"]["repeat"], 100)
            self.assertIn("prepared grouped_sum only", scale["exact_row_identity"]["scope"])
            device = scale["optix_device_columns"]
            host = scale["optix_host_packed"]
            self.assertEqual(device["layout"], "cupy_device_columns")
            self.assertEqual(device["created_from"], "partner_device_columns")
            self.assertTrue(device["native_device_column_path_used"])
            self.assertEqual(device["host_packed_ray_count"], 0)
            self.assertEqual(host["layout"], "host_packed")
            self.assertEqual(host["host_packed_ray_count"], scale["logical_ray_count"])
            self.assertTrue(scale["logical_ray_counts_match"])
            self.assertTrue(scale["all_match_cpu_reference"])

    def test_source_manifest_covers_missing_git_head(self):
        payload = self.payload()
        provenance = payload["source_provenance"]
        self.assertTrue(provenance["source_manifest_is_traceability_record"])
        self.assertTrue(provenance["git_head_missing_acknowledged"])
        self.assertFalse(provenance["remote_worktree_git_head_available"])
        self.assertIn("source_manifest.sha256", provenance["source_manifest_path"])
        self.assertGreaterEqual(len(provenance["source_manifest_entries"]), 4)
        self.assertIn("not a git checkout", provenance["provenance_interpretation"])
        for value in provenance["raw_payload_git_head_values"]:
            self.assertIn("fatal: not a git repository", value)

    def test_speedups_are_material_not_one_percent(self):
        payload = self.payload()
        self.assertGreater(
            payload["summary"]["min_host_packed_over_device_columns_cold_prepare_speedup"],
            5.0,
        )
        self.assertGreater(
            payload["summary"]["min_host_packed_over_device_columns_cold_plus_loop_speedup"],
            3.0,
        )
        self.assertGreater(
            payload["summary"]["min_embree_over_optix_device_columns_hot_query_speedup"],
            100.0,
        )
        self.assertGreater(
            payload["summary"]["min_embree_over_optix_device_columns_cold_plus_loop_speedup"],
            100.0,
        )
        scale_524k = next(scale for scale in payload["scales"] if scale["generated_rows"] == 524288)
        self.assertGreater(
            scale_524k["optix_host_packed_over_device_columns_workload_build_speedup"],
            1000.0,
        )
        self.assertGreater(
            scale_524k["optix_host_packed_over_device_columns_prepared_ray_batch_speedup"],
            8.0,
        )
        self.assertTrue(scale_524k["phase_attribution"]["not_only_ray_batch_prepare"])
        self.assertIn("workload_build_sec", scale_524k["phase_attribution"]["cold_prepare_speedup_includes"])

    def test_pre_dedup_hits_are_explained_without_blocking_cpu_parity(self):
        for scale in self.payload()["scales"]:
            hits = scale["pre_dedup_hit_events"]
            self.assertGreater(hits["optix_device_columns"], 0)
            self.assertGreater(hits["embree"], 0)
            self.assertNotEqual(hits["embree"], hits["optix_device_columns"])
            self.assertIn("all rows match the CPU reference", hits["interpretation"])
            self.assertTrue(scale["all_match_cpu_reference"])

    def test_evidence_artifacts_are_present(self):
        for name in [
            "grouped_sum_device_columns_262144_repeat100.json",
            "grouped_sum_host_packed_optix_262144_repeat100.json",
            "grouped_sum_device_columns_524288_repeat100.json",
            "grouped_sum_host_packed_optix_524288_repeat100.json",
            "run_device_columns_repeat100.log",
            "run_device_columns_repeat100.status",
            "nvidia-smi.txt",
            "gpu_env_gate.json",
            "optix_hardware_gate.json",
            "source_manifest.sha256",
        ]:
            self.assertTrue((EVIDENCE_DIR / name).exists(), name)
        self.assertEqual(
            (EVIDENCE_DIR / "run_device_columns_repeat100.status").read_text(encoding="utf-8").strip(),
            "0",
        )

    def test_markdown_keeps_public_boundary(self):
        text = PACKET_MD.read_text(encoding="utf-8")
        for phrase in [
            "pending 2-AI review, not M7 promotion",
            "true_zero_copy_authorized: false",
            "m7_promoted: false",
            "This proves true zero-copy",
            "This is an M7-qualified row before 2-AI review",
            "host-packed ray materialization can",
            "dominate the story",
            "Host/device cold prepare",
            "Candidate Exact Rows",
            "Source manifest entries",
            "fatal: not a git repository",
            "workload-build/input-path collapse",
            "Pre-Dedup Hit Events",
            "grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups",
            "grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups",
        ]:
            self.assertIn(phrase, text)

    def test_builder_matches_checked_in_packet(self):
        self.assertEqual(evidence.build_payload(), self.payload())


if __name__ == "__main__":
    unittest.main()
