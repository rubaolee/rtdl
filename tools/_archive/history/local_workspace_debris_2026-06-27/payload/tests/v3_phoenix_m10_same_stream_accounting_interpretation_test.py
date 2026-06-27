import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "phoenix_v3_m4_grouped_continuation_20260620"
RAW_M10 = ART / "m10_same_stream_65536.json"
INDEX = ART / "phoenix_v3_m4_evidence_index_2026-06-20.json"
PACKET_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m10_same_stream_accounting_interpretation_2026-06-20.json"
PACKET_MD = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m10_same_stream_accounting_interpretation_2026-06-20.md"


class V3PhoenixM10SameStreamAccountingInterpretationTest(unittest.TestCase):
    def payload(self):
        return json.loads(PACKET_JSON.read_text(encoding="utf-8"))

    def test_packet_keeps_m10_internal_and_unpromoted(self):
        payload = self.payload()
        self.assertEqual(payload["status"], "m10_same_stream_accounting_interpreted_not_release")
        self.assertEqual(payload["generic_capability"], "same_stream_partner_continuation_accounting")
        self.assertEqual(
            payload["current_packet_external_review_status"],
            "claude_approved_after_p0_p1_fixes_internal_note",
        )
        self.assertEqual(
            payload["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete_internal_not_m7",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["same_stream_public_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_public_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["phoenix_m7_qualified_release_rows"], 0)

    def test_raw_m4_index_classification_is_preserved(self):
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        m10 = {row["gate"]: row for row in index["rows"]}["M10"]
        self.assertFalse(m10["clean_pass"])
        self.assertEqual(m10["accounting_warning_count"], 1)
        self.assertEqual(m10["result_classification"], "pass_internal_with_accounting_warning")

        interpretation = self.payload()["interpretation"]
        self.assertEqual(interpretation["raw_index_classification_preserved"], "pass_internal_with_accounting_warning")
        self.assertFalse(interpretation["raw_index_clean_pass_preserved"])
        self.assertEqual(interpretation["event_ordering_interpretation"], "per_sample_event_ordering_clean")
        self.assertEqual(interpretation["median_accounting_interpretation"], "independent_median_non_additivity_note")
        self.assertIn("-0.128 microseconds", interpretation["why_this_is_not_an_event_ordering_failure"])
        self.assertIn("event pointer fields are 0", interpretation["numba_event_pointer_explanation"])
        self.assertIn("phoenix_m4_system_python_missing_cupy_numba", interpretation["system_python_binding_gap"])

    def test_raw_event_samples_are_per_sample_clean(self):
        raw = json.loads(RAW_M10.read_text(encoding="utf-8"))
        for row in raw["partner_rows"]:
            samples = row["event_samples"]
            self.assertEqual(len(samples), 5)
            bad = [
                sample
                for sample in samples
                if not (
                    sample["same_stream_ready"]
                    and sample["total_event_seconds"] >= sample["native_event_seconds"]
                    and sample["total_event_seconds"] >= sample["partner_event_seconds"]
                )
            ]
            self.assertEqual(bad, [], row["partner"])

    def test_partner_rows_distinguish_warning_from_event_failure(self):
        rows = {row["partner"]: row for row in self.payload()["partner_rows"]}
        self.assertEqual(set(rows), {"cupy", "numba"})
        self.assertEqual(rows["cupy"]["sample_count"], 5)
        self.assertEqual(rows["cupy"]["per_sample_bad_count"], 0)
        self.assertEqual(rows["cupy"]["raw_event_accounting_status"], "warning")
        self.assertLess(rows["cupy"]["independent_median_delta_seconds"], 0)
        self.assertLess(abs(rows["cupy"]["independent_median_delta_seconds"]), 1e-6)
        self.assertIn("independent median", rows["cupy"]["interpretation"])

        self.assertEqual(rows["numba"]["sample_count"], 5)
        self.assertEqual(rows["numba"]["per_sample_bad_count"], 0)
        self.assertEqual(rows["numba"]["raw_event_accounting_status"], "clean")
        self.assertGreater(rows["numba"]["independent_median_delta_seconds"], 0)
        self.assertIn("event pointer fields are 0", rows["numba"]["numba_event_pointer_explanation"])

        for row in rows.values():
            self.assertTrue(row["same_stream_ready"])
            self.assertFalse(row["true_zero_copy_ready"])
            self.assertFalse(row["transfer_counter_observed"])

    def test_report_and_boundaries_prevent_release_overclaim(self):
        payload = self.payload()
        for blocker in [
            "transfer_counter_evidence_missing_in_m10",
            "raw_m4_index_still_internal_not_m7",
            "public_same_stream_wording_review_missing",
            "system_python_binding_gap_open",
            "m7_row_level_release_review_missing",
        ]:
            self.assertIn(blocker, payload["m7_blockers"])
        forbidden = "\n".join(payload["hard_boundaries"])
        self.assertIn("Do not rewrite the raw M4 evidence index", forbidden)
        self.assertIn("Do not promote M10 to M7", forbidden)

        text = PACKET_MD.read_text(encoding="utf-8")
        for phrase in [
            "m10_same_stream_accounting_interpreted_not_release",
            "per_sample_event_ordering_clean",
            "independent_median_non_additivity_note",
            "pass_internal_with_accounting_warning",
            "clean_pass: false",
            "current_packet_2ai_consensus_status: claude_codex_consensus_complete_internal_not_m7",
            "current_packet_external_review_status: claude_approved_after_p0_p1_fixes_internal_note",
            "native_start_event_ptr",
            "phoenix_m4_system_python_missing_cupy_numba",
            "Phoenix M7-qualified release rows: 0",
            "Do not promote M10 to M7",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
