import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_grouped_reduction_m7_feasibility.py"
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.json"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.md"


class V3PhoenixGroupedReductionM7FeasibilityTest(unittest.TestCase):
    def load(self):
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def pairs(self):
        pairs = {}
        for scale in self.load()["scales"]:
            for pair in scale["pairs"]:
                pairs[(scale["generated_rows"], pair["mode"])] = pair
        return pairs

    def test_packet_is_feasibility_not_m7_promotion(self):
        payload = self.load()
        self.assertEqual(payload["status"], "grouped_reduction_m7_feasibility_not_promoted")
        self.assertEqual(payload["generic_capability"], "grouped_reduction")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promoted"])
        self.assertEqual(payload["m7_qualified_release_rows"], 0)
        self.assertEqual(payload["summary"]["scale_count"], 2)
        self.assertEqual(payload["summary"]["pair_count"], 4)
        self.assertTrue(payload["summary"]["all_cpu_reference_match"])
        self.assertTrue(payload["summary"]["all_optix_hot_faster"])
        self.assertTrue(payload["summary"]["any_sum_row_has_large_cold_cost"])
        self.assertIn("262144/sum", payload["summary"]["sum_rows_with_large_cold_cost"])
        self.assertIn("524288/sum", payload["summary"]["sum_rows_with_large_cold_cost"])

    def test_repeat_amortization_keeps_count_and_sum_honest(self):
        pairs = self.pairs()
        count_262k = pairs[(262144, "count")]
        sum_262k = pairs[(262144, "sum")]
        count_524k = pairs[(524288, "count")]
        sum_524k = pairs[(524288, "sum")]

        self.assertEqual(count_262k["break_even_repeat_count_ceiling"], 1)
        self.assertGreater(count_262k["repeat_scenarios"]["1"]["end_to_end_speedup"], 15.0)
        self.assertGreater(count_262k["hot_query_speedup_embree_over_optix"], 9.0)

        self.assertGreater(sum_262k["embree_workload_build_sec"], 100.0)
        self.assertGreater(sum_262k["max_workload_build_sec"], 100.0)
        self.assertIn("large_sum_workload_build_cost_must_be_prominent", sum_262k["m7_blockers"])

        self.assertGreater(count_524k["hot_query_speedup_embree_over_optix"], 8.0)
        self.assertGreater(count_524k["break_even_repeat_count"], 10.0)
        self.assertLess(count_524k["break_even_repeat_count"], 25.0)
        self.assertLess(count_524k["repeat_scenarios"]["1"]["end_to_end_speedup"], 1.0)
        self.assertGreater(count_524k["repeat_scenarios"]["100"]["end_to_end_speedup"], 2.0)
        self.assertIn("single_query_end_to_end_not_optix_win", count_524k["m7_blockers"])

        self.assertGreater(sum_524k["hot_query_speedup_embree_over_optix"], 100.0)
        self.assertGreater(sum_524k["min_workload_build_sec"], 200.0)
        self.assertGreater(sum_524k["repeat_scenarios"]["1"]["end_to_end_speedup"], 1.0)
        self.assertLess(sum_524k["repeat_scenarios"]["1"]["end_to_end_speedup"], 1.1)
        self.assertIn("large_sum_workload_build_cost_must_be_prominent", sum_524k["m7_blockers"])

    def test_every_pair_blocks_public_claims(self):
        for pair in self.pairs().values():
            self.assertFalse(pair["m7_promoted"])
            self.assertFalse(pair["release_authorized"])
            self.assertFalse(pair["public_speedup_claim_authorized"])
            self.assertTrue(pair["both_match_cpu_reference"])
            self.assertFalse(pair["embree_rt_core_accelerated"])
            self.assertTrue(pair["optix_rt_core_accelerated"])
            self.assertGreater(len(pair["m7_blockers"]), 0)
            self.assertEqual(pair["claim_status"], "internal_feasibility_not_m7")

    def test_source_warmup_asymmetry_is_recorded(self):
        scales = {scale["generated_rows"]: scale for scale in self.load()["scales"]}
        self.assertEqual(scales[262144]["source_warmup"], 1)
        self.assertEqual(scales[524288]["source_warmup"], 2)

    def test_script_rebuilds_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "grouped_reduction.json"
            md_out = Path(tmp) / "grouped_reduction.md"
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
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            rebuilt = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(rebuilt["summary"], self.load()["summary"])
            self.assertEqual(rebuilt["scales"], self.load()["scales"])
            self.assertIn("M7-qualified release rows: 0", md_out.read_text(encoding="utf-8"))

    def test_report_blocks_end_to_end_overclaim(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "feasibility packet, not M7 promotion",
            "release_authorized: false",
            "public_speedup_claim_authorized: false",
            "M7-qualified release rows: 0",
            "hot prepared-query wins are real",
            "Do not claim RayDB-style V3 is 158x faster end to end",
            "cold/setup and repeat-count policy are not yet a public contract",
            "warmup=1",
            "warmup=2",
            "the cheapest path can hide that the other baseline still pays a large cold/setup cost",
            "single_query_end_to_end_not_optix_win",
            "large_sum_workload_build_cost_must_be_prominent",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
