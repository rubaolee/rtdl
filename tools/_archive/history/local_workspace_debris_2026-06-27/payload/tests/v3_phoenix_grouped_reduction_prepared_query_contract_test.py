import json
import unittest
from pathlib import Path

from scripts import v3_phoenix_grouped_reduction_prepared_query_contract as contract


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.json"
CONTRACT_MD = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.md"


class V3PhoenixGroupedReductionPreparedQueryContractTest(unittest.TestCase):
    def payload(self):
        return json.loads(CONTRACT_JSON.read_text(encoding="utf-8"))

    def test_contract_is_draft_not_release(self):
        payload = self.payload()
        self.assertEqual(payload["status"], "prepared_query_contract_draft_not_release")
        self.assertEqual(payload["source_intake_status"], "grouped_reduction_m7_post_run_intake_not_promoted")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows"], 0)
        self.assertTrue(payload["sum_repeat100_actual_evidence_supersedes_formula_candidates"])
        self.assertTrue(payload["current_candidate_wording_uses_actual_repeat100"])
        self.assertIn(
            "phoenix_v3_grouped_reduction_sum_repeat100_actual_pod_evidence_2026-06-20.md",
            payload["sum_repeat100_actual_evidence"],
        )

    def test_contract_terms_are_user_reproducible(self):
        payload = self.payload()
        public_contract = payload["public_contract"]
        timing = payload["timing_contract"]
        self.assertEqual(public_contract["scope"], "prepared repeated grouped reductions over a fixed schema")
        self.assertEqual(public_contract["supported_operations_for_this_packet"], ["group_count", "group_sum_i64"])
        self.assertEqual(public_contract["supported_backends_for_this_packet"], ["embree", "optix"])
        self.assertFalse(public_contract["partner_continuation_required"])
        self.assertFalse(public_contract["native_engine_customization_allowed"])
        serialized = json.dumps(payload)
        for internal_term in ["RT-shaped table", "RayDB-specific native engine", "revenue/value encoding"]:
            self.assertNotIn(internal_term, serialized)
        self.assertEqual(timing["minimum_warmup_for_m7"], 3)
        self.assertIn("cold_prepare_total_sec", timing["required_fields"])
        self.assertIn("elapsed_median_sec", timing["required_fields"])
        self.assertTrue(timing["repeat_scenario_values_are_formula_projections"])
        self.assertIn("not independent multi-query end-to-end runs", timing["repeat_end_to_end_formula_note"])
        self.assertTrue(timing["single_query_required"])
        self.assertTrue(timing["break_even_required"])
        self.assertTrue(timing["cold_cost_must_be_reported_next_to_hot_speedup"])

    def test_candidate_rows_keep_m7_false_but_preserve_repeat100_signal(self):
        payload = self.payload()
        rows = {(row["generated_rows"], row["mode"]): row for row in payload["candidate_rows"]}
        self.assertEqual(len(rows), 4)
        self.assertGreater(rows[(262144, "sum")]["hot_query_speedup_embree_over_optix"], 200.0)
        self.assertGreater(rows[(262144, "sum")]["repeat_100_end_to_end_speedup"], 30.0)
        self.assertLess(rows[(262144, "sum")]["repeat_1_end_to_end_speedup"], 1.0)
        self.assertGreater(rows[(262144, "sum")]["repeat_profile"]["25"], 9.0)
        self.assertEqual(rows[(262144, "sum")]["recommended_public_repeat_count_if_promoted"], 100)
        self.assertGreater(rows[(524288, "sum")]["repeat_100_end_to_end_speedup"], 30.0)
        self.assertLess(rows[(524288, "sum")]["repeat_1_end_to_end_speedup"], 1.10)
        self.assertEqual(rows[(524288, "sum")]["recommended_public_repeat_count_if_promoted"], 100)
        self.assertIsNone(rows[(262144, "count")]["recommended_public_repeat_count_if_promoted"])
        self.assertIsNone(rows[(524288, "count")]["recommended_public_repeat_count_if_promoted"])
        self.assertIn("count_mode_high_breakeven_blocks_public_claim", rows[(262144, "count")]["blockers"])
        self.assertIn("count_mode_high_breakeven_blocks_public_claim", rows[(524288, "count")]["blockers"])
        for row in rows.values():
            self.assertEqual(row["promotion_status"], "candidate_needs_public_row_review_not_m7")
            self.assertFalse(row["m7_promoted"])
            self.assertIn("final_public_row_wording_review_required", row["blockers"])
            self.assertEqual(sorted(row["repeat_profile"].keys()), ["1", "10", "100", "2", "25", "5", "50"])
            self.assertEqual(
                row["repeat_profile_basis"],
                "formula_projection_from_measured_cold_prepare_and_hot_query_median",
            )

    def test_forbidden_claims_block_hot_query_overread(self):
        payload = self.payload()
        forbidden = "\n".join(payload["forbidden_claims"])
        self.assertIn("V3 is 224x faster end to end", forbidden)
        self.assertIn("whole-app or whole-database speedup is authorized", forbidden)
        self.assertIn("hot prepared-query speedup can be quoted without cold cost and repeat count", forbidden)
        wording = "\n".join(payload["draft_candidate_wording_not_publishable"])
        self.assertIn("not publishable", wording)
        self.assertIn("modeled repeat 100 end-to-end", wording)
        self.assertIn("not from an independently measured 100-query loop", wording)

    def test_markdown_contains_contract_boundaries(self):
        text = CONTRACT_MD.read_text(encoding="utf-8")
        for phrase in [
            "prepared-query contract draft",
            "fixed schema",
            "Modeled repeat 100 end-to-end",
            "Repeat Profile",
            "formula projections",
            "Supersession Note",
            "actual repeat100 pod",
            "not publishable",
            "Phoenix M7-qualified release rows: 0",
            "Do not",
        ]:
            self.assertIn(phrase, text)

    def test_generator_reproduces_checked_payload_shape(self):
        generated = contract.build_payload()
        current = self.payload()
        self.assertEqual(generated["status"], current["status"])
        self.assertEqual(generated["candidate_rows"], current["candidate_rows"])
        self.assertEqual(generated["forbidden_claims"], current["forbidden_claims"])


if __name__ == "__main__":
    unittest.main()
