import json
import unittest
from pathlib import Path

from scripts import goal1610_v1_6_1_phase_copy_measurement as goal1610
from scripts import goal1612_v1_6_3_backend_prepared_host_output_bridge as goal1612


ROOT = Path(__file__).resolve().parents[1]
FOUNDATION_REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal1612_v1_6_3_backend_prepared_host_output_bridge_foundation_2026-05-09.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal1612_v1_6_3_backend_prepared_host_output_bridge_claude_review_2026-05-09.md"
)
GEMINI_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal1612_v1_6_3_backend_prepared_host_output_bridge_gemini_review_2026-05-09.md"
)
CONSENSUS_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal1612_v1_6_3_backend_prepared_host_output_bridge_3ai_consensus_2026-05-09.md"
)


class Goal1612BackendPreparedHostOutputBridgeTest(unittest.TestCase):
    def test_manifest_reuses_goal1610_schema_and_keeps_claims_closed(self):
        manifest = goal1612.build_manifest()

        self.assertEqual(manifest["goal"], "Goal1612")
        self.assertEqual(manifest["version_slot"], "v1.6.3")
        self.assertEqual(tuple(manifest["phase_fields"]), goal1610.PHASE_FIELDS)
        self.assertEqual(tuple(manifest["copy_count_fields"]), goal1610.COPY_COUNT_FIELDS)
        self.assertEqual(tuple(manifest["supported_backends"]), ("fake_native", "embree", "optix"))
        self.assertIn("does not authorize performance claims", manifest["claim_boundary"])
        for flag, value in manifest["claim_flags"].items():
            self.assertIs(value, False, flag)

    def test_fake_backend_records_materialization_delta(self):
        payload = goal1612.run_package(
            backends=("fake_native",),
            required_backends=("fake_native",),
            unique_rows=8,
            repeats=2,
            iterations=3,
        )

        self.assertTrue(payload["accepted"])
        record = payload["records"][0]
        self.assertEqual(record["status"], "pass")
        self.assertEqual(record["backend"], "fake_native")
        self.assertEqual(record["candidate_row_count"], 16)
        self.assertEqual(tuple(record["phase_times_sec"].keys()), goal1610.PHASE_FIELDS)
        self.assertEqual(tuple(record["copy_counts"].keys()), goal1610.COPY_COUNT_FIELDS)
        self.assertEqual(record["copy_counts"]["input_materialization_count"], 3)
        self.assertEqual(record["copy_counts"]["prepared_buffer_reuse_count"], 3)
        self.assertEqual(record["path_comparison"]["prepared_input_materialization_count"], 1)
        self.assertEqual(record["path_comparison"]["input_materialization_count_delta"], 2)
        self.assertTrue(record["path_comparison"]["prepared_host_output_buffer_reused"])
        self.assertTrue(record["path_comparison"]["timing_recorded_for_diagnostics_only"])

    def test_optional_unavailable_backend_can_skip_without_rejecting_package(self):
        payload = goal1612.run_package(
            backends=("fake_native", "optix"),
            required_backends=("fake_native",),
            unique_rows=8,
            repeats=2,
            iterations=3,
            backend_libraries={"optix": object()},
        )

        self.assertTrue(payload["accepted"])
        by_backend = {record["backend"]: record for record in payload["records"]}
        self.assertEqual(by_backend["optix"]["status"], "skipped")
        self.assertIn("does not export", by_backend["optix"]["skip_reason"])
        self.assertEqual(payload["skipped_required"], ())

    def test_required_backend_skip_rejects_package(self):
        payload = goal1612.run_package(
            backends=("optix",),
            required_backends=("optix",),
            unique_rows=8,
            repeats=2,
            iterations=3,
            backend_libraries={"optix": object()},
        )

        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["status"], "not_accepted")
        self.assertEqual(len(payload["skipped_required"]), 1)
        self.assertEqual(payload["records"][0]["status"], "skipped")

    def test_unexpected_backend_error_is_recorded_as_failure(self):
        class _ExplodingSymbol:
            def __call__(self, *_args):
                raise RuntimeError("boom")

        library = type("BadLibrary", (), {"rtdl_fake_collect_k_bounded_i64": _ExplodingSymbol()})()
        payload = goal1612.run_package(
            backends=("fake_native",),
            required_backends=("fake_native",),
            unique_rows=8,
            repeats=2,
            iterations=3,
            backend_libraries={"fake_native": library},
        )

        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["records"][0]["status"], "fail")
        self.assertIn("RuntimeError: boom", payload["records"][0]["error"])
        self.assertEqual(len(payload["failed"]), 1)

    def test_validator_rejects_claim_and_path_comparison_regressions(self):
        payload = goal1612.run_package(
            backends=("fake_native",),
            required_backends=("fake_native",),
            unique_rows=8,
            repeats=2,
            iterations=3,
        )
        record = dict(payload["records"][0])
        record["phase_times_sec"] = dict(record["phase_times_sec"])
        record["copy_counts"] = dict(record["copy_counts"])
        record["claim_flags"] = dict(record["claim_flags"])
        record["path_comparison"] = dict(record["path_comparison"])

        record["claim_flags"]["public_speedup_wording_authorized"] = True
        with self.assertRaisesRegex(ValueError, "claim flag must remain false"):
            goal1612.validate_record(record, manifest=payload["manifest"])

        record["claim_flags"]["public_speedup_wording_authorized"] = False
        record["path_comparison"]["input_materialization_count_delta"] = -1
        with self.assertRaisesRegex(ValueError, "must be non-negative"):
            goal1612.validate_record(record, manifest=payload["manifest"])

        record["path_comparison"]["input_materialization_count_delta"] = 2
        record["path_comparison"]["timing_recorded_for_diagnostics_only"] = False
        with self.assertRaisesRegex(ValueError, "diagnostic only"):
            goal1612.validate_record(record, manifest=payload["manifest"])

        record["path_comparison"]["timing_recorded_for_diagnostics_only"] = True
        record["path_comparison"]["prepared_host_output_buffer_reused"] = False
        with self.assertRaisesRegex(ValueError, "output buffer must be reused"):
            goal1612.validate_record(record, manifest=payload["manifest"])

    def test_markdown_and_json_keep_scope_narrow(self):
        payload = goal1612.run_package(
            backends=("fake_native",),
            required_backends=("fake_native",),
            unique_rows=8,
            repeats=2,
            iterations=3,
        )
        markdown = goal1612.to_markdown(payload)
        encoded = json.dumps(payload, sort_keys=True)

        self.assertIn("ACCEPTED as backend bridge evidence.", markdown)
        self.assertIn("Real backend skips are allowed only when the backend is not required.", markdown)
        self.assertIn("does not authorize performance claims", encoded)
        self.assertIn('"true_zero_copy_authorized": false', encoded)

    def test_foundation_report_names_runner_and_boundaries(self):
        text = FOUNDATION_REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal1612 starts the `v1.6.3` backend bridge", text)
        self.assertIn("scripts/goal1612_v1_6_3_backend_prepared_host_output_bridge.py", text)
        self.assertIn("tests/goal1612_v1_6_3_backend_prepared_host_output_bridge_test.py", text)
        self.assertIn("Real backends may skip locally", text)
        self.assertIn("does not authorize", text)

    def test_external_review_artifacts_record_acceptance(self):
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS_REVIEW.read_text(encoding="utf-8")

        self.assertIn("ACCEPTED", claude)
        self.assertIn("ACCEPTED", gemini)
        self.assertIn("ACCEPTED as backend bridge evidence", consensus)
        self.assertIn("does not authorize performance claims", consensus)


if __name__ == "__main__":
    unittest.main()
