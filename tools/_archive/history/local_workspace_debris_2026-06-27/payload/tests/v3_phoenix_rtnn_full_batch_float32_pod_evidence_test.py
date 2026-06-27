import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_rtnn_full_batch_float32_pod_evidence.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
MAIN_EVIDENCE_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "rtnn_full_batch_float32_same_contract_1048576_r5_20260621"
)


class V3PhoenixRtnnFullBatchFloat32PodEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_is_hot_query_candidate_not_m7(self):
        payload = self.payload
        self.assertEqual(
            payload["status"],
            "rtnn_full_batch_float32_hot_query_candidate_pending_2ai_wall_blocked_not_m7",
        )
        self.assertEqual(payload["generic_capability"], "ranked_summary")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertTrue(payload["m7_reopen_candidate_pending_2ai_review"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_main_row_is_serious_scale_and_same_contract(self):
        payload = self.payload
        self.assertEqual(payload["hardware"]["gpu"], "NVIDIA RTX 4000 Ada Generation")
        self.assertEqual(payload["hardware"]["rt_hardware_gate"], "pass")
        self.assertEqual(payload["main_row"]["point_count"], 1_048_576)
        self.assertEqual(payload["main_row"]["repeat"], 5)
        self.assertTrue(payload["parity"]["same_contract_signature_match"])
        self.assertTrue(payload["parity"]["integer_signature_match"])
        self.assertLessEqual(
            payload["parity"]["sum_distance_relative_error"],
            payload["parity"]["sum_distance_relative_tolerance"],
        )
        self.assertTrue((MAIN_EVIDENCE_DIR / "summary.json").exists())
        self.assertTrue((MAIN_EVIDENCE_DIR / "rtnn_full_batch_float32_optix.json").exists())
        self.assertTrue((MAIN_EVIDENCE_DIR / "rtnn_full_batch_float32_cupy_grid.json").exists())

    def test_hot_query_win_and_wall_regressions_are_both_explicit(self):
        row = self.payload["main_row"]
        self.assertGreater(row["hot_speedup_optix_over_cupy_grid"], 7.0)
        self.assertLess(row["cold_plus_query_speedup_optix_over_cupy_grid"], 0.5)
        self.assertLess(row["runner_wall_speedup_optix_over_cupy_grid"], 0.7)
        self.assertIn("prepared-hot-query candidate", self.payload["interpretation"])
        self.assertIn("OptiX still loses cold-plus-query wall", self.payload["interpretation"])
        self.assertIn(
            "Do not claim RTDL beats CuPy grid end-to-end or wall-clock on this row.",
            self.payload["forbidden_shortcuts"],
        )

    def test_scale_rows_include_262k_and_1m_repeat5(self):
        rows = {(row["point_count"], row["repeat"]): row for row in self.payload["scale_rows"]}
        self.assertIn((262_144, 3), rows)
        self.assertIn((1_048_576, 3), rows)
        self.assertIn((1_048_576, 5), rows)
        self.assertGreater(rows[(1_048_576, 5)]["hot_speedup_optix_over_cupy_grid"], 7.0)
        self.assertLess(rows[(1_048_576, 5)]["runner_wall_speedup_optix_over_cupy_grid"], 1.0)

    def test_markdown_preserves_public_boundary(self):
        for phrase in (
            "M7 rows added by this packet: 0",
            "OptiX/CuPy hot-query speedup: `7.790x`",
            "OptiX/CuPy cold-plus-query speedup: `0.393x`",
            "Do not quote the 7.790x hot-query speedup without saying prepared-hot-query only.",
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
            self.assertEqual(rebuilt["main_row"], self.payload["main_row"])
            self.assertIn("RTNN Full-Batch Float32", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
