import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622"
)
SUMMARY = EVIDENCE_DIR / "summary.json"
REPORT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_prepared_execution_runner_repeat50_pod_evidence_2026-06-22.md"
)


class V3PhoenixRtnnPreparedExecutionRunnerRepeat50PodEvidenceTest(unittest.TestCase):
    def test_summary_records_focused_runtime_trunk_material_probe_not_release(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        summary = payload["summary"]

        self.assertEqual(
            summary["status"],
            "rtnn_prepared_execution_runner_repeat50_collected_not_release",
        )
        self.assertEqual(summary["point_count"], 1_048_576)
        self.assertEqual(summary["repeat"], 50)
        self.assertTrue(summary["runtime_trunk_executes_end_to_end"])
        self.assertTrue(summary["runtime_sourced_material_gain_candidate"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(summary["true_zero_copy_claim_authorized"])
        self.assertFalse(summary["full_all_app_rerun_authorized_by_this_packet"])
        self.assertEqual(payload["failed_checks"], [])

    def test_summary_keeps_signature_parity_and_three_timing_lenses(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        summary = payload["summary"]
        parity = summary["parity"]
        comparisons = summary["comparisons"]
        runner = summary["phase_rows"]["productized_prepared_execution_runner"]

        self.assertTrue(parity["runner_vs_legacy_signature_match"])
        self.assertTrue(parity["runner_vs_cupy_signature_match"])
        self.assertLessEqual(parity["runner_vs_cupy"]["sum_distance_relative_error"], 1.0e-4)
        self.assertEqual(runner["productized_execution_path"], "prepared_execution_session_runner")
        self.assertTrue(runner["runtime_trunk_executes_end_to_end"])
        self.assertTrue(runner["internal_device_residency_between_rtdl_phases"])
        self.assertTrue(runner["repeat50_material_probe_candidate"])
        self.assertGreater(comparisons["runner_over_cupy_hot_speedup"], 1.20)
        self.assertGreater(comparisons["runner_over_cupy_runner_wall_speedup"], 1.20)
        self.assertIn("runner_over_cupy_cold_plus_query_speedup", comparisons)
        self.assertIn("runner_vs_legacy_hot_speedup", comparisons)
        self.assertIn("runner_vs_legacy_cold_plus_query_speedup", comparisons)
        self.assertIn("runner_vs_legacy_runner_wall_speedup", comparisons)

    def test_report_documents_boundaries_and_result_paths(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "accepted_second_set_a_material_probe_not_release",
            "accept_as_second_set_a_material_probe",
            "not V3 release authorization",
            "not an all-app benchmark",
            "runtime_trunk_executes_end_to_end=true",
            "repeat50_material_probe_candidate=true",
            "Runner over CuPy hot query: `7.786920x`",
            "Runner over CuPy runner-wall: `3.196372x`",
            "Runner vs legacy runner-wall: `1.370176x`",
            "full_all_app_rerun_authorized_by_this_packet: false",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
