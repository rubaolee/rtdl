import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "phoenix_v3_raydb_m28_grouped_reduction_20260620"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_raydb_m28_grouped_reduction_pod_evidence_2026-06-20.md"


class V3PhoenixRaydbM28EvidenceTest(unittest.TestCase):
    def load(self, rel: str):
        return json.loads((EVIDENCE / rel).read_text(encoding="utf-8"))

    def test_524k_grouped_reduction_passes_internal_gate(self):
        payload = self.load("m28_raydb_grouped_reduction_524288.json")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["parameters"]["generated_rows"], 524288)
        self.assertEqual(payload["parameters"]["generated_groups"], 2048)
        self.assertTrue(payload["comparison"]["all_match_cpu_reference"])
        self.assertTrue(payload["comparison"]["all_prepared_steady_state"])
        self.assertTrue(payload["comparison"]["all_primitive_payload_reused"])
        self.assertTrue(payload["comparison"]["all_ray_batch_reused"])
        self.assertTrue(payload["comparison"]["no_partner_continuation_required"])
        self.assertFalse(payload["comparison"]["public_speedup_claim_authorized"])

    def test_same_contract_ratios_are_internal_hot_query_only(self):
        payload = self.load("m28_raydb_grouped_reduction_524288.json")
        pairs = {row["mode"]: row for row in payload["comparison"]["same_contract_backend_pairs"]}
        self.assertGreater(pairs["count"]["embree_over_optix_median"], 8.0)
        self.assertGreater(pairs["sum"]["embree_over_optix_median"], 100.0)
        for pair in pairs.values():
            self.assertEqual(
                pair["comparison_scope"],
                "internal_same_contract_prepared_query_refresh_not_public_speedup",
            )
        rows = {(row["backend"], row["mode"]): row for row in payload["rows"]}
        self.assertGreater(rows[("embree", "sum")]["workload_build_sec"], 200.0)
        self.assertGreater(rows[("optix", "sum")]["workload_build_sec"], 200.0)
        self.assertLess(rows[("embree", "count")]["workload_build_sec"], 5.0)
        self.assertLess(rows[("optix", "count")]["workload_build_sec"], 5.0)
        for mode in ("count", "sum"):
            self.assertFalse(rows[("embree", mode)]["rt_core_accelerated"])
            self.assertTrue(rows[("optix", mode)]["rt_core_accelerated"])
        for row in rows.values():
            self.assertTrue(row["matches_cpu_reference"])
            self.assertEqual(row["v2_5_selected_path"], "prepared_fused_generic_grouped_reduction")
            self.assertFalse(row["partner_continuation_required"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])

    def test_overlarge_attempt_is_preserved(self):
        status = (EVIDENCE / "overlarge_1048576_attempt_status.txt").read_text(encoding="utf-8")
        self.assertIn("stopped overlarge 1048576-row attempt", status)
        self.assertIn("exceeded bounded-goal time budget", status)
        log_text = (EVIDENCE / "m28_raydb_grouped_reduction_1048576.log").read_text(
            encoding="utf-8"
        )
        self.assertTrue(
            len(log_text.strip()) > 0,
            "overlarge log file must contain at least one line of output",
        )

    def test_report_keeps_release_and_end_to_end_claims_blocked(self):
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("internal grouped-reduction evidence", report)
        self.assertIn("prepared hot-query ratios", report)
        self.assertIn("not end-to-end application timings", report)
        self.assertIn("RayDB-style V3 is 158x faster end to end", report)
        self.assertIn("release_authorized=false", report)
        self.assertIn("public_speedup_claim_authorized=false", report)


if __name__ == "__main__":
    unittest.main()
