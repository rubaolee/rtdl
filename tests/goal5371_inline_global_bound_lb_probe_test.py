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
    / "build_xhd_goal5371_inline_global_bound_lb_probe.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5371_inline_global_bound_lb_probe.json"
)
PROBE_SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_cell_mbr_frontier_kind_count_probe.py"
)
PARTNER = ROOT / "src" / "rtdsl" / "partner_continuations.py"


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5371_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5371InlineGlobalBoundLbProbeTest(unittest.TestCase):
    def test_artifact_rejects_materialization_and_existing_global_bound_hypotheses(self) -> None:
        payload = _load_module().build_artifact()
        self.assertEqual(
            "inline_and_global_bound_lb_probes_ready__author_denominator_still_unmatched",
            payload["status"],
        )
        self.assertEqual(
            "inline_payload_and_existing_global_bound_do_not_explain_author_offloading_size",
            payload["exit_label"],
        )
        comparison = payload["comparison"]
        self.assertEqual(27_133_990, comparison["author_offloading_size_rows"])
        self.assertEqual(21_006_960, comparison["rtdl_author_radius_materialized_rows_from_goal5367"])
        self.assertEqual(304_981_889, comparison["rtdl_author_radius_noinline_raw_kind2_rows_from_goal5368"])
        self.assertEqual(21_006_960, comparison["rtdl_author_radius_inline_count_only_kind2_rows"])
        self.assertEqual(21_006_960, comparison["rtdl_author_radius_inline_global_bound_kind2_rows"])
        self.assertTrue(comparison["materialized_equals_inline_count_only"])
        self.assertFalse(comparison["global_bound_changed_kind2_rows"])
        self.assertFalse(comparison["row_count_parity"])
        self.assertAlmostEqual(0.7741935483870968, comparison["inline_div_author"])
        self.assertGreater(comparison["noinline_div_author"], 11.0)

    def test_probe_modes_and_claim_boundary_are_explicit(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        inline = payload["probe_results"]["inline_count_only"]
        self.assertTrue(inline["inline_nearest"])
        self.assertFalse(inline["global_bound_early_break"])
        self.assertTrue(inline["overflow_telemetry_only"])
        self.assertEqual(21_006_960, inline["raw_kind2_rows"])

        gb = payload["probe_results"]["inline_global_bound_count_only"]
        self.assertTrue(gb["inline_nearest"])
        self.assertTrue(gb["global_bound_early_break"])
        self.assertEqual(0, gb["global_bound_early_break_count"])
        self.assertEqual(21_006_960, gb["raw_kind2_rows"])

        claims = payload["claim_boundary"]
        self.assertTrue(claims["generic_probe_capability_claimed"])
        for key in (
            "explicit_lb_support_claimed",
            "row_count_parity_claimed",
            "same_denominator_memory_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "author_rt_core_algorithm_parity_claimed",
            "rtdl_author_performance_ratio_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertFalse(claims[key], key)

    def test_probe_frontdoor_exposes_inline_modes_and_overflow_telemetry_only_is_safe(self) -> None:
        script = PROBE_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("--inline-nearest", script)
        self.assertIn("--global-bound-early-break", script)
        self.assertIn("target_point_columns=target_columns if bool(args.inline_nearest) else None", script)
        self.assertIn("global_bound_early_break=bool(args.global_bound_early_break)", script)

        partner = PARTNER.read_text(encoding="utf-8")
        self.assertIn("inline_nearest_state_available = False", partner)
        self.assertIn("overflow_telemetry_only", partner)
        self.assertIn("inline_nearest_state_available", partner)


if __name__ == "__main__":
    unittest.main()
