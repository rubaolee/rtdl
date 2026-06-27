import json
import unittest
from pathlib import Path

from scripts import v3_phoenix_grouped_reduction_sum_m7_candidate_wording as wording


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.json"
PACKET_MD = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.md"
ACTUAL_DIR = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "phoenix_v3_grouped_reduction_repeat100_actual_20260620"
CLEAN_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_grouped_reduction_repeat100_actual_524288_clean_20260620"
)
SCALAR_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_grouped_reduction_scalar_broadcast_repeat100_20260620"
)


class V3PhoenixGroupedReductionSumM7CandidateWordingTest(unittest.TestCase):
    def payload(self):
        return json.loads(PACKET_JSON.read_text(encoding="utf-8"))

    def test_packet_is_actual_repeat100_sum_only_not_release(self):
        payload = self.payload()
        self.assertEqual(payload["status"], "sum_only_actual_repeat100_candidate_wording_not_release")
        self.assertEqual(payload["source_contract_status"], "prepared_query_contract_draft_not_release")
        self.assertEqual(payload["actual_repeat100_evidence_status"], "ok")
        self.assertEqual(payload["actual_repeat100_clean_override_rows"], [524288])
        self.assertEqual(payload["actual_repeat100_scalar_broadcast_override_rows"], [262144, 524288])
        self.assertIn("524288_clean", payload["source_actual_repeat100_clean_evidence_dir"])
        self.assertIn("scalar_broadcast_repeat100", payload["source_actual_repeat100_scalar_broadcast_evidence_dir"])
        self.assertTrue(payload["supersedes_modeled_repeat100_packet"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["current_packet_external_review_status"], "blocked_current_packet")
        self.assertEqual(payload["current_packet_2ai_consensus_status"], "not_recorded_for_this_packet")
        self.assertIn(
            "external_review_blocked_phoenix_v3_grouped_reduction_scalar_broadcast_optimization",
            payload["external_review_blockage"],
        )
        self.assertEqual(payload["m7_candidate_rows"], 2)
        self.assertEqual(payload["m7_qualified_release_rows"], 0)

    def test_actual_repeat100_artifacts_are_present_and_claim_gated(self):
        for name in [
            "gpu_env_gate.json",
            "optix_hardware_gate.json",
            "grouped_sum_repeat100_actual_262144.json",
            "grouped_sum_repeat100_actual_524288.json",
            "repeat100_actual.log",
            "repeat100_actual.status",
            "source_manifest.sha256",
        ]:
            self.assertTrue((ACTUAL_DIR / name).exists(), name)
        status = (ACTUAL_DIR / "repeat100_actual.status").read_text(encoding="utf-8").strip()
        self.assertEqual(status, "ok")
        for name in ["grouped_sum_repeat100_actual_262144.json", "grouped_sum_repeat100_actual_524288.json"]:
            raw = json.loads((ACTUAL_DIR / name).read_text(encoding="utf-8"))
            self.assertEqual(raw["status"], "ok")
            self.assertFalse(raw["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertTrue(raw["comparison"]["all_match_cpu_reference"])
            rows = {row["backend"]: row for row in raw["rows"]}
            self.assertEqual(rows["embree"]["repeat"], 100)
            self.assertEqual(rows["optix"]["repeat"], 100)
        for name in [
            "gpu_env_gate.json",
            "optix_hardware_gate.json",
            "grouped_sum_repeat100_actual_524288_clean.json",
            "repeat100_524288_clean.log",
            "repeat100_524288_clean.status",
            "source_manifest.sha256",
        ]:
            self.assertTrue((CLEAN_DIR / name).exists(), name)
        clean_status = (CLEAN_DIR / "repeat100_524288_clean.status").read_text(encoding="utf-8").strip()
        self.assertEqual(clean_status, "ok")
        clean_raw = json.loads((CLEAN_DIR / "grouped_sum_repeat100_actual_524288_clean.json").read_text(encoding="utf-8"))
        self.assertEqual(clean_raw["status"], "ok")
        self.assertTrue(clean_raw["comparison"]["all_match_cpu_reference"])
        self.assertFalse(clean_raw["claim_boundary"]["public_speedup_claim_authorized"])
        for name in [
            "gpu_env_gate.json",
            "optix_hardware_gate.json",
            "grouped_sum_scalar_broadcast_repeat100_262144.json",
            "grouped_sum_scalar_broadcast_repeat100_524288.json",
            "repeat100_scalar_broadcast.log",
            "repeat100_scalar_broadcast.status",
            "source_manifest.sha256",
        ]:
            self.assertTrue((SCALAR_DIR / name).exists(), name)
        scalar_status = (SCALAR_DIR / "repeat100_scalar_broadcast.status").read_text(encoding="utf-8").strip()
        self.assertEqual(scalar_status, "ok")
        for name in ["grouped_sum_scalar_broadcast_repeat100_262144.json", "grouped_sum_scalar_broadcast_repeat100_524288.json"]:
            raw = json.loads((SCALAR_DIR / name).read_text(encoding="utf-8"))
            self.assertEqual(raw["status"], "ok")
            self.assertTrue(raw["comparison"]["all_match_cpu_reference"])
            self.assertFalse(raw["claim_boundary"]["public_speedup_claim_authorized"])

    def test_only_sum_rows_are_candidate_rows_and_count_rows_remain_internal(self):
        payload = self.payload()
        self.assertEqual({row["operation"] for row in payload["rows"]}, {"group_sum_i64"})
        self.assertEqual({row["generated_rows"] for row in payload["rows"]}, {262144, 524288})
        row_ids = {row["row_id"] for row in payload["rows"]}
        self.assertIn("grouped_reduction_sum_scalar_broadcast_repeat100_262144", row_ids)
        self.assertIn("grouped_reduction_sum_scalar_broadcast_repeat100_524288", row_ids)
        self.assertEqual(len(payload["excluded_rows"]), 2)
        for row in payload["excluded_rows"]:
            self.assertIn("count row kept internal", row["reason"])
            self.assertEqual(row["break_even_repeat_count_ceiling"], 14)
            self.assertFalse(row["m7_promoted"])

    def test_actual_repeat100_numbers_replace_modeled_candidate_numbers(self):
        rows = {row["generated_rows"]: row for row in self.payload()["rows"]}
        self.assertGreater(rows[262144]["actual_repeat100_loop_speedup"], 200.0)
        self.assertGreater(rows[262144]["actual_repeat100_cold_plus_loop_speedup"], 27.5)
        self.assertGreater(rows[524288]["actual_repeat100_loop_speedup"], 155.0)
        self.assertLess(rows[524288]["actual_repeat100_cold_plus_loop_speedup"], 3.0)
        self.assertGreater(rows[524288]["actual_repeat100_cold_plus_loop_speedup"], 2.9)
        self.assertIn("scalar_broadcast_repeat100", rows[262144]["source_actual_file"])
        self.assertIn("scalar_broadcast_repeat100", rows[524288]["source_actual_file"])
        self.assertIn("large_cold_prepare_cost_limits_public_claim", rows[524288]["blockers"])
        for row in rows.values():
            self.assertTrue(row["actual_evidence_supersedes_modeled_value"])
            self.assertFalse(row["m7_promoted"])
            self.assertIn("actual repeat=100", row["draft_public_wording_not_publishable"])
            self.assertIn("not publishable", row["draft_public_wording_not_publishable"])

    def test_forbidden_wording_blocks_old_model_and_broad_claims(self):
        payload = self.payload()
        forbidden = "\n".join(payload["forbidden_public_wording"])
        self.assertIn("V3 is 224x faster", forbidden)
        self.assertIn("RTDL is 33x faster end to end", forbidden)
        self.assertIn("repeat 100 is only modeled", forbidden)
        rules = "\n".join(payload["public_copy_rules"])
        self.assertIn("Say actual repeat 100", rules)
        self.assertIn("Use the scalar-broadcast optimized repeat100 rerun", rules)
        self.assertIn("Do not quote the older modeled repeat 100 values", rules)
        self.assertIn("Keep whole-app and whole-database speedup unauthorized", rules)

    def test_markdown_contains_actual_repeat100_and_cold_cost_tables(self):
        text = PACKET_MD.read_text(encoding="utf-8")
        for phrase in [
            "actual repeat100 sum-only M7 candidate wording",
            "superseded by actual repeat100 pod",
            "Clean rerun source for the 524,288-row candidate",
            "Current scalar-broadcast optimized repeat100 source",
            "Actual repeat100 loop",
            "Actual cold plus loop",
            "Cold prepare is part of the user contract",
            "must not be quoted as a 33x",
            "Phoenix M7-qualified release rows: 0",
            "current_packet_external_review_status: blocked_current_packet",
            "current_packet_2ai_consensus_status: not_recorded_for_this_packet",
            "Do not claim: RTDL is 33x faster end to end",
            "grouped_reduction_sum_scalar_broadcast_repeat100_262144",
        ]:
            self.assertIn(phrase, text)

    def test_generator_reproduces_saved_packet_shape(self):
        generated = wording.build_payload()
        current = self.payload()
        self.assertEqual(generated["status"], current["status"])
        self.assertEqual(generated["rows"], current["rows"])
        self.assertEqual(generated["excluded_rows"], current["excluded_rows"])


if __name__ == "__main__":
    unittest.main()
