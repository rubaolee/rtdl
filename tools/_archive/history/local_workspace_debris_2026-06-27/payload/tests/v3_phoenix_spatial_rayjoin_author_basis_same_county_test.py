from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/v3_phoenix_spatial_rayjoin_author_basis_same_county.py"
PACKET_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.json"
PACKET_MD = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.md"


class V3PhoenixSpatialRayJoinAuthorBasisSameCountyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_author_timing_basis_present_but_not_m7(self) -> None:
        packet = self.packet
        self.assertEqual(packet["status"], "spatial_rayjoin_same_county_author_timing_present_not_m7")
        self.assertEqual(packet["generic_capability"], "point_location_topology_stream")
        self.assertTrue(packet["same_dataset_author_timing_basis_present"])
        self.assertFalse(packet["author_result_count_printed"])
        self.assertFalse(packet["author_result_count_parity_verified"])
        self.assertFalse(packet["m7_promotion_authorized"])
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertFalse(packet["rtdl_beats_rayjoin_claim_authorized"])
        self.assertEqual(packet["failed_checks"], [])

    def test_author_run_and_rtdl_reference_are_same_county_scoped(self) -> None:
        packet = self.packet
        author = packet["author_run"]
        rtdl = packet["rtdl_exact_f64_reference"]
        self.assertEqual(packet["dataset"], "data/rayjoin_public_cdb/br_county.cdb")
        self.assertIn("/workspace/RayJoin_fresh/release/bin/query_exec", author["query_exec_path"])
        self.assertIn("NVIDIA RTX 4000 Ada Generation", author["gpu"])
        self.assertEqual(author["warmup"], 5)
        self.assertEqual(author["repeat"], 50)
        self.assertEqual(author["query_launch_count"], 55)
        self.assertEqual(author["query_point_count_from_optix_launch_width"], 342738)
        self.assertAlmostEqual(author["query_ms"], 1.86566)
        self.assertGreater(author["wrapper_elapsed_sec"], 1.0)
        self.assertEqual(rtdl["exact_count"], 47262)
        self.assertEqual(rtdl["count_mode"], "relation_status_corrected_executor_validated")
        self.assertGreater(rtdl["prepared_query_ms_median"], 6.0)
        self.assertIn("device_resident_prepared_point_probe_columns", rtdl["query_stream_residency"])

    def test_comparison_keeps_author_faster_fact_and_blocks_claims(self) -> None:
        comparison = self.packet["comparison"]
        self.assertGreater(
            comparison["rayjoin_author_query_speedup_vs_rtdl_exact_f64_prepared_query"],
            3.0,
        )
        self.assertLess(
            comparison["rtdl_exact_f64_prepared_query_relative_to_rayjoin_author_query"],
            0.4,
        )
        self.assertFalse(comparison["wrapper_comparison_authorized_for_public_claim"])
        blockers = set(self.packet["remaining_blockers_before_m7"])
        self.assertIn("rayjoin_author_result_count_not_printed_or_public_scope_review_missing", blockers)
        self.assertIn("rayjoin_author_query_faster_than_rtdl_exact_f64_query", blockers)
        self.assertIn("external_ai_review_missing", blockers)
        self.assertIn("public_wording_review_missing", blockers)

    def test_markdown_exposes_boundary(self) -> None:
        markdown = self.markdown
        self.assertIn("Same-dataset author timing basis present: `true`", markdown)
        self.assertIn("Author result count printed: `false`", markdown)
        self.assertIn("M7 promotion authorized: `false`", markdown)
        self.assertIn("RTDL-beats-RayJoin claim authorized: `false`", markdown)
        self.assertIn("RayJoin author Query speedup vs RTDL exact-f64 prepared query", markdown)
        self.assertIn("not an M7 promotion", markdown)
        self.assertIn("Goal-Level Decision Self-Audit", markdown)

    def test_script_rebuilds_packet(self) -> None:
        before_json = PACKET_JSON.read_text(encoding="utf-8")
        before_md = PACKET_MD.read_text(encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(PACKET_JSON.read_text(encoding="utf-8"), before_json)
        self.assertEqual(PACKET_MD.read_text(encoding="utf-8"), before_md)


if __name__ == "__main__":
    unittest.main()
