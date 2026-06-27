import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_rtnn_cubin_cache_evidence.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_optix_cubin_cache_evidence_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixRtnnCubinCacheEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_records_generic_cache_not_m7(self):
        payload = self.payload
        self.assertEqual(
            payload["status"],
            "rtnn_optix_cubin_cache_reduces_prepare_not_m7_wall_floor_not_met",
        )
        self.assertIn("OptiX CUBIN", payload["candidate_scope"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertFalse(payload["m7_reopen_candidate_pending_2ai_review"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_cache_reduces_prepare_but_not_material_wall_speed(self):
        payload = self.payload
        improvement = payload["improvement_vs_cold_optix"]
        warm = payload["warm_comparison_vs_cupy_grid"]
        self.assertGreater(improvement["execution_prepare_reduction"], 5.0)
        self.assertGreater(improvement["cold_plus_query_reduction"], 2.0)
        self.assertGreater(improvement["runner_wall_reduction"], 1.7)
        self.assertGreater(warm["rtdl_optix_over_cupy_grid_hot_speedup"], 7.0)
        self.assertLess(warm["rtdl_optix_over_cupy_grid_cold_plus_query_speedup"], 1.0)
        self.assertGreater(warm["rtdl_optix_over_cupy_grid_runner_wall_speedup"], 1.0)
        self.assertLess(warm["rtdl_optix_over_cupy_grid_runner_wall_speedup"], 2.0)
        self.assertIn("1.098x", payload["not_m7_blockers"][0])

    def test_cache_controls_and_pod_evidence_are_named(self):
        payload = self.payload
        self.assertEqual(payload["cache_controls"]["cache_dir_env"], "RTDL_OPTIX_CUBIN_CACHE_DIR")
        self.assertEqual(payload["cache_controls"]["disable_env"], "RTDL_OPTIX_DISABLE_CUBIN_CACHE")
        self.assertGreater(payload["cache_controls"]["cache_bytes"], 0)
        self.assertTrue(payload["cache_controls"]["cache_files"])
        self.assertEqual(payload["hardware"]["name"], "NVIDIA RTX 4000 Ada Generation")
        self.assertTrue(payload["parity"]["same_contract_signature_match"])
        self.assertTrue(payload["parity"]["integer_signature_match"])

    def test_markdown_keeps_boundary_visible(self):
        for phrase in (
            "M7 rows added by this packet: 0",
            "Prepare reduction: `5.914x`",
            "Warm OptiX/CuPy runner-wall speedup: `1.098x`",
            "Do not call 1.098x runner-wall speedup a Phoenix V3 performance win.",
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
            self.assertEqual(rebuilt["improvement_vs_cold_optix"], self.payload["improvement_vs_cold_optix"])
            self.assertIn("RTNN OptiX CUBIN Cache", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
