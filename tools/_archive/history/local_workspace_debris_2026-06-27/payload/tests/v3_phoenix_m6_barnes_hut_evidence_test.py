import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "phoenix_v3_m6_barnes_hut_20260620"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m6_barnes_hut_pod_evidence_2026-06-20.md"


class V3PhoenixM6BarnesHutEvidenceTest(unittest.TestCase):
    def load(self, rel: str):
        return json.loads((EVIDENCE / rel).read_text(encoding="utf-8"))

    def test_intake_passes_but_keeps_release_blocked(self):
        payload = self.load("m6_barnes_hut_intake_summary.json")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["overall_status"], "internal_m6_route_parity_evidence")
        self.assertEqual(payload["generic_capability"], "aggregate_frontier_vector_accumulation")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertEqual(payload["phoenix_m7_qualified_release_rows"], 0)
        self.assertTrue(payload["timing_basis_mixed"])
        self.assertEqual(payload["failures"], [])
        self.assertTrue(payload["checks"]["serious_scale_present"])
        self.assertTrue(payload["checks"]["route_parity_passed"])
        self.assertTrue(payload["checks"]["all_body_counts_have_four_routes"])

    def test_partitioned_rerun_covers_serious_scales(self):
        payload = self.load("m6_barnes_hut_intake_summary.json")
        rows = {int(row["body_count"]): row for row in payload["body_summaries"]}
        self.assertEqual({32768, 65536, 131072}, set(rows))
        for row in rows.values():
            self.assertEqual(row["fastest_route_id"], "numba_cuda_fused")
            self.assertEqual(row["route_count"], 4)
            self.assertTrue(row["route_parity_passed"])
            self.assertGreater(row["contribution_row_count"], 10_000_000)
            self.assertGreater(row["optix_numba_over_fastest"], 5.0)
        self.assertGreater(rows[131072]["optix_numba_over_fastest"], 10.0)

    def test_failed_single_process_attempt_is_preserved(self):
        log = (EVIDENCE / "m6_barnes_hut_rerank.log").read_text(encoding="utf-8")
        partitioned_log = (EVIDENCE / "m6_barnes_hut_partitioned.log").read_text(encoding="utf-8")
        self.assertIn("out of memory", log.lower())
        self.assertIn("END_PARTITIONED", partitioned_log)
        self.assertIn('"merged_rows": 12', partitioned_log)

    def test_report_records_boundary_and_interpretation(self):
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("internal M6 route-parity evidence", report)
        self.assertIn("This is not release authorization", report)
        self.assertIn("not a Barnes-Hut RT-core speedup claim", report)
        self.assertIn("prepared aggregate-frontier contract", report)
        self.assertIn("fused Numba CUDA route", report)
        self.assertIn("mixed timing bases", report)
        self.assertIn("Goal-Level Decision Audit", report)


if __name__ == "__main__":
    unittest.main()
