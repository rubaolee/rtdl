from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts import v3_phoenix_aabb_native_query_handle_stability_evidence as stability


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_stability_evidence_2026-06-21.json"
PACKET_MD = PACKET_JSON.with_suffix(".md")
SCRIPT = ROOT / "scripts/v3_phoenix_aabb_native_query_handle_stability_evidence.py"


class V3PhoenixAabbNativeQueryHandleStabilityEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not PACKET_JSON.exists() or not PACKET_MD.exists():
            subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_stability_packet_closes_only_fresh_run_blocker(self) -> None:
        packet = self.packet
        self.assertEqual(packet["status"], "aabb_native_query_handle_stability_pass_not_m7")
        self.assertTrue(packet["fresh_run_stability_closes_blocker"])
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertFalse(packet["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(packet["m7_promotion_authorized"])
        self.assertEqual(packet["m7_qualified_release_rows_added"], 0)
        self.assertEqual(packet["failed_checks"], [])

    def test_six_fresh_runs_clear_material_floor_at_both_scales(self) -> None:
        packet = self.packet
        self.assertEqual(len(packet["observed_rows"]), 6)
        self.assertEqual(set(packet["by_scale"]), {"32768", "65536"})
        for item in packet["by_scale"].values():
            self.assertEqual(item["sample_count"], 3)
            self.assertGreaterEqual(
                item["weakest_cold_plus_collect_wall_speedup"],
                packet["material_wall_speedup_floor"],
            )
            self.assertGreater(item["weakest_runner_wall_speedup"], 1.0)
        self.assertGreater(packet["stability_summary"]["weakest_cold_plus_collect_wall_speedup"], 1.6)

    def test_rows_keep_correctness_and_native_cache_observed(self) -> None:
        for row in self.packet["observed_rows"]:
            self.assertTrue(row["runner_completed"])
            self.assertEqual(row["run_errors"], {})
            self.assertTrue(row["matches_cpu_reference"])
            self.assertTrue(row["complete_candidate_coverage"])
            self.assertTrue(row["optix_native_cache_observed"])

    def test_markdown_states_boundary(self) -> None:
        markdown = self.markdown
        self.assertIn("not release", markdown)
        self.assertIn("Weakest cold-plus-collect wall speedup", markdown)
        self.assertIn("M7 promotion authorized: `false`", markdown)
        self.assertIn("Goal-Level Decision Self-Audit", markdown)

    def test_script_rebuilds_checked_in_packet(self) -> None:
        before_json = PACKET_JSON.read_text(encoding="utf-8")
        before_md = PACKET_MD.read_text(encoding="utf-8")
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertEqual(PACKET_JSON.read_text(encoding="utf-8"), before_json)
        self.assertEqual(PACKET_MD.read_text(encoding="utf-8"), before_md)


if __name__ == "__main__":
    unittest.main()
