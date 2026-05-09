import json
import unittest
from pathlib import Path

from scripts import goal1610_v1_6_1_phase_copy_measurement as goal1610


ROOT = Path(__file__).resolve().parents[1]
FOUNDATION_REPORT = (
    ROOT / "docs" / "reports" / "goal1610_v1_6_1_phase_copy_measurement_foundation_2026-05-09.md"
)
CLAUDE_REVIEW = (
    ROOT / "docs" / "reviews" / "goal1610_v1_6_1_phase_copy_measurement_claude_review_2026-05-09.md"
)
GEMINI_REVIEW = (
    ROOT / "docs" / "reviews" / "goal1610_v1_6_1_phase_copy_measurement_gemini_review_2026-05-09.md"
)
CONSENSUS_REVIEW = (
    ROOT / "docs" / "reviews" / "goal1610_v1_6_1_phase_copy_measurement_3ai_consensus_2026-05-09.md"
)


class Goal1610PhaseCopyMeasurementTest(unittest.TestCase):
    def test_manifest_defines_required_schema_and_claim_boundary(self):
        manifest = goal1610.build_manifest()

        self.assertEqual(manifest["goal"], "Goal1610")
        self.assertEqual(manifest["version_slot"], "v1.6.1")
        self.assertIn("hausdorff_cpu_reference_smoke", manifest["cases"])
        self.assertEqual(tuple(manifest["phase_fields"]), goal1610.PHASE_FIELDS)
        self.assertEqual(tuple(manifest["copy_count_fields"]), goal1610.COPY_COUNT_FIELDS)

        case = manifest["cases"]["hausdorff_cpu_reference_smoke"]
        self.assertFalse(case["requires_pod"])
        self.assertFalse(case["requires_optix"])
        self.assertIn("cpu_python_reference", case["command"])

        for flag, value in manifest["claim_flags"].items():
            self.assertIs(value, False, flag)
        self.assertIn("does not authorize public speedup wording", manifest["claim_boundary"])
        self.assertIn("true zero-copy wording", manifest["claim_boundary"])

    def test_local_smoke_package_records_complete_phase_and_copy_shape(self):
        payload = goal1610.run_package(("hausdorff_cpu_reference_smoke",))

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["status"], "accepted_local_measurement_foundation")
        self.assertEqual(len(payload["records"]), 1)

        record = payload["records"][0]
        self.assertEqual(record["status"], "pass")
        self.assertEqual(record["backend"], "cpu_python_reference")
        self.assertTrue(record["parsed_app_status"]["json_detected"])
        self.assertTrue(record["parsed_app_status"]["matches_oracle"])

        phases = record["phase_times_sec"]
        self.assertEqual(tuple(phases.keys()), goal1610.PHASE_FIELDS)
        self.assertIsNotNone(phases["input_construction_sec"])
        self.assertIsNotNone(phases["query_and_materialize_sec"])
        self.assertIsNotNone(phases["validation_sec"])
        self.assertGreaterEqual(phases["total_wrapper_sec"], 0.0)

        counts = record["copy_counts"]
        self.assertEqual(tuple(counts.keys()), goal1610.COPY_COUNT_FIELDS)
        self.assertEqual(counts["input_materialization_count"], 4)
        self.assertEqual(counts["python_row_count"], 4)
        self.assertEqual(counts["output_materialization_count"], 4)

        for flag, value in record["claim_flags"].items():
            self.assertIs(value, False, flag)

    def test_markdown_and_json_payload_keep_scope_narrow(self):
        payload = goal1610.run_package(("hausdorff_cpu_reference_smoke",))
        markdown = goal1610.to_markdown(payload)
        encoded = json.dumps(payload, sort_keys=True)

        self.assertIn("ACCEPTED as local measurement-foundation evidence.", markdown)
        self.assertIn("Hardware: local only; no paid pod required", markdown)
        self.assertIn("Goal1610 defines local phase/copy measurement schema", markdown)
        self.assertIn("public_speedup_wording_authorized", encoded)
        self.assertIn('"true_zero_copy_authorized": false', encoded)

    def test_validator_rejects_negative_phases_and_claim_flag_expansion(self):
        payload = goal1610.run_package(("hausdorff_cpu_reference_smoke",))
        record = dict(payload["records"][0])
        record["phase_times_sec"] = dict(record["phase_times_sec"])
        record["copy_counts"] = dict(record["copy_counts"])
        record["claim_flags"] = dict(record["claim_flags"])

        record["phase_times_sec"]["total_wrapper_sec"] = -0.001
        with self.assertRaisesRegex(ValueError, "phase must be non-negative"):
            goal1610.validate_record(record, manifest=payload["manifest"])

        record["phase_times_sec"]["total_wrapper_sec"] = 0.0
        record["claim_flags"]["public_speedup_wording_authorized"] = True
        with self.assertRaisesRegex(ValueError, "claim flag must remain false"):
            goal1610.validate_record(record, manifest=payload["manifest"])

        del record["claim_flags"]
        with self.assertRaisesRegex(ValueError, "missing required metadata field: claim_flags"):
            goal1610.validate_record(record, manifest=payload["manifest"])

        record["claim_flags"] = {}
        with self.assertRaisesRegex(ValueError, "missing required flag"):
            goal1610.validate_record(record, manifest=payload["manifest"])

        record["claim_flags"] = dict(payload["records"][0]["claim_flags"])
        del record["status"]
        with self.assertRaisesRegex(ValueError, "missing required metadata field: status"):
            goal1610.validate_record(record, manifest=payload["manifest"])

    def test_foundation_report_is_present_and_names_default_artifacts(self):
        text = FOUNDATION_REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal1610 starts the `v1.6.1` measurement-foundation track.", text)
        self.assertIn("scripts/goal1610_v1_6_1_phase_copy_measurement.py", text)
        self.assertIn("tests/goal1610_v1_6_1_phase_copy_measurement_test.py", text)
        self.assertIn("goal1610_v1_6_1_phase_copy_measurement_smoke_2026-05-09.json", text)
        self.assertIn("This is a measurement foundation, not a performance claim.", text)

    def test_external_review_artifacts_record_acceptance(self):
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS_REVIEW.read_text(encoding="utf-8")

        self.assertIn("ACCEPTED", claude)
        self.assertIn("ACCEPTED", gemini)
        self.assertIn("ACCEPTED as a local phase/copy measurement foundation", consensus)
        self.assertIn("does not authorize performance claims", consensus)


if __name__ == "__main__":
    unittest.main()
