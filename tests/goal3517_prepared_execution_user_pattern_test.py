from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
GOAL3511_ARTIFACT = ROOT / "docs" / "reports" / "goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json"


class Goal3517PreparedExecutionUserPatternTest(unittest.TestCase):
    def test_public_pattern_is_explicit_and_non_authorizing(self) -> None:
        pattern = rt.describe_prepared_execution_user_pattern()

        self.assertEqual(pattern["schema"], rt.PREPARED_EXECUTION_REPORT_VERSION)
        self.assertEqual(
            tuple(pattern["workflow"]),
            ("prepare", "pack_or_cache", "warm", "run_steady_state", "explain_timings"),
        )
        self.assertIn("partner", pattern["required_user_decisions"])
        self.assertFalse(pattern["automatic_partner_selection_allowed"])
        self.assertFalse(pattern["app_specific_engine_logic_allowed"])
        self.assertFalse(pattern["release_authorized"])
        self.assertFalse(pattern["public_speedup_claim_authorized"])
        self.assertFalse(pattern["rt_core_speedup_claim_authorized"])
        self.assertFalse(pattern["true_zero_copy_claim_authorized"])
        self.assertIn("RayJoin paper-reproduction", pattern["claim_boundary"])
        self.assertIn("full overlay", pattern["claim_boundary"])

    def test_goal3511_artifact_normalizes_all_required_phases(self) -> None:
        artifact = json.loads(GOAL3511_ARTIFACT.read_text(encoding="utf-8"))
        report = rt.prepared_execution_report_from_artifact(
            artifact,
            workflow_name="simple_polygon_overlay_area_prepared_execution",
            backend="optix",
        )
        payload = report.to_dict()
        validation = rt.validate_prepared_execution_report(report)

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(payload["schema"], rt.PREPARED_EXECUTION_REPORT_VERSION)
        self.assertEqual(payload["workflow_name"], "simple_polygon_overlay_area_prepared_execution")
        self.assertEqual(payload["explicit_backend"], "optix")
        self.assertEqual(payload["explicit_partner"], "cupy")
        self.assertEqual(payload["warmup_count"], 3)
        self.assertEqual(payload["source_goal"], 3511)
        self.assertTrue(payload["source_commit"].startswith("b156242b"))

        phases = {phase["phase"]: phase for phase in payload["phase_timings"]}
        for phase in rt.PREPARED_EXECUTION_REQUIRED_PHASES:
            with self.subTest(phase=phase):
                self.assertIn(phase, phases)

        self.assertAlmostEqual(
            phases["cache_load"]["seconds"],
            artifact["timing_sec"]["payload_cache_load"],
        )
        self.assertEqual(len(phases["warmup"]["repeat_seconds"]), 3)
        self.assertAlmostEqual(payload["summary_sec"]["setup"], phases["prepare"]["seconds"])
        self.assertAlmostEqual(payload["summary_sec"]["warmup"], phases["warmup"]["seconds"])
        self.assertLess(phases["steady_state_stream"]["seconds"], 0.005)
        self.assertLess(phases["executor"]["seconds"], 0.02)
        self.assertGreater(phases["validation"]["seconds"], 0.2)
        self.assertLess(payload["summary_sec"]["steady_state"], artifact["timing_sec"]["relation_discovery"])
        for field, value in payload["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)

    def test_runner_attaches_prepared_execution_report_to_future_artifacts(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "prepared_execution_report_from_artifact",
            '"prepared_execution_report"',
            "simple_polygon_overlay_area_prepared_execution",
            "Validation oracle time is separated from the steady-state execution path.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_validation_rejects_missing_phases_or_authorization(self) -> None:
        artifact = json.loads(GOAL3511_ARTIFACT.read_text(encoding="utf-8"))
        report = rt.prepared_execution_report_from_artifact(artifact, backend="optix").to_dict()

        missing_phase = dict(report)
        missing_phase["phase_timings"] = [
            phase for phase in report["phase_timings"] if phase["phase"] != "executor"
        ]
        self.assertEqual(rt.validate_prepared_execution_report(missing_phase)["status"], "reject")

        authorized = dict(report)
        authorized["public_speedup_claim_authorized"] = True
        self.assertEqual(rt.validate_prepared_execution_report(authorized)["status"], "reject")


if __name__ == "__main__":
    unittest.main()
