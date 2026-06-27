import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_grouped_reduction_device_column_m7_final_review_packet.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixGroupedReductionDeviceColumnM7FinalReviewPacketTest(unittest.TestCase):
    def payload(self):
        return json.loads(PACKET_JSON.read_text(encoding="utf-8"))

    def test_packet_is_row_scoped_m7_not_release(self):
        payload = self.payload()
        self.assertEqual(
            payload["status"],
            "grouped_reduction_device_column_scoped_row_evidence_not_release",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertTrue(payload["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertTrue(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows"], 2)
        self.assertEqual(
            payload["current_packet_external_review_status"],
            "claude_external_approve_with_required_fixes_p1_applied_2026-06-22",
        )
        self.assertEqual(
            payload["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete_after_subagent_gap_supersession_2026-06-22",
        )
        self.assertEqual(
            payload["packet_path"],
            "docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md",
        )

    def test_two_exact_rows_are_defined_and_promoted(self):
        payload = self.payload()
        rows = {row["row_id"]: row for row in payload["candidate_rows"]}
        self.assertEqual(
            set(rows),
            {
                "grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups",
                "grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups",
            },
        )
        for row in rows.values():
            self.assertEqual(row["generic_capability"], "grouped_reduction")
            self.assertEqual(row["operation"], "prepared_grouped_sum_i64")
            self.assertEqual(row["ray_batch_layout"], "cupy_device_columns")
            self.assertEqual(row["warmup"], 3)
            self.assertEqual(row["repeat"], 100)
            self.assertTrue(row["same_contract"])
            self.assertTrue(row["all_match_cpu_reference"])
            self.assertFalse(row["app_specific_native_engine_logic_allowed"])
            self.assertFalse(row["native_engine_customization"])
            self.assertFalse(row["partner_continuation_required"])
            self.assertFalse(row["true_zero_copy_authorized"])
            self.assertEqual(row["host_packed_ray_count_device_route"], 0)
            self.assertFalse(row["replaces_existing_m7_row"])
            self.assertEqual(
                row["existing_m7_row_retained"],
                "grouped_reduction_sum_scalar_broadcast_repeat100_262144",
            )
            self.assertEqual(
                row["local_gate_reading"],
                "m7_row_evidence_scoped_not_release_after_claude_codex_consensus",
            )
            self.assertTrue(row["m7_promoted"])

    def test_speedups_are_material_and_phase_attributed(self):
        payload = self.payload()
        self.assertGreater(
            payload["summary"]["min_host_packed_over_device_columns_cold_plus_loop_speedup"],
            3.0,
        )
        self.assertGreater(
            payload["summary"]["min_embree_over_optix_device_columns_cold_plus_loop_speedup"],
            100.0,
        )
        row_524k = next(row for row in payload["candidate_rows"] if row["generated_rows"] == 524288)
        self.assertGreater(row_524k["optix_host_packed_over_device_columns_cold_prepare_speedup"], 200.0)
        self.assertGreater(row_524k["optix_host_packed_over_device_columns_workload_build_speedup"], 1000.0)
        self.assertGreater(row_524k["optix_host_packed_over_device_columns_prepared_ray_batch_speedup"], 8.0)
        self.assertTrue(row_524k["phase_attribution"]["not_only_ray_batch_prepare"])
        self.assertIn("workload_build_sec", row_524k["phase_attribution"]["cold_prepare_speedup_includes"])

    def test_source_provenance_and_boundaries_are_present(self):
        payload = self.payload()
        provenance = payload["source_provenance"]
        self.assertTrue(provenance["source_manifest_is_traceability_record"])
        self.assertTrue(provenance["git_head_missing_acknowledged"])
        self.assertIn("source_manifest.sha256", provenance["source_manifest_path"])
        self.assertIn("fatal: not a git repository", provenance["raw_payload_git_head_values"][0])
        self.assertTrue(provenance["source_manifest_does_not_cover_orchestration_wrappers"])
        self.assertEqual(
            provenance["manifested_benchmark_entry_point"],
            "scripts/v3_0_m28_raydb_prepared_grouped_refresh.py",
        )
        self.assertTrue(provenance["raw_json_version_confirms_manifested_entry_point"])
        self.assertIn(
            "scripts/v3_phoenix_grouped_reduction_device_column_pod_evidence.py",
            provenance["orchestration_wrappers_not_manifested"],
        )
        self.assertIn("future reruns should expand the manifest scope", provenance["source_manifest_scope_p1_acknowledgement"])
        boundaries = "\n".join(payload["remaining_non_release_boundaries"])
        self.assertIn("release_authorized remains false", boundaries)
        self.assertIn("true_zero_copy_authorized remains false", boundaries)
        forbidden = "\n".join(payload["forbidden_public_wording"])
        self.assertIn("V3 is 218x faster", forbidden)
        self.assertIn("pure backend-only ratios", forbidden)

    def test_markdown_preserves_review_state(self):
        text = PACKET_MD.read_text(encoding="utf-8")
        for phrase in [
            "claude_external_approve_with_required_fixes_p1_applied_2026-06-22",
            "phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md",
            "claude_codex_consensus_complete_after_subagent_gap_supersession_2026-06-22",
            "Phoenix scoped row-evidence rows from this packet: 2",
            "workload-build/input-path collapse",
            "pure backend-only ratios",
            "Embree remains the host-packed route while the OptiX candidate uses cupy_device_columns",
            "source_manifest.sha256",
            "fatal: not a git repository",
            "Manifest scope note",
            "orchestration wrappers",
            "claude_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-22.md",
            "codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_claude_supersession_consensus_2026-06-22.md",
            "Prior substitute review, kept as historical but superseded",
            "Was I foolish?",
        ]:
            self.assertIn(phrase, text)

    def test_script_rebuilds_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            md_out = Path(tmp) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.payload())
            self.assertIn(
                "Phoenix V3 Grouped-Reduction Device-Column M7 Final Review Packet",
                md_out.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
