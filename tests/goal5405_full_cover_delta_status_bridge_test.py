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
    / "run_xhd_goal5405_full_cover_delta_status_bridge.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5405_full_cover_delta_status_bridge_pod.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5405_bridge", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5405FullCoverDeltaStatusBridgeTest(unittest.TestCase):
    def test_target_shape_is_56_plus_6_rows_per_active_from_prior_artifacts(self) -> None:
        module = _load_module()
        target = module.target_shape_from_prior_artifacts()
        self.assertEqual(target["selected_rows_per_active"], 56)
        self.assertEqual(target["missing_rows_per_active"], 6)
        self.assertEqual(target["author_rows_per_active"], 62)
        self.assertEqual(target["selected_surface_rows"], 24508120)
        self.assertEqual(target["missing_rows_to_author"], 2625870)
        self.assertTrue(target["goal5394_shape_matches_target"])

    def test_bounded_fixture_materializes_expected_full_cover_delta_shape(self) -> None:
        module = _load_module()
        fixture = module.bounded_full_cover_delta_fixture(active_count=2)
        expected = module.expected_columns_from_fixture(fixture)
        self.assertEqual(len(expected["cell_ids"]), 124)
        self.assertEqual(expected["cell_ids"][:3], [100000, 100001, 100002])
        self.assertEqual(expected["cell_ids"][55:58], [100055, 101000, 101001])
        self.assertEqual(expected["cell_ids"][112:115], [900000, 900001, 900002])
        self.assertEqual(expected["cell_ids"][-3:], [901003, 901004, 901005])
        self.assertEqual(expected["source_ids"][0], 11168)
        self.assertEqual(expected["source_ids"][56], 210712)
        self.assertEqual(expected["source_ids"][112], 11168)
        self.assertEqual(expected["status_codes"], [2] * 124)
        self.assertEqual(expected["transition_phase_codes"], [1] * 124)

    def test_multiround_reference_shape_matches_expected_rows(self) -> None:
        module = _load_module()
        fixture = module.bounded_full_cover_delta_fixture(active_count=2)
        shape = module._multiround_reference_shape(fixture)
        self.assertEqual(shape["contract"], "generic_active_query_multiround_status_reference_v1")
        self.assertEqual(shape["app_semantics"], "none")
        self.assertEqual(shape["expected_base_rows"], 112)
        self.assertEqual(shape["expected_delta_rows"], 12)
        self.assertEqual(shape["expected_total_rows"], 124)
        self.assertEqual(shape["raw_offload_rows_before_sort_reduce"], 124)
        self.assertEqual(shape["rounds"][0]["offload_row_count"], 112)
        self.assertEqual(shape["rounds"][1]["offload_row_count"], 12)

    def test_script_keeps_full_trace_claims_false(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("bounded_full_cover_delta_bridge_claimed", source)
        self.assertIn("full_goal5387_gate_authorized_by_goal5405", source)
        self.assertIn("goal5387_row_count_parity_claimed", source)
        self.assertIn("goal5387_hash_sample_parity_claimed", source)
        self.assertIn("full_xhd_paper_reproduction_claimed", source)

    def test_pod_artifact_if_present_passes_bounded_bridge_only(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal5405 POD artifact has not been generated yet")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal5405")
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["expected_rows"]["base_rows_per_active"], 56)
        self.assertEqual(payload["expected_rows"]["delta_rows_per_active"], 6)
        self.assertEqual(payload["expected_rows"]["total_rows_per_active"], 62)
        self.assertEqual(payload["expected_rows"]["expected_total_rows"], 124)
        for key in (
            "goal5394_shape_matches_target",
            "native_row_count_matched_expected",
            "native_hash_matched_expected",
            "native_sample_matched_expected",
            "native_status_count_matched_expected",
            "native_feedback_count_zero_matched",
            "native_current_best_after_matched",
            "multiround_reference_total_rows_matched",
            "overflow_fail_closed_matched",
        ):
            self.assertTrue(payload["comparisons"][key], key)
        self.assertFalse(payload["next_gate_decision"]["full_goal5387_gate_authorized_by_goal5405"])
        for key, value in payload["claim_boundary"].items():
            if key.endswith("_claimed") and key not in {
                "bounded_full_cover_delta_bridge_claimed",
                "generic_multiround_reference_shape_reused",
                "generic_native_status_state_smoke_reused",
            }:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
