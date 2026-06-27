from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.json"
)
PACKET_MD = (
    ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.md"
)
SCRIPT = ROOT / "scripts/v3_phoenix_spatial_rayjoin_relation_status_exact_f64_review_gate.py"


class V3PhoenixSpatialRelationStatusExactF64ReviewGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_review_gate_blocks_m7_despite_material_internal_delta(self) -> None:
        packet = self.packet
        self.assertEqual(packet["status"], "spatial_rayjoin_relation_status_exact_f64_review_blocked_not_m7")
        self.assertEqual(packet["intake_status"], "spatial_rayjoin_relation_status_exact_f64_device_scalar_count_intake_not_m7")
        self.assertEqual(packet["external_review_status"], "blocked_no_external_ai_verdict")
        self.assertEqual(packet["codex_review_status"], "approve_as_intake_blocks_m7")
        self.assertFalse(packet["m7_candidate_reopen_authorized"])
        self.assertFalse(packet["m7_promotion_authorized"])
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertFalse(packet["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(packet["rtdl_beats_rayjoin_claim_authorized"])
        self.assertGreater(packet["internal_material_delta_vs_exact_executor"]["prepared_query_speedup"], 3.6)
        self.assertGreater(packet["internal_material_delta_vs_exact_executor"]["runner_wall_speedup"], 1.4)

    def test_required_blockers_cover_review_author_after_adverse_subset_closure(self) -> None:
        blockers = set(self.packet["required_blockers_before_m7"])
        self.assertIn("external_ai_review_missing", blockers)
        self.assertIn("codex_consensus_response_missing_after_external_review", blockers)
        self.assertNotIn("same_dataset_rayjoin_author_timing_basis_missing", blockers)
        self.assertIn("rayjoin_author_result_count_not_printed_or_public_scope_review_missing", blockers)
        self.assertIn("rayjoin_author_query_faster_than_rtdl_exact_f64_query", blockers)
        self.assertNotIn("adverse_subset_parity_missing", blockers)
        self.assertIn("public_wording_review_missing", blockers)
        self.assertTrue(self.packet["adverse_subset_parity_closed"])
        self.assertEqual(
            self.packet["adverse_subset_packet"],
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_adverse_subset_2026-06-21.json",
        )
        adverse_subset = json.loads((ROOT / self.packet["adverse_subset_packet"]).read_text(encoding="utf-8"))
        self.assertEqual(
            adverse_subset["status"],
            "spatial_rayjoin_relation_status_exact_f64_adverse_subset_parity_pass_not_m7",
        )
        self.assertEqual(adverse_subset["m7_qualified_release_rows_added"], 0)
        self.assertFalse(adverse_subset["release_authorized"])

    def test_author_timing_basis_is_structured_present_and_still_blocks_m7(self) -> None:
        author = self.packet["author_timing_basis"]
        self.assertEqual(author["status"], "present_but_not_m7_author_query_faster_count_not_printed")
        self.assertTrue(author["same_dataset_author_timing_basis_present"])
        self.assertEqual(author["current_candidate"]["exact_count"], 47262)
        self.assertEqual(
            author["current_candidate"]["comparison_basis"],
            "RTDL exact-f64 native scalar-count versus prior RTDL exact executor",
        )
        self.assertGreater(
            author["current_candidate"]["prepared_query_speedup_vs_prior_rtdl_exact_executor"],
            3.6,
        )
        same = author["same_dataset_author_evidence"]
        self.assertEqual(
            same["source"],
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.json",
        )
        self.assertEqual(same["status"], "spatial_rayjoin_same_county_author_timing_present_not_m7")
        self.assertAlmostEqual(same["author_query_ms"], 1.86566)
        self.assertEqual(same["author_query_point_count"], 342738)
        self.assertFalse(same["author_result_count_printed"])
        self.assertFalse(same["author_result_count_parity_verified"])
        self.assertGreater(same["rayjoin_author_query_speedup_vs_rtdl_exact_f64_prepared_query"], 3.0)
        prior = author["prior_author_evidence"]
        self.assertEqual(
            prior["source"],
            "docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620/m5_pip_point_location_parity_filtered_100k/summary.json",
        )
        self.assertEqual(prior["query_count"], 100000)
        self.assertEqual(prior["query_generation"], "backend_parity_filtered_random_bbox")
        self.assertFalse(prior["direct_current_packet_comparison_authorized"])
        self.assertGreater(prior["rayjoin_rt_speedup_vs_rtdl_optix_native_traversal"], 3.0)
        self.assertIn("same-dataset RayJoin author timing basis now exists", author["why_not_m7"])
        self.assertIn("RayJoin author Query is faster", author["why_not_m7"])
        self.assertTrue(
            any("external public wording review" in item for item in author["required_evidence_before_m7"])
        )
        self.assertFalse(self.packet["rtdl_beats_rayjoin_claim_authorized"])

    def test_review_records_make_failed_external_attempts_visible(self) -> None:
        records = self.packet["review_records"]
        for key in (
            "call_for_review",
            "claude_unavailable",
            "gemini_attempt",
            "external_ai_blocked",
            "codex_blocking_review",
        ):
            self.assertIn(key, records)
            self.assertTrue((ROOT / records[key]).exists(), key)
        gemini_text = (ROOT / records["gemini_attempt"]).read_text(encoding="utf-8")
        self.assertIn("IneligibleTierError", gemini_text)
        claude_text = (ROOT / records["claude_unavailable"]).read_text(encoding="utf-8")
        self.assertIn("No Claude review verdict is claimed", claude_text)

    def test_markdown_boundary_is_clear(self) -> None:
        markdown = self.markdown
        self.assertIn("This packet intentionally blocks M7 promotion.", markdown)
        self.assertIn("`external_ai_review_missing`", markdown)
        self.assertIn("Adverse-Subset Parity", markdown)
        self.assertIn("Closed: `true`", markdown)
        self.assertIn("Prepared-query speedup versus prior RTDL exact executor: `3.680x`", markdown)
        self.assertIn("Author Timing Basis", markdown)
        self.assertIn("Same-dataset author timing present: `true`", markdown)
        self.assertIn("Same-dataset author Query timer: `1.865660 ms`", markdown)
        self.assertIn("RayJoin author Query speedup vs RTDL exact-f64 prepared query", markdown)
        self.assertIn("Prior author query count: `100000`", markdown)
        self.assertIn("same-dataset RayJoin author timing basis now exists", markdown)
        self.assertIn("not RayJoin author, paper", markdown)
        self.assertIn("Goal-Level Decision Self-Audit", markdown)

    def test_script_rebuilds_checked_in_gate(self) -> None:
        before_json = PACKET_JSON.read_text(encoding="utf-8")
        before_md = PACKET_MD.read_text(encoding="utf-8")
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertEqual(PACKET_JSON.read_text(encoding="utf-8"), before_json)
        self.assertEqual(PACKET_MD.read_text(encoding="utf-8"), before_md)


if __name__ == "__main__":
    unittest.main()
