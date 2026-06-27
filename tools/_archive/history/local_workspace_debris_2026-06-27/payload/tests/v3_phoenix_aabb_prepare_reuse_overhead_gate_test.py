import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_aabb_prepare_reuse_overhead_gate.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_overhead_gate_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixAabbPrepareReuseOverheadGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_gate_blocks_m7_and_public_claims(self):
        payload = self.payload
        self.assertEqual(payload["status"], "aabb_prepare_reuse_overhead_gate_blocked_not_m7")
        self.assertEqual(payload["generic_capability"], "aabb_candidate_stream")
        self.assertFalse(payload["m7_candidate_reopen_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["full_contact_solver_claim_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_observed_ratios_explain_why_this_is_not_material_v3(self):
        rows = {row["grid_count"]: row for row in self.payload["observed_ratios"]}
        self.assertEqual(set(rows), {32_768, 65_536})
        self.assertAlmostEqual(rows[32_768]["cold_plus_collect_wall_speedup"], 1.1400086912394385)
        self.assertAlmostEqual(rows[65_536]["cold_plus_collect_wall_speedup"], 1.0870090497524356)
        self.assertLess(rows[65_536]["cold_plus_collect_wall_speedup"], rows[32_768]["cold_plus_collect_wall_speedup"])
        for row in rows.values():
            self.assertLess(row["prepare_speedup"], 1.0)
            self.assertGreater(row["query_total_speedup"], 1.0)
            self.assertLess(row["cold_plus_collect_wall_speedup"], self.payload["material_wall_speedup_floor"])
        summary = self.payload["blocker_summary"]
        self.assertLess(summary["best_cold_plus_collect_wall_speedup"], self.payload["material_wall_speedup_floor"])
        self.assertLess(summary["best_collect_speedup"], 1.01)

    def test_required_blockers_are_engine_level_not_app_specific(self):
        blockers = set(self.payload["required_blockers_before_m7"])
        self.assertIn("optix_prepare_slower_than_embree", blockers)
        self.assertIn("material_wall_floor_not_met", blockers)
        self.assertIn("larger_scale_not_better", blockers)
        self.assertIn("query_only_claim_forbidden", blockers)
        self.assertIn("collect_not_material_win", blockers)
        self.assertIn("external_m7_review_missing_for_new_row", blockers)
        self.assertIn("generic_overhead_reduction_required", blockers)
        self.assertIn("same_contract_public_wording_review_missing", blockers)
        self.assertIn("prepare", self.payload["next_engine_action"])
        self.assertIn("collect/compaction", self.payload["next_engine_action"])
        self.assertIn("without contact-specific native logic", self.payload["next_engine_action"])

    def test_markdown_keeps_no_go_boundary_and_user_audit(self):
        for phrase in (
            "AABB Prepare-Reuse Overhead Gate",
            "Status: `aabb_prepare_reuse_overhead_gate_blocked_not_m7`",
            "| 32768 | 50 | 0.624x | 1.178x | 1.005x | 1.140x | 1.137x |",
            "| 65536 | 50 | 0.742x | 1.109x | 0.906x | 1.087x | 1.084x |",
            "Best cold+collect wall speedup: `1.140x`",
            "`generic_overhead_reduction_required`",
            "Do not quote query-total speedup as a V3 win",
            "Goal-Level Decision Audit",
            "Was I foolish?",
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
            self.assertEqual(rebuilt["observed_ratios"], self.payload["observed_ratios"])
            self.assertIn("AABB Prepare-Reuse Overhead Gate", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
