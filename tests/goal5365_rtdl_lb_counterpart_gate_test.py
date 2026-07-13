from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5365_rtdl_lb_counterpart_gate.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5365_rtdl_lb_counterpart_gate.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5365_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5365RtdlLbCounterpartGateTest(unittest.TestCase):
    def test_lb_counterpart_behavior_gate_passes_but_does_not_authorize_lb(self) -> None:
        payload = _load_module().build_artifact()
        self.assertEqual(
            "rtdl_lb0_lb256_counterpart_behavior_gate_passed__row_count_denominator_not_parity",
            payload["status"],
        )
        comparison = payload["comparison"]
        self.assertTrue(comparison["matched"])
        self.assertTrue(comparison["input_match"])
        self.assertTrue(comparison["preprocessing_match"])
        self.assertTrue(comparison["value_match"])
        self.assertTrue(comparison["lb0_behavior_zero_offload"])
        self.assertTrue(comparison["lb256_behavior_positive_offload"])
        self.assertFalse(comparison["row_count_or_byte_parity_claimed"])
        self.assertFalse(comparison["performance_ratio_claimed"])

        decision = payload["decision"]
        self.assertTrue(decision["bounded_lb_behavior_gate_passed"])
        self.assertFalse(decision["explicit_lb_support_authorized_now"])
        self.assertIn("row counts / byte denominators are not equal", decision["reason_support_not_authorized"])

    def test_rtdl_counterparts_match_author_value_and_offload_signs(self) -> None:
        payload = _load_module().build_artifact()
        comparison = payload["comparison"]
        self.assertLessEqual(comparison["lb0_abs_diff"], comparison["tolerance"])
        self.assertLessEqual(comparison["lb256_abs_diff"], comparison["tolerance"])

        rtdl = payload["rtdl_counterparts"]
        lb0 = rtdl["lb0_disabled_offload"]
        lb256 = rtdl["lb256_heavy_offload"]
        self.assertEqual(4294967295, lb0["max_inline_points"])
        self.assertEqual(256, lb256["max_inline_points"])
        self.assertEqual(["translate_each_input_to_min_bound"], lb0["reference_preprocessing"])
        self.assertEqual(["translate_each_input_to_min_bound"], lb256["reference_preprocessing"])

        self.assertEqual(0, lb0["heavy_offload_peak_rows"])
        self.assertEqual(0, lb0["heavy_offload_queue_peak_bytes_generic_u64"])
        self.assertEqual(0, lb0["heavy_offload_queue_peak_bytes_author_u32_equivalent"])

        self.assertGreater(lb256["heavy_offload_peak_rows"], 0)
        self.assertGreater(lb256["heavy_offload_queue_peak_bytes_generic_u64"], 0)
        self.assertGreater(lb256["heavy_offload_queue_peak_bytes_author_u32_equivalent"], 0)
        self.assertGreater(lb256["nearest_continuation_sec"], 1.0)

    def test_saved_artifact_claim_boundary_is_false(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["comparison"]["matched"])
        self.assertIn("behavior_gate_passed", payload["exit_label"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)


if __name__ == "__main__":
    unittest.main()
