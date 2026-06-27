import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_rtnn_npz_cubin_cache_evidence.py"
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_npz_cubin_cache_evidence_2026-06-21.json"
REPORT = PACKET.with_suffix(".md")


class V3PhoenixRtnnNpzCubinCacheEvidenceTest(unittest.TestCase):
    def load(self):
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_records_real_progress_without_m7(self):
        payload = self.load()
        self.assertEqual(
            payload["status"],
            "rtnn_npz_cubin_cache_wall_improves_not_m7_material_floor_not_met",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertEqual(
            payload["generic_capability"],
            "fixed_radius_neighbors_3d_npz_ingestion_plus_optix_cubin_cache",
        )

    def test_warm_runner_improves_but_stays_below_material_floor(self):
        payload = self.load()
        warm = payload["warm_comparison_vs_cupy_grid"]
        floor = payload["material_speedup_floor"]
        self.assertGreater(warm["hot_query_speedup"], floor)
        self.assertGreater(warm["cold_plus_query_speedup"], 1.0)
        self.assertLess(warm["cold_plus_query_speedup"], floor)
        self.assertGreater(warm["runner_wall_speedup"], 1.0)
        self.assertLess(warm["runner_wall_speedup"], floor)
        self.assertGreater(payload["cache_reductions"]["execution_prepare"], 10.0)
        self.assertGreater(payload["cache_reductions"]["runner_wall"], 4.0)
        self.assertGreater(payload["remaining_overhead"]["warm_optix_non_hot_over_hot_query"], 20.0)

    def test_npz_source_and_parity_are_recorded(self):
        payload = self.load()
        self.assertEqual(payload["measurements"]["warm_optix"]["point_column_source"], "npz")
        self.assertEqual(payload["measurements"]["warm_cupy_grid"]["point_column_source"], "npz")
        self.assertTrue(payload["parity"]["same_contract_signature_match"])
        self.assertTrue(payload["parity"]["integer_signature_match"])
        blockers = "\n".join(payload["not_m7_blockers"])
        self.assertIn("1.328x", blockers)
        self.assertIn("2.0x material floor", blockers)

    def test_report_contains_decision_audit_and_forbidden_shortcuts(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Phoenix V3 RTNN NPZ + CUBIN Cache Evidence",
            "not M7",
            "runner-wall speedup",
            "Goal-Level Decision Audit",
            "Do not call 1.328x runner-wall",
        ):
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
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.load())
            self.assertIn("NPZ + CUBIN", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
