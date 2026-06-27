import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_barnes_hut_same_basis_wall_time_no_go.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_barnes_hut_same_basis_wall_time_no_go_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixBarnesHutSameBasisWallTimeNoGoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_is_same_basis_no_go_not_release(self):
        payload = self.payload
        self.assertEqual(
            payload["status"],
            "barnes_hut_same_basis_no_go_current_frontier_shape_not_m7",
        )
        self.assertEqual(payload["generic_capability"], "aggregate_frontier")
        self.assertEqual(payload["refined_generic_capability"], "vector_accumulation")
        self.assertEqual(payload["same_basis_timing_kind"], "wall_repeat_median_seconds")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertFalse(payload["aggregate_frontier_m7_gap_closed"])
        self.assertFalse(payload["current_prepared_optix_frontier_shape_m7_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertEqual(payload["failures"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_wall_repeat_basis_keeps_fused_numba_cuda_fastest(self):
        summary = self.payload["same_basis_summary"]
        self.assertTrue(summary["all_fastest_numba_cuda"])
        self.assertTrue(summary["prepared_optix_numba_slower_all_scales"])
        self.assertEqual(
            summary["fastest_by_scale"],
            {
                "32768": "numba_cuda_fused",
                "65536": "numba_cuda_fused",
                "131072": "numba_cuda_fused",
            },
        )
        self.assertAlmostEqual(summary["prepared_optix_numba_over_fastest"]["32768"], 7.022492010243151)
        self.assertAlmostEqual(summary["prepared_optix_numba_over_fastest"]["65536"], 4.989954431032739)
        self.assertAlmostEqual(summary["prepared_optix_numba_over_fastest"]["131072"], 13.591229310768684)
        self.assertGreater(summary["min_prepared_optix_numba_over_fastest"], 2.0)

    def test_every_route_uses_repeat_seconds_for_same_basis(self):
        for body in self.payload["body_summaries"]:
            self.assertTrue(body["route_parity_passed"])
            self.assertGreater(body["contribution_row_count"], 1_000_000)
            for row in body["route_rows"]:
                self.assertIsNotNone(row["repeat_seconds_median"])
                self.assertEqual(
                    row["same_basis_wall_repeat_seconds"],
                    row["repeat_seconds_median"],
                )
                self.assertFalse(row["public_speedup_claim_authorized"])
                self.assertFalse(row["rt_core_speedup_claim_authorized"])

    def test_markdown_records_no_go_and_next_path(self):
        for phrase in (
            "M7 rows added by this packet: 0",
            "Current prepared RTDL/OptiX frontier-emission rows remain not M7.",
            "The fused Numba CUDA route is not an RT-core result.",
            "A future aggregate-frontier M7 attempt must be a separate reusable partner-contract review.",
            "Was I foolish?",
            "I rechecked the historical artifact under one wall-clock basis",
            "wall-repeat fields already show the same ordering",
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
            self.assertEqual(rebuilt["same_basis_summary"], self.payload["same_basis_summary"])
            self.assertIn("Same-Basis Wall-Time No-Go", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
