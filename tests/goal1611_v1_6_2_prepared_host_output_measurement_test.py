import json
import unittest
from pathlib import Path

from scripts import goal1610_v1_6_1_phase_copy_measurement as goal1610
from scripts import goal1611_v1_6_2_prepared_host_output_measurement as goal1611


ROOT = Path(__file__).resolve().parents[1]
FOUNDATION_REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal1611_v1_6_2_prepared_host_output_measurement_foundation_2026-05-09.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal1611_v1_6_2_prepared_host_output_measurement_claude_review_2026-05-09.md"
)
GEMINI_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal1611_v1_6_2_prepared_host_output_measurement_gemini_review_2026-05-09.md"
)
CONSENSUS_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal1611_v1_6_2_prepared_host_output_measurement_3ai_consensus_2026-05-09.md"
)


class Goal1611PreparedHostOutputMeasurementTest(unittest.TestCase):
    def test_manifest_reuses_goal1610_schema_and_keeps_claims_closed(self):
        manifest = goal1611.build_manifest()

        self.assertEqual(manifest["goal"], "Goal1611")
        self.assertEqual(manifest["version_slot"], "v1.6.2")
        self.assertEqual(tuple(manifest["phase_fields"]), goal1610.PHASE_FIELDS)
        self.assertEqual(tuple(manifest["copy_count_fields"]), goal1610.COPY_COUNT_FIELDS)
        self.assertIn("collect_k_fake_prepared_host_output_smoke", manifest["cases"])
        self.assertFalse(manifest["cases"]["collect_k_fake_prepared_host_output_smoke"]["requires_pod"])
        self.assertFalse(manifest["cases"]["collect_k_fake_prepared_host_output_smoke"]["requires_optix"])
        self.assertIn("deterministic fake native symbol", manifest["claim_boundary"])

        for flag, value in manifest["claim_flags"].items():
            self.assertIs(value, False, flag)

    def test_local_preflight_records_materialization_delta_and_buffer_reuse(self):
        payload = goal1611.run_package(unique_rows=8, repeats=2, iterations=3)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["status"], "accepted_local_prepared_host_output_preflight")
        self.assertEqual(len(payload["records"]), 1)

        record = payload["records"][0]
        self.assertEqual(record["status"], "pass")
        self.assertEqual(record["backend"], "fake_native")
        self.assertEqual(record["candidate_row_count"], 16)

        phases = record["phase_times_sec"]
        self.assertEqual(tuple(phases.keys()), goal1610.PHASE_FIELDS)
        self.assertIsNotNone(phases["input_construction_sec"])
        self.assertIsNotNone(phases["probe_packing_sec"])
        self.assertIsNotNone(phases["launch_sec"])
        self.assertGreaterEqual(phases["total_wrapper_sec"], 0.0)

        counts = record["copy_counts"]
        self.assertEqual(tuple(counts.keys()), goal1610.COPY_COUNT_FIELDS)
        self.assertEqual(counts["input_materialization_count"], 3)
        self.assertEqual(counts["output_materialization_count"], 3)
        self.assertEqual(counts["host_to_device_copy_count"], 0)
        self.assertEqual(counts["device_to_host_copy_count"], 0)
        self.assertEqual(counts["python_row_count"], 16)
        self.assertEqual(counts["prepared_buffer_reuse_count"], 3)

        comparison = record["path_comparison"]
        self.assertEqual(comparison["baseline_input_materialization_count"], 3)
        self.assertEqual(comparison["prepared_input_materialization_count"], 1)
        self.assertEqual(comparison["input_materialization_count_delta"], 2)
        self.assertTrue(comparison["prepared_host_output_buffer_reused"])
        self.assertTrue(comparison["stable_typed_input_buffer_address"])
        self.assertTrue(comparison["timing_recorded_for_diagnostics_only"])

    def test_validator_rejects_claim_expansion_and_missing_path_comparison(self):
        payload = goal1611.run_package(unique_rows=8, repeats=2, iterations=3)
        record = dict(payload["records"][0])
        record["phase_times_sec"] = dict(record["phase_times_sec"])
        record["copy_counts"] = dict(record["copy_counts"])
        record["claim_flags"] = dict(record["claim_flags"])
        record["path_comparison"] = dict(record["path_comparison"])

        record["claim_flags"]["public_speedup_wording_authorized"] = True
        with self.assertRaisesRegex(ValueError, "claim flag must remain false"):
            goal1611.validate_record(record, manifest=payload["manifest"])

        record["claim_flags"]["public_speedup_wording_authorized"] = False
        del record["path_comparison"]
        with self.assertRaisesRegex(ValueError, "missing path_comparison"):
            goal1611.validate_record(record, manifest=payload["manifest"])

    def test_validator_rejects_path_comparison_regressions(self):
        payload = goal1611.run_package(unique_rows=8, repeats=2, iterations=3)
        record = dict(payload["records"][0])
        record["phase_times_sec"] = dict(record["phase_times_sec"])
        record["copy_counts"] = dict(record["copy_counts"])
        record["claim_flags"] = dict(record["claim_flags"])
        record["path_comparison"] = dict(record["path_comparison"])

        record["path_comparison"]["input_materialization_count_delta"] = -1
        with self.assertRaisesRegex(ValueError, "must be non-negative"):
            goal1611.validate_record(record, manifest=payload["manifest"])

        record["path_comparison"]["input_materialization_count_delta"] = 2
        record["path_comparison"]["timing_recorded_for_diagnostics_only"] = False
        with self.assertRaisesRegex(ValueError, "diagnostic only"):
            goal1611.validate_record(record, manifest=payload["manifest"])

        record["path_comparison"]["timing_recorded_for_diagnostics_only"] = True
        record["path_comparison"]["prepared_host_output_buffer_reused"] = False
        with self.assertRaisesRegex(ValueError, "output buffer must be reused"):
            goal1611.validate_record(record, manifest=payload["manifest"])

    def test_markdown_and_json_keep_scope_narrow(self):
        payload = goal1611.run_package(unique_rows=8, repeats=2, iterations=3)
        markdown = goal1611.to_markdown(payload)
        encoded = json.dumps(payload, sort_keys=True)

        self.assertIn("ACCEPTED as local prepared-host-output measurement preflight.", markdown)
        self.assertIn("real Embree/OptiX evidence must be collected separately", markdown)
        self.assertIn("does not authorize performance claims", encoded)
        self.assertIn('"true_zero_copy_authorized": false', encoded)

    def test_foundation_report_names_runner_and_boundaries(self):
        text = FOUNDATION_REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal1611 starts the `v1.6.2` prepared host-output measurement track.", text)
        self.assertIn("scripts/goal1611_v1_6_2_prepared_host_output_measurement.py", text)
        self.assertIn("tests/goal1611_v1_6_2_prepared_host_output_measurement_test.py", text)
        self.assertIn("fake native symbol is deliberate", text)
        self.assertIn("not a performance claim", text)

    def test_external_review_artifacts_record_acceptance(self):
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS_REVIEW.read_text(encoding="utf-8")

        self.assertIn("ACCEPTED", claude)
        self.assertIn("ACCEPTED", gemini)
        self.assertIn("ACCEPTED as a local prepared host-output measurement preflight", consensus)
        self.assertIn("does not authorize performance claims", consensus)


if __name__ == "__main__":
    unittest.main()
