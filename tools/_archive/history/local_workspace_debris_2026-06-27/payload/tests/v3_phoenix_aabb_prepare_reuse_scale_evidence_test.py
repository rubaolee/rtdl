import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_aabb_prepare_reuse_scale_evidence.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_scale_evidence_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixAabbPrepareReuseScaleEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_records_not_m7_scale_no_go(self):
        payload = self.payload
        self.assertEqual(
            payload["status"],
            "aabb_prepare_reuse_scale_evidence_not_m7_scale_does_not_clear_floor",
        )
        self.assertEqual(payload["generic_capability"], "aabb_candidate_stream")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertFalse(payload["m7_reopen_candidate_pending_2ai_review"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_scale_rows_show_larger_scale_does_not_clear_floor(self):
        rows = {row["grid_count"]: row for row in self.payload["scale_rows"]}
        self.assertEqual(set(rows), {32_768, 65_536})
        self.assertAlmostEqual(
            rows[32_768]["optix_over_embree_cold_plus_collect_wall_speedup"],
            1.1400086912394385,
        )
        self.assertAlmostEqual(
            rows[65_536]["optix_over_embree_cold_plus_collect_wall_speedup"],
            1.0870090497524356,
        )
        self.assertLess(
            rows[65_536]["optix_over_embree_cold_plus_collect_wall_speedup"],
            rows[32_768]["optix_over_embree_cold_plus_collect_wall_speedup"],
        )
        for row in rows.values():
            self.assertLess(
                row["optix_over_embree_cold_plus_collect_wall_speedup"],
                self.payload["material_wall_speedup_floor"],
            )
            self.assertTrue(row["matches_cpu_reference"])
            self.assertTrue(row["complete_candidate_coverage"])

    def test_interpretation_blocks_scale_shopping(self):
        self.assertIn("does not reopen M7", self.payload["interpretation"])
        self.assertIn("fell to 1.087x", self.payload["interpretation"])
        self.assertIn("Stop scale-shopping this row", self.payload["next_engine_action"])
        self.assertIn(
            "Do not keep increasing scale until a ratio crosses the floor without a contract rationale.",
            self.payload["forbidden_shortcuts"],
        )

    def test_markdown_contains_ratios_and_decision_audit(self):
        for phrase in (
            "M7 rows added by this packet: 0",
            "| 32768 | 50 | 0.624x | 1.178x | 1.005x | 1.140x | 1.137x |",
            "| 65536 | 50 | 0.742x | 1.109x | 0.906x | 1.087x | 1.084x |",
            "Material wall-speedup floor: `1.200x`.",
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
            self.assertEqual(rebuilt["scale_rows"], self.payload["scale_rows"])
            self.assertIn("AABB Prepare-Reuse Scale Evidence", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
