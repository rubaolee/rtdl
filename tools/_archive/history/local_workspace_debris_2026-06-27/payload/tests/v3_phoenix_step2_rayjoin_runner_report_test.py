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
    / "phoenix_v3_rayjoin_point_location_runner_pod_ab_20260622_175115"
    / "summary.json"
)
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_step2_rayjoin_point_location_runner_pod_ab_2026-06-22.md"
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_step2_rayjoin_point_location_runner_pod_ab_2026-06-22.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_step2_rayjoin_point_location_runner_review_2026-06-22.md"
)


class V3PhoenixStep2RayJoinRunnerReportTest(unittest.TestCase):
    def test_evidence_records_structural_runtime_without_material_gain(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        summary = payload["summary"]

        self.assertEqual(payload["status"], "rayjoin_point_location_runner_pod_ab_collected_not_release")
        self.assertEqual(payload["failed_checks"], [])
        self.assertEqual(summary["row_count"], 47262)
        self.assertAlmostEqual(
            summary["speedups"]["median_per_call_speedup_legacy_over_runner"],
            0.9734650006717721,
        )
        self.assertAlmostEqual(
            summary["speedups"]["median_total_repeat_speedup_legacy_over_runner"],
            0.9737541084926657,
        )
        self.assertFalse(summary["material_set_a_candidate"])
        self.assertFalse(summary["runtime_sourced_material_gain"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(summary["full_all_app_rerun_authorized_by_this_packet"])

        checks = payload["checks"]
        self.assertTrue(checks["runner_runtime_trunk_executes_all_samples"])
        self.assertTrue(checks["runner_internal_device_residency_all_samples"])
        self.assertTrue(checks["runner_hot_path_host_materialization_absent"])
        self.assertTrue(checks["all_claim_flags_false"])

    def test_report_and_review_request_preserve_no_go_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        call_for_review = CALL_FOR_REVIEW.read_text(encoding="utf-8")

        self.assertIn("step2_rayjoin_runner_executes_but_not_material_not_release", report)
        self.assertIn("0.973754x", report)
        self.assertIn("structural success and a performance no-go", report)
        self.assertIn("not against Embree", report)
        self.assertIn("Do not run all-app yet", report)
        self.assertIn("release gate remains `redo_required`", report)

        self.assertIn("0.9737541084926657x", call_for_review)
        self.assertIn("Material Set-A candidate: `false`", call_for_review)
        self.assertIn("Is any all-app pod run authorized now? My position: no.", call_for_review)
        self.assertIn("Explicit Non-Authorization", call_for_review)

        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        self.assertIn("step2_rayjoin_runner_executes_structural_only_not_material_not_release", claude)
        self.assertIn("not Embree", claude)
        self.assertIn("stopped as a material Set-A candidate", claude)
        self.assertIn("Barnes-Hut frontier/vector accumulation", claude)
        self.assertIn("No all-app pod run is authorized", claude)
        self.assertIn("does not lower the release bar", claude)


if __name__ == "__main__":
    unittest.main()
