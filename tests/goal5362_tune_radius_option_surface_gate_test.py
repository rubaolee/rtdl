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
    / "build_xhd_goal5362_tune_radius_option_surface_gate.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5362_tune_radius_option_surface_gate.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5362_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5362TuneRadiusOptionSurfaceGateTest(unittest.TestCase):
    def test_adaptive_tune_radius_is_narrowly_supported_for_nonterminal_trace(self) -> None:
        payload = _load_module().build_artifact()
        self.assertEqual("narrow_internal_adaptive_tune_radius_mapping_passed", payload["status"])
        self.assertTrue(payload["comparison"]["matched"])
        self.assertTrue(payload["comparison"]["adaptive_supported"])
        self.assertTrue(payload["comparison"]["fail_closed_controls_matched"])

        adaptive = payload["adaptive_supported_case"]
        self.assertEqual(0, adaptive["exit_code"])
        self.assertLessEqual(adaptive["hd_abs_diff"], payload["comparison"]["tolerance"])
        self.assertEqual(["translate_each_input_to_min_bound"], adaptive["preprocessing_contract"])
        self.assertTrue(adaptive["row_comparison"]["matched"])
        self.assertEqual(2, len(adaptive["rtdl_rows"]))
        self.assertEqual(5205, adaptive["rtdl_rows"][0]["NumInputPoints"])
        self.assertEqual(4, adaptive["rtdl_rows"][0]["NumOutputPoints"])
        self.assertEqual(4, adaptive["rtdl_rows"][1]["NumInputPoints"])
        self.assertEqual(0, adaptive["rtdl_rows"][1]["NumOutputPoints"])

        surface = adaptive["author_rt_option_surface"]
        self.assertEqual("explicit_author_rt_options_supported_for_internal_diagnostic_route", surface["status"])
        self.assertEqual(["tune_radius"], surface["explicit_author_rt_options"])
        self.assertEqual(["tune_radius"], surface["supported_explicit_author_rt_options"])
        self.assertEqual([], surface["unsupported_explicit_author_rt_options"])
        self.assertTrue(surface["all_explicit_author_rt_options_supported"])
        self.assertEqual(
            "supported_internal_cell_mbr_author_queue_diagnostic_nonterminal_trace",
            surface["options"]["tune_radius"]["current_rtdl_support_status"],
        )
        self.assertEqual("radius_growth_step(mode=adaptive)", surface["options"]["tune_radius"]["mapped_to_rtdl_control"])

        metadata = adaptive["radius_trace_metadata"]
        self.assertTrue(metadata["uses_radius_growth_step"])
        self.assertTrue(metadata["author_tune_radius_supported"])
        self.assertIn("Internal diagnostic route only", metadata["author_tune_radius_support_scope"])

    def test_unsupported_modes_and_options_still_fail_closed(self) -> None:
        payload = _load_module().build_artifact()
        controls = payload["fail_closed_controls"]

        double_mode = controls["double_mode"]
        self.assertEqual(2, double_mode["exit_code"])
        self.assertEqual("unsupported_author_rt_options_fail_closed", double_mode["status"])
        self.assertEqual(["tune_radius"], double_mode["explicit_author_rt_options"])
        self.assertEqual(["tune_radius"], double_mode["unsupported_explicit_author_rt_options"])
        self.assertFalse(double_mode["route_executed"])

        terminal = controls["terminal_trace_adaptive"]
        self.assertEqual(2, terminal["exit_code"])
        self.assertEqual("unsupported_author_rt_options_fail_closed", terminal["status"])
        self.assertEqual(["tune_radius"], terminal["explicit_author_rt_options"])
        self.assertEqual(["tune_radius"], terminal["unsupported_explicit_author_rt_options"])
        self.assertFalse(terminal["route_executed"])

        lb = controls["other_author_rt_option_lb"]
        self.assertEqual(2, lb["exit_code"])
        self.assertEqual("unsupported_author_rt_options_fail_closed", lb["status"])
        self.assertEqual(["lb", "tune_radius"], sorted(lb["explicit_author_rt_options"]))
        self.assertEqual(["tune_radius"], lb["supported_explicit_author_rt_options"])
        self.assertEqual(["lb"], lb["unsupported_explicit_author_rt_options"])
        self.assertFalse(lb["route_executed"])

    def test_saved_artifact_preserves_claim_boundary(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["comparison"]["matched"])
        self.assertIn("narrow_internal_adaptive_tune_radius", payload["exit_label"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)


if __name__ == "__main__":
    unittest.main()
