import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from examples.current.research_benchmarks.contact_manifold import (
    rtdl_contact_manifold_benchmark_app as contact,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_aabb_prepare_reuse_contract.py"
PACKET_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_aabb_prepare_reuse_contract_2026-06-21.json"
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixAabbPrepareReuseContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_is_contract_candidate_not_m7(self):
        payload = self.payload
        self.assertEqual(payload["status"], "aabb_prepare_reuse_contract_candidate_not_m7")
        self.assertEqual(payload["generic_capability"], "aabb_candidate_stream")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(
            payload["current_packet_external_review_status"],
            "claude_approve_with_amendments_p1_applied",
        )
        self.assertEqual(
            payload["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete_queue_advancement_not_m7",
        )
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_existing_aabb_row_and_contact_gap_are_preserved(self):
        row = self.payload["existing_m7_aabb_row"]
        self.assertEqual(row["row_id"], "aabb_candidate_stream_all_count_only_float32_32768")
        self.assertTrue(row["remains_the_only_aabb_m7_row"])
        gap = self.payload["current_contact_gap"]
        self.assertAlmostEqual(gap["query_optix_over_embree"], 1.2348474960917915)
        self.assertAlmostEqual(gap["collect_k_optix_over_embree"], 2.7590511659809116)
        self.assertLess(gap["prepare_aabb_index_optix_over_embree"], 1.0)
        self.assertLess(gap["wall_optix_over_embree"], 1.0)
        self.assertIn("preparation dominates", gap["reading"])

    def test_contact_payload_emits_generic_prepared_session_residency(self):
        payload = contact.aabb_broadphase_collect_k_payload(
            dataset="tiny",
            witness_capacity=3,
            discovery_backend="cpu",
            discovery_row_capacity=8,
            discovery_warmup_count=1,
            discovery_repeat_count=2,
        )
        metadata = payload["prepared_session_residency"]
        self.assertEqual(metadata["cache_key"]["primitive"], "aabb_index_query_2d")
        self.assertEqual(metadata["cache_key"]["backend"], "cpu")
        self.assertEqual(metadata["policy"]["cold_prepare_phase"], "prepare_aabb_index_2d")
        self.assertEqual(metadata["policy"]["hot_query_phase"], "emit_aabb_intersection_pair_rows_2d")
        self.assertEqual(metadata["explicit_reuse_helper"], "get_or_prepare_explicit_session")
        self.assertTrue(metadata["prepare_once_query_many_pattern"])
        self.assertTrue(metadata["query_reuse_observed_within_payload"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["app_specific_native_engine_logic_allowed"])

    def test_markdown_records_future_m7_requirements_and_decision_audit(self):
        for phrase in (
            "M7 rows added by this packet: 0",
            "This remains the only AABB M7 row.",
            "at least 32,768 indexed AABBs and 32,768 query AABBs",
            "Prepare indexed AABB scene once",
            "Show material OptiX wall win after prepare reuse",
            "It does not claim the current local smoke observed a prepared AABB execution path",
            "scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py",
            "runner_available_not_yet_rt_pod_evidence",
            "--dataset jittered_grid --grid-count 32768",
            "claude_approve_with_amendments_p1_applied",
            "claude_codex_consensus_complete_queue_advancement_not_m7",
            "Do not promote contact_manifold from this packet.",
            "Was I foolish?",
            "No. The current contact row is wall-slower",
        ):
            self.assertIn(phrase, self.text)

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
                    "--pretty",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            rebuilt = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(rebuilt["status"], self.payload["status"])
            self.assertEqual(rebuilt["current_contact_gap"], self.payload["current_contact_gap"])
            self.assertIn("AABB Prepare-Reuse Contract", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
