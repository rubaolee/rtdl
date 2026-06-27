import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_aabb_query_cache_evidence.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_query_cache_evidence_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixAabbQueryCacheEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_query_cache_packet_is_no_go_not_m7(self):
        payload = self.payload
        self.assertEqual(
            payload["status"],
            "aabb_prepare_reuse_query_cache_evidence_not_m7_wall_floor_not_met",
        )
        self.assertEqual(payload["generic_capability"], "aabb_candidate_stream")
        self.assertFalse(payload["m7_candidate_reopen_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_cache_is_real_but_wall_floor_still_fails(self):
        rows = {row["grid_count"]: row for row in self.payload["observed_rows"]}
        self.assertEqual(set(rows), {32_768, 65_536})
        self.assertAlmostEqual(
            rows[32_768]["optix_over_embree_cold_plus_collect_wall_speedup"],
            1.1880894980002084,
        )
        self.assertAlmostEqual(
            rows[65_536]["optix_over_embree_cold_plus_collect_wall_speedup"],
            1.1351174352209814,
        )
        self.assertLess(
            rows[65_536]["optix_over_embree_cold_plus_collect_wall_speedup"],
            rows[32_768]["optix_over_embree_cold_plus_collect_wall_speedup"],
        )
        for row in rows.values():
            self.assertTrue(row["embree_cache_observed"])
            self.assertTrue(row["optix_cache_observed"])
            self.assertEqual(row["optix_cache_stats"]["range_intersection_misses"], 1)
            self.assertEqual(row["optix_cache_stats"]["range_intersection_hits"], 52)
            self.assertGreater(row["optix_over_embree_query_total_speedup"], 1.0)
            self.assertLess(
                row["optix_over_embree_cold_plus_collect_wall_speedup"],
                self.payload["material_wall_speedup_floor"],
            )
        self.assertTrue(self.payload["blocker_summary"]["cache_was_observed"])

    def test_markdown_forbids_query_only_or_scale_shopping_claims(self):
        for phrase in (
            "Status: `aabb_prepare_reuse_query_cache_evidence_not_m7_wall_floor_not_met`",
            "| 32768 | 50 | 52 | 0.577x | 1.238x | 0.936x | 1.188x | 1.181x |",
            "| 65536 | 50 | 52 | 0.803x | 1.161x | 0.878x | 1.135x | 1.129x |",
            "correct engine cleanup, not a V3 performance promotion",
            "Do not quote query-total speedup as a V3 win",
            "Do not keep scale-shopping this contract",
            "Goal-Level Decision Audit",
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
            self.assertEqual(rebuilt["observed_rows"], self.payload["observed_rows"])
            self.assertIn("AABB Query-Cache Evidence", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
