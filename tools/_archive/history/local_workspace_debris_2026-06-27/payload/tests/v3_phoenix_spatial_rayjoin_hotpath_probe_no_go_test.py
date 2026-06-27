from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/v3_phoenix_spatial_rayjoin_hotpath_probe_no_go.py"
PACKET_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_hotpath_probe_no_go_2026-06-21.json"
PACKET_MD = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_hotpath_probe_no_go_2026-06-21.md"
CLAUDE_ATTEMPT = (
    ROOT / "docs/reviews/claude_phoenix_v3_spatial_hotpath_probe_no_go_review_2026-06-21.md"
)
GEMINI_ATTEMPT = (
    ROOT / "docs/reviews/gemini_phoenix_v3_spatial_hotpath_probe_no_go_review_attempt_2026-06-21.md"
)
EXTERNAL_BLOCKED = (
    ROOT / "docs/reviews/external_ai_blocked_phoenix_v3_spatial_hotpath_probe_no_go_2026-06-21.md"
)
CODEX_INTERIM = (
    ROOT / "docs/reviews/codex_phoenix_v3_spatial_hotpath_probe_no_go_interim_consensus_2026-06-21.md"
)


class V3PhoenixSpatialRayJoinHotpathProbeNoGoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_blocks_m7_and_public_claims(self) -> None:
        packet = self.packet
        self.assertEqual(packet["status"], "spatial_rayjoin_hotpath_probe_no_go_author_gap_not_closed")
        self.assertEqual(packet["generic_capability"], "point_location_topology_stream")
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["m7_promotion_authorized"])
        self.assertEqual(packet["m7_qualified_release_rows_added"], 0)
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertFalse(packet["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(packet["paper_reproduction_claim_authorized"])
        self.assertEqual(packet["failed_checks"], [])

    def test_best_legal_route_is_exact_but_still_slower_than_author(self) -> None:
        best = self.packet["best_legal_route"]
        gap = self.packet["same_dataset_author_gap"]
        self.assertEqual(best["count_mode"], "relation_status_corrected_executor_validated")
        self.assertEqual(best["point_order_mode"], "y_then_x")
        self.assertEqual(best["row_count"], 47262)
        self.assertTrue(best["row_count_consistent"])
        self.assertGreater(best["prepared_query_ms"], 5.0)
        self.assertLess(best["prepared_query_ms"], 6.0)
        self.assertAlmostEqual(gap["author_query_ms"], 1.86566)
        self.assertGreater(gap["rayjoin_author_speedup_vs_best_legal_rtdl_hotpath"], 2.8)
        self.assertIn("not closed", gap["interpretation"])

    def test_device_filtered_route_is_rejected_for_exactness(self) -> None:
        rejected = self.packet["device_filtered_rejected_route"]
        self.assertEqual(rejected["count_mode"], "device_filtered_prepared_points_validated")
        self.assertEqual(rejected["failure_class"], "validated_candidate_exactness_mismatch")
        self.assertEqual(rejected["observed_count"], 47570)
        self.assertEqual(rejected["exact_count"], 47262)
        self.assertEqual(rejected["candidate_minus_exact"], 308)
        self.assertTrue(rejected["excluded_from_m7"])
        self.assertTrue(
            all(row["count_mode"] != rejected["count_mode"] for row in self.packet["route_rows"])
        )

    def test_route_sweep_covers_expected_orders_and_executor(self) -> None:
        route_keys = {(row["count_mode"], row["point_order_mode"]) for row in self.packet["route_rows"]}
        self.assertIn(("relation_status_corrected_executor_validated", "natural"), route_keys)
        self.assertIn(("relation_status_corrected_executor_validated", "x_then_y"), route_keys)
        self.assertIn(("relation_status_corrected_executor_validated", "y_then_x"), route_keys)
        self.assertIn(("relation_status_corrected_executor_validated", "morton_xy"), route_keys)
        self.assertIn(("exact_prepared_points_executor", "y_then_x"), route_keys)
        exact_executor = [
            row
            for row in self.packet["route_rows"]
            if row["count_mode"] == "exact_prepared_points_executor"
        ][0]
        self.assertGreater(exact_executor["prepared_query_ms"], 20.0)

    def test_markdown_states_no_go_boundary(self) -> None:
        markdown = self.markdown
        self.assertIn("Spatial RayJoin Hotpath Probe No-Go", markdown)
        self.assertIn("does not promote M7", markdown)
        self.assertIn("RayJoin author speedup vs best legal RTDL hotpath", markdown)
        self.assertIn("`2.898x`", markdown)
        self.assertIn("Observed count: `47570`", markdown)
        self.assertIn("Exact count: `47262`", markdown)
        self.assertIn("Goal-Level Decision Self-Audit", markdown)

    def test_external_ai_blocked_records_are_explicit_not_2ai_consensus(self) -> None:
        claude = CLAUDE_ATTEMPT.read_text(encoding="utf-8")
        gemini = GEMINI_ATTEMPT.read_text(encoding="utf-8")
        blocked = EXTERNAL_BLOCKED.read_text(encoding="utf-8")
        codex = CODEX_INTERIM.read_text(encoding="utf-8")
        self.assertIn("claude_unavailable_session_limit_not_review", claude)
        self.assertIn("No Claude review verdict is claimed", claude)
        self.assertIn("gemini_unavailable_ineligible_tier_not_review", gemini)
        self.assertIn("No Gemini review verdict is claimed", gemini)
        self.assertIn("external_ai_review_blocked_not_2ai_consensus", blocked)
        self.assertIn("This is not a completed 2-AI consensus", codex)

    def test_script_rebuilds_checked_in_packet(self) -> None:
        before_json = PACKET_JSON.read_text(encoding="utf-8")
        before_md = PACKET_MD.read_text(encoding="utf-8")
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertEqual(PACKET_JSON.read_text(encoding="utf-8"), before_json)
        self.assertEqual(PACKET_MD.read_text(encoding="utf-8"), before_md)


if __name__ == "__main__":
    unittest.main()
