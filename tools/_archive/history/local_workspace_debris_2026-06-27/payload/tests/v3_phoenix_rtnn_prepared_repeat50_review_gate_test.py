from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_rtnn_prepared_repeat50_review_gate.py"
PACKET_JSON = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_prepared_repeat50_review_gate_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
ROW_ID = "rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02"


class V3PhoenixRtnnPreparedRepeat50ReviewGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not PACKET_JSON.exists() or not PACKET_MD.exists():
            subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_gate_promotes_one_scoped_row_only(self) -> None:
        packet = self.packet
        self.assertEqual(packet["status"], "rtnn_prepared_repeat50_m7_qualified_row_scoped")
        self.assertEqual(packet["generic_capability"], "ranked_summary")
        self.assertEqual(packet["external_review_status"], "claude_approve_with_conditions")
        self.assertEqual(
            packet["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete_approve_one_row_scoped_m7",
        )
        self.assertTrue(packet["m7_candidate_reopen_authorized"])
        self.assertTrue(packet["m7_promotion_authorized"])
        self.assertEqual(packet["m7_qualified_release_rows_added"], 1)
        self.assertEqual(packet["candidate_row_ids"], [ROW_ID])
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertTrue(packet["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(packet["whole_app_speedup_claim_authorized"])
        self.assertFalse(packet["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(packet["whole_rtnn_claim_authorized"])
        self.assertFalse(packet["one_shot_rtnn_claim_authorized"])
        self.assertFalse(packet["paper_equivalent_claim_authorized"])
        self.assertEqual(packet["failed_checks"], [])
        self.assertTrue(all(packet["checks"].values()))

    def test_numbers_precision_baseline_and_provenance_are_hard_conditions(self) -> None:
        row = self.packet["candidate_row"]
        self.assertEqual(row["row_id"], ROW_ID)
        self.assertEqual(row["app_id"], "rtnn")
        self.assertEqual(row["generic_capability"], "ranked_summary")
        self.assertEqual(row["scope"], "prepared repeat50 session amortization only")
        self.assertEqual(row["hardware"], "NVIDIA RTX 4000 Ada Generation")
        self.assertEqual(row["point_count"], 1_048_576)
        self.assertEqual(row["repeat"], 50)
        self.assertEqual(row["k_max"], 50)
        self.assertAlmostEqual(row["radius"], 0.02)
        self.assertEqual(row["baseline"], "CuPy uniform-grid CUDA-core")
        self.assertAlmostEqual(row["hot_query_speedup"], 7.88855708189875)
        self.assertAlmostEqual(row["cold_plus_query_speedup"], 1.3150391330840123)
        self.assertAlmostEqual(row["runner_wall_speedup"], 3.760722286400028)
        self.assertGreater(row["runner_wall_speedup"], self.packet["material_speedup_floor"])
        self.assertLess(row["cold_plus_query_speedup"], self.packet["material_speedup_floor"])
        self.assertIn("float32 internal precision", row["precision_disclosure"])
        self.assertIn("float64 coordinate columns", row["precision_disclosure"])
        self.assertAlmostEqual(row["sum_distance_relative_error"], 1.2073584296566818e-10)
        self.assertGreaterEqual(row["source_manifest_hash_count"], 4)
        self.assertEqual(
            row["source_manifest_path"],
            "docs/rebuild/v3/evidence/phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621/source_manifest.sha256",
        )

    def test_approved_wording_carries_claude_conditions_together(self) -> None:
        wording = self.packet["candidate_row"]["approved_row_scoped_public_wording"]
        for phrase in (
            "7.889x hot-query speedup",
            "1.315x cold-plus-query speedup",
            "3.761x runner-wall speedup",
            "CuPy uniform-grid CUDA-core",
            "float32 internal precision",
            "float64 coordinate columns",
            "across 50 prepared repeated queries on the same search structure",
            "1.207e-10 sum-distance relative error",
            "source_manifest.sha256",
            "no git head",
            "scoped prepared repeated-session amortization result only",
        ):
            self.assertIn(phrase, wording)
        forbidden = "\n".join(self.packet["forbidden_public_wording"])
        self.assertIn("RTNN is solved", forbidden)
        self.assertIn("one-shot RTNN speedup", forbidden)
        self.assertIn("general nearest-neighbor baseline", forbidden)
        self.assertIn("broad V3-over-V2 speedup", forbidden)

    def test_review_records_are_real_and_consensus_accepts_conditions(self) -> None:
        records = self.packet["review_records"]
        for key in (
            "candidate_evidence",
            "repeat50_summary",
            "optix_payload",
            "cupy_grid_payload",
            "source_manifest",
            "call_for_review",
            "claude_external_review",
            "claude_external_review_stream",
            "codex_consensus",
        ):
            self.assertIn(key, records)
            self.assertTrue((ROOT / records[key]).exists(), key)
        claude = (ROOT / records["claude_external_review"]).read_text(encoding="utf-8")
        self.assertIn("APPROVE\\_WITH\\_CONDITIONS", claude)
        self.assertIn("Cold-plus-query (1.315x) is below the 2.0x material floor", claude)
        self.assertIn("float32 OptiX ranked-summary vs float64-coordinate CuPy grid", claude)
        consensus = (ROOT / records["codex_consensus"]).read_text(encoding="utf-8")
        self.assertIn("claude_codex_consensus_complete_approve_one_row_scoped_m7", consensus)
        self.assertIn("release_authorized: false", consensus)
        self.assertIn("source_manifest.sha256", consensus)

    def test_markdown_keeps_release_boundary_and_decision_audit(self) -> None:
        markdown = self.markdown
        self.assertIn("not V3 release authorization", markdown)
        self.assertIn("M7 rows added: `1`", markdown)
        self.assertIn(ROW_ID, markdown)
        self.assertIn("Hot-query speedup: `7.889x`", markdown)
        self.assertIn("Cold-plus-query speedup: `1.315x`", markdown)
        self.assertIn("Runner-wall speedup: `3.761x`", markdown)
        self.assertIn("Goal-Level Decision Audit", markdown)
        self.assertIn("Was I foolish?", markdown)

    def test_script_rebuilds_checked_in_gate(self) -> None:
        before_json = PACKET_JSON.read_text(encoding="utf-8")
        before_md = PACKET_MD.read_text(encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(PACKET_JSON.read_text(encoding="utf-8"), before_json)
        self.assertEqual(PACKET_MD.read_text(encoding="utf-8"), before_md)


if __name__ == "__main__":
    unittest.main()
