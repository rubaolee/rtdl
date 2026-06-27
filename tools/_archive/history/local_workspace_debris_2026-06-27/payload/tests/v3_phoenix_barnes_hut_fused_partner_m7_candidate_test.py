import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_barnes_hut_fused_partner_m7_candidate.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixBarnesHutFusedPartnerM7CandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_candidate_packet_is_not_yet_m7(self):
        payload = self.payload
        self.assertEqual(payload["status"], "aggregate_tree_fused_partner_m7_candidate_pending_external_review")
        self.assertEqual(payload["candidate_row_id"], "aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped")
        self.assertEqual(payload["generic_capability"], "aggregate_frontier")
        self.assertEqual(payload["refined_generic_capability"], "vector_accumulation")
        self.assertEqual(payload["contract"], "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["candidate_m7_contribution_if_external_review_approves"], 1)
        self.assertTrue(payload["local_evidence_sufficient_for_external_public_row_review"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_small_smoke_proves_generic_contract_boundary(self):
        smoke = self.payload["small_exact_smoke"]
        metadata = smoke["metadata"]
        self.assertTrue(smoke["passed"])
        self.assertEqual(smoke["compared_against"], "sum_aggregate_frontier_weighted_vectors_2d_cpu_reference")
        self.assertEqual(metadata["contract"], "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1")
        self.assertFalse(metadata["frontier_rows_emitted"])
        self.assertFalse(metadata["frontier_rows_materialized_on_host"])
        self.assertFalse(metadata["contribution_rows_materialized_on_host"])
        self.assertFalse(metadata["native_engine_app_specific"])
        self.assertFalse(metadata["rt_cores_used"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_large_rows_show_candidate_speedup_under_same_wall_basis(self):
        rows = {row["body_count"]: row for row in self.payload["large_same_basis_rows"]}
        self.assertEqual(set(rows), {32768, 65536, 131072})
        self.assertGreater(self.payload["large_same_basis_summary"]["min_cpu_numba_fused_over_candidate"], 3.0)
        self.assertGreater(self.payload["large_same_basis_summary"]["min_prepared_optix_numba_over_candidate"], 4.0)
        self.assertAlmostEqual(rows[32768]["cpu_numba_fused_over_candidate"], 7.491750733402135)
        self.assertAlmostEqual(rows[65536]["cpu_numba_fused_over_candidate"], 3.1018109918722025)
        self.assertAlmostEqual(rows[131072]["cpu_numba_fused_over_candidate"], 4.081631994617688)
        self.assertAlmostEqual(rows[131072]["prepared_optix_numba_over_candidate"], 13.591229310768684)
        self.assertGreater(rows[131072]["contribution_row_count"], 60_000_000)
        for row in rows.values():
            self.assertFalse(row["frontier_rows_materialized_on_host"])
            self.assertFalse(row["contribution_rows_materialized_on_host"])
            self.assertFalse(row["rt_cores_used"])
            self.assertFalse(row["rt_core_speedup_claim_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])

    def test_markdown_keeps_review_and_claim_boundary(self):
        for phrase in (
            "This packet does not promote a row.",
            "candidate_m7_contribution_if_external_review_approves: 1",
            "This is not an RT-core claim.",
            "external_ai_review_not_done_for_candidate_row",
            "large-row validation is route parity plus checksums",
            "Was I foolish?",
            "I separated the slow RT frontier-emission no-go from the fast generic partner route.",
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
            self.assertEqual(rebuilt["large_same_basis_summary"], self.payload["large_same_basis_summary"])
            self.assertIn("Fused Partner M7 Candidate", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
