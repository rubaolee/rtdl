from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5392_lb_denominator_surface_reconciliation.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5392_lb_denominator_surface_reconciliation.json"
)


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_xhd_goal5392_lb_denominator_surface_reconciliation",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5392LbDenominatorSurfaceReconciliationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_builder()
        cls.artifact = cls.module.build(output=ARTIFACT)

    def _surface(self, name: str) -> dict:
        for surface in self.artifact["surfaces"]:
            if surface["name"] == name:
                return surface
        self.fail(f"missing surface {name}")

    def test_surface_table_preserves_author_and_known_rtdl_denominators(self) -> None:
        payload = self.artifact
        self.assertEqual(
            "lb_denominator_surfaces_reconciled__select_raw_status_target_before_native_work",
            payload["exit_label"],
        )
        self.assertEqual(27133990, payload["author_oracle"]["raw_offload_rows_before_sort_reduce"])
        self.assertEqual(62, payload["author_oracle"]["division"]["rows_per_active_integer_if_exact"])

        bridge = self._surface("current_bridge_materialized_offload_rows")
        self.assertEqual(2188225, bridge["row_count"])
        self.assertEqual(5, bridge["division"]["rows_per_active_integer_if_exact"])
        self.assertFalse(bridge["raw_author_denominator_candidate"])

        default = self._surface("default_inline_raw_kind2_count")
        self.assertEqual(21006960, default["row_count"])
        self.assertEqual(48, default["division"]["rows_per_active_integer_if_exact"])
        self.assertTrue(default["raw_author_denominator_candidate"])

        full_cover = self._surface("full_cover_lb256_behavior_gate_surface")
        self.assertEqual(24508120, full_cover["row_count"])
        self.assertEqual(56, full_cover["division"]["rows_per_active_integer_if_exact"])
        self.assertTrue(full_cover["raw_author_denominator_candidate"])

        overcount = self._surface("noinline_or_heavy_before_raw_kind2_overcount")
        self.assertEqual(304981889, overcount["row_count"])
        self.assertFalse(overcount["division"]["integer_multiple"])

    def test_bridge_surface_is_not_the_sole_or_closest_target(self) -> None:
        summary = self.artifact["summary"]
        self.assertFalse(summary["bridge_surface_is_sole_target"])
        self.assertEqual(
            "full_cover_lb256_behavior_gate_surface",
            summary["closest_surface_by_absolute_row_delta"],
        )
        self.assertEqual(
            "full_cover_lb256_behavior_gate_surface",
            summary["closest_raw_denominator_candidate"],
        )
        self.assertTrue(summary["bridge_is_farther_from_author_than_closest_raw_candidate"])
        self.assertEqual(24945765, summary["bridge_absolute_row_delta"])
        self.assertEqual(2625870, summary["closest_raw_candidate_absolute_row_delta"])
        self.assertFalse(summary["any_surface_has_row_count_parity"])
        self.assertFalse(summary["any_surface_has_hash_parity"])

    def test_decision_selects_raw_semantics_without_promoting_full_cover(self) -> None:
        decision = self.artifact["decision"]
        self.assertEqual(
            "author_compatible_raw_status_semantics_not_post_bridge_row_count",
            decision["native_implementation_should_start_from"],
        )
        self.assertEqual(
            "generic_status_stream_target_selection_or_fail_closed_closeout",
            decision["next_goal"],
        )
        self.assertTrue(decision["bridge_runtime_optimization_rejected_as_next_main_path"])
        self.assertTrue(decision["hardcode_author_rows_per_active_rejected"])
        self.assertFalse(decision["full_cover_promoted_to_correctness_claim"])

    def test_claim_boundary_stays_closed(self) -> None:
        boundary = self.artifact["claim_boundary"]
        self.assertTrue(boundary["denominator_surface_reconciliation_claimed"])
        for key in (
            "explicit_lb_support_claimed",
            "row_count_parity_claimed",
            "hash_sample_parity_claimed",
            "full_cover_surface_promoted_to_author_semantics",
            "bridge_surface_promoted_to_sole_target",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "same_denominator_memory_claimed",
            "author_rt_core_algorithm_parity_claimed",
            "performance_ratio_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()
