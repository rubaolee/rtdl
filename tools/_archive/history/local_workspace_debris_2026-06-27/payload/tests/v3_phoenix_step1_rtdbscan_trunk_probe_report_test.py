from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_step1_rtdbscan_trunk_probe_20260622_211934"
    / "summary.json"
)
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "phoenix_v3_step1_rtdbscan_runtime_trunk_probe_pod_ab_2026-06-22.md"
)
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_step1_rtdbscan_runtime_trunk_probe_2026-06-22.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_step1_rtdbscan_runtime_trunk_probe_review_2026-06-22.md"
)
SCRIPT = ROOT / "scripts" / "v3_phoenix_rtdbscan_runner_m3_4_pod_ab.py"


class V3PhoenixStep1RtdbscanTrunkProbeReportTest(unittest.TestCase):
    def test_summary_records_execution_without_material_release_credit(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["status"],
            "rtdbscan_component_signature_runner_m3_4_pod_ab_collected_not_release",
        )
        self.assertAlmostEqual(payload["geomean_runner_vs_legacy_speedup"], 0.9948584784435961)
        self.assertAlmostEqual(payload["geomean_runner_vs_embree_speedup"], 2.927728873898229)
        self.assertTrue(payload["runtime_trunk_executes_all_runner_samples"])
        self.assertTrue(payload["internal_device_residency_all_runner_samples"])
        self.assertFalse(payload["hot_path_host_materialization_any_runner_sample"])
        self.assertFalse(payload["external_device_buffer_interop_any_runner_sample"])
        self.assertFalse(payload["v4_embedding_or_external_zero_copy_any_runner_sample"])
        self.assertFalse(payload["material_set_a_candidate"])
        self.assertFalse(payload["material_vs_incumbent_legacy_candidate"])
        self.assertTrue(payload["legacy_parity_recovered"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["full_all_app_rerun_authorized_by_this_packet"])

    def test_report_and_review_request_preserve_the_no_go_interpretation(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        call_for_review = CALL_FOR_REVIEW.read_text(encoding="utf-8")
        claude_review = CLAUDE_REVIEW.read_text(encoding="utf-8")

        self.assertIn("step1_trunk_executes_but_not_material_not_release", report)
        self.assertIn("Runner vs legacy OptiX grouped-stream geomean | `0.994858x`", report)
        self.assertIn("Legacy vs Embree control geomean | `2.942860x`", report)
        self.assertIn("Runner vs Embree control geomean | `2.927729x`", report)
        self.assertIn("does not create it", report)
        self.assertIn("not a material", report)
        self.assertIn("Do not count RTDBSCAN Step 1", report)
        self.assertIn("full\nall-app rerun", report)
        self.assertIn("Release remains `redo_required`", report)

        self.assertIn("runner_vs_legacy_geomean: 0.9948584784435961", call_for_review)
        self.assertIn("material_set_a_candidate: false", call_for_review)
        self.assertIn("Which next Set-A family", call_for_review)
        self.assertIn("all-app pod spend", call_for_review)

        self.assertIn("verdict: approve_blocked_not_release", claude_review)
        self.assertIn("Runner vs legacy OptiX grouped-stream is the correct incumbent", claude_review)
        self.assertIn("no use of RTDBSCAN\n`2.93x vs Embree`", claude_review)
        self.assertIn("RayJoin is the strongest next candidate", claude_review)

    def test_m3_4_script_emits_shared_step3_audit_fields(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("audit_prepared_execution_session_metadata", source)
        self.assertIn("runner_step3_audit_rows", source)
        self.assertIn("runner_step3_residency_default_ready_all_runner_samples", source)
        self.assertIn("step3_audit_missing_fields", source)
        self.assertIn("step3_residency_default_ready", source)
        self.assertIn(
            "and summary[\"runner_step3_residency_default_ready_all_runner_samples\"]",
            source,
        )


if __name__ == "__main__":
    unittest.main()
