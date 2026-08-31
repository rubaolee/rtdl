from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5404_bounded_status_state_oracle_gate.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5404_bounded_status_state_oracle_gate_pod.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5404_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5404BoundedStatusStateOracleGateTest(unittest.TestCase):
    def test_bounded_fixture_expected_oracle_shape(self) -> None:
        module = _load_module()
        fixture = module.bounded_fixture_inputs()
        expected = module.expected_oracle_columns()
        telemetry = module.expected_telemetry()

        self.assertEqual(fixture["query_row_ids"].tolist(), [1010, 1011, 1012, 1013])
        self.assertEqual(fixture["candidate_query_row_ids"].tolist(), [1010, 1010, 1011, 1012, 1013, 1011])
        self.assertEqual(fixture["candidate_work_counts"].tolist(), [64, 4, 65, 17, 2, 80])
        self.assertEqual(fixture["heavy_threshold"], 16)
        self.assertEqual(expected["active_queue_indices"], [0, 2, 4, 2])
        self.assertEqual(expected["query_row_ids"], [1010, 1011, 1012, 1011])
        self.assertEqual(expected["source_ids"], [11168, 210712, 437119, 210712])
        self.assertEqual(expected["cell_ids"], [2924, 17, 18, 99])
        self.assertEqual(expected["current_best_before_sq"], [25.0, 16.0, 9.0, 16.0])
        self.assertEqual(expected["current_best_after_sq"], [20.0, 16.0, 9.0, 16.0])
        self.assertEqual(telemetry["raw_offload_row_count"], 4)
        self.assertEqual(telemetry["status_count_offloading"], 4)
        self.assertEqual(telemetry["feedback_update_count"], 2)

    def test_expected_trace_summary_is_deterministic_and_app_neutral(self) -> None:
        module = _load_module()
        summary = module._trace_summary(module.expected_oracle_columns())
        again = module._trace_summary(module.expected_oracle_columns())
        self.assertEqual(summary["row_count"], 4)
        self.assertEqual(summary["status_count_offloading"], 4)
        self.assertEqual(summary["active_query_count"], 4)
        self.assertEqual(summary["raw_offload_row_hash"], again["raw_offload_row_hash"])
        self.assertEqual(summary["samples"]["source_ids"], [11168, 437119, 210712])
        self.assertEqual(summary["samples"]["cell_ids"], [2924, 18, 99])
        self.assertEqual(summary["metadata"]["app_semantics"], "none")
        self.assertFalse(summary["metadata"]["explicit_app_option_support_claimed"])

    def test_script_keeps_full_trace_claims_false(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("bounded_status_state_oracle_claimed", source)
        self.assertIn("explicit_lb_support_claimed", source)
        self.assertIn("goal5387_row_count_parity_claimed", source)
        self.assertIn("goal5387_hash_sample_parity_claimed", source)
        self.assertIn("full_goal5387_gate_authorized_by_goal5404", source)
        self.assertIn("False", source)

    def test_pod_artifact_if_present_passes_bounded_oracle_only(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal5404 POD artifact has not been generated yet")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal5404")
        self.assertTrue(payload["matched"])
        comparisons = payload["comparisons"]
        for key in (
            "row_count_matched",
            "raw_hash_matched",
            "sample_matched",
            "status_count_offloading_matched",
            "feedback_update_count_matched",
            "current_best_after_matched",
            "overflow_fail_closed_matched",
        ):
            self.assertTrue(comparisons[key], key)
        self.assertEqual(payload["observed_telemetry"]["raw_offload_row_count"], 4)
        self.assertEqual(payload["observed_telemetry"]["feedback_update_count"], 2)
        self.assertTrue(payload["overflow_probe"]["raised"])
        self.assertFalse(payload["next_gate_decision"]["full_goal5387_gate_authorized_by_goal5404"])
        for key, value in payload["claim_boundary"].items():
            if key.endswith("_claimed") and key not in {
                "bounded_status_state_oracle_claimed",
                "generic_native_status_state_smoke_reused",
            }:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
