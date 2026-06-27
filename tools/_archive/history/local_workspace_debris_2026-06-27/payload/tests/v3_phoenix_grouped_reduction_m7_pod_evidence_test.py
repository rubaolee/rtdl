import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "phoenix_v3_grouped_reduction_m7_20260620"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_m7_pod_evidence_2026-06-20.md"


class V3PhoenixGroupedReductionM7PodEvidenceTest(unittest.TestCase):
    def intake(self):
        return json.loads((EVIDENCE / "m7_grouped_reduction_post_run_intake.json").read_text(encoding="utf-8"))

    def pairs(self):
        pairs = {}
        for scale in self.intake()["scales"]:
            for pair in scale["pairs"]:
                pairs[(scale["generated_rows"], pair["mode"])] = pair
        return pairs

    def test_post_run_intake_is_fresh_not_promoted(self):
        payload = self.intake()
        self.assertTrue(payload["fresh_rerun"])
        self.assertEqual(payload["status"], "grouped_reduction_m7_post_run_intake_not_promoted")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promoted"])
        self.assertEqual(payload["m7_qualified_release_rows"], 0)
        self.assertEqual(payload["summary"]["m7_qualified_release_rows"], 0)
        self.assertEqual(payload["summary"]["pair_count"], 4)
        self.assertTrue(payload["summary"]["all_cpu_reference_match"])
        self.assertTrue(payload["summary"]["all_optix_hot_faster"])
        self.assertFalse(payload["summary"]["any_sum_row_has_large_cold_cost"])
        self.assertEqual(payload["summary"]["sum_rows_with_large_cold_cost"], [])

    def test_all_sources_are_warmup3_and_claim_flags_false(self):
        for scale in self.intake()["scales"]:
            self.assertEqual(scale["source_warmup"], 3)
            self.assertEqual(scale["status"], "ok")
            for pair in scale["pairs"]:
                self.assertTrue(pair["both_match_cpu_reference"])
                self.assertFalse(pair["embree_rt_core_accelerated"])
                self.assertTrue(pair["optix_rt_core_accelerated"])
                self.assertFalse(pair["release_authorized"])
                self.assertFalse(pair["public_speedup_claim_authorized"])
                self.assertFalse(pair["m7_promoted"])
                self.assertEqual(pair["claim_status"], "internal_post_run_intake_not_m7")
                self.assertNotIn("no_fresh_m7_pod_rerun_after_feasibility_packet", pair["m7_blockers"])
                self.assertIn(
                    "fresh_rerun_requires_external_review_before_m7_promotion",
                    pair["m7_blockers"],
                )
        audit = self.intake()["goal_level_decision_audit"]
        self.assertNotIn("158x", audit["foolish_actions"])
        self.assertIn("224.269x", audit["foolish_actions"])

    def test_repeat_aware_results_block_hot_query_overclaim(self):
        pairs = self.pairs()
        self.assertGreater(pairs[(262144, "sum")]["hot_query_speedup_embree_over_optix"], 200.0)
        self.assertLess(pairs[(262144, "sum")]["repeat_scenarios"]["1"]["end_to_end_speedup"], 1.0)
        self.assertGreater(pairs[(262144, "sum")]["repeat_scenarios"]["100"]["end_to_end_speedup"], 30.0)

        self.assertGreater(pairs[(524288, "sum")]["hot_query_speedup_embree_over_optix"], 180.0)
        self.assertGreater(pairs[(524288, "sum")]["repeat_scenarios"]["1"]["end_to_end_speedup"], 1.0)
        self.assertLess(pairs[(524288, "sum")]["repeat_scenarios"]["1"]["end_to_end_speedup"], 1.1)
        self.assertGreater(pairs[(524288, "sum")]["repeat_scenarios"]["100"]["end_to_end_speedup"], 30.0)

        for key in [(262144, "count"), (524288, "count")]:
            pair = pairs[key]
            self.assertGreater(pair["break_even_repeat_count"], 10.0)
            self.assertLess(pair["break_even_repeat_count"], 20.0)
            self.assertLess(pair["repeat_scenarios"]["1"]["end_to_end_speedup"], 1.0)
            self.assertGreater(pair["repeat_scenarios"]["100"]["end_to_end_speedup"], 2.0)

    def test_run_artifacts_and_report_exist(self):
        for name in [
            "claim_boundary_gate.txt",
            "gpu_env_gate.json",
            "optix_hardware_gate.json",
            "m7_execution.status",
            "m7_execution.log",
            "artifact_file_index.txt",
            "m7_grouped_reduction_262144_warmup3.json",
            "m7_grouped_reduction_524288_warmup3.json",
            "m7_grouped_reduction_post_run_intake.md",
        ]:
            self.assertTrue((EVIDENCE / name).exists(), name)
        self.assertEqual((EVIDENCE / "m7_execution.status").read_text(encoding="utf-8").strip(), "0")
        gate = (EVIDENCE / "claim_boundary_gate.txt").read_text(encoding="utf-8")
        self.assertIn("claim-boundary gate ok", gate)

        report = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "not M7 promotion",
            "M7-qualified release rows: 0",
            "224.269x",
            "superseded by actual",
            "phoenix_v3_grouped_reduction_sum_repeat100_actual_pod_evidence_2026-06-20.md",
            "Repeat 1 end-to-end",
            "Do not claim the fresh grouped_reduction hot-query ratios",
            "repeat-1 losses",
        ]:
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
