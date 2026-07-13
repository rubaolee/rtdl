import unittest
import sys
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


ARTIFACT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "xhd_goal5354_radius_growth_semantics.json"


class Goal5354RadiusGrowthScheduleTest(unittest.TestCase):
    def test_adaptive_mode_matches_strict_author_thresholds(self):
        # reduced_factor = (100 - 90) / 100 = 0.10 < 1/8, so +8 diagonals.
        step = rt.radius_growth_step(
            radius=2.0,
            hd_upper_bound=100.0,
            cell_diagonal=0.5,
            last_input_count=100,
            next_input_count=90,
            mode="adaptive",
        )
        self.assertEqual(4.0, step.expanded_by)
        self.assertEqual(6.0, step.next_radius)
        self.assertAlmostEqual(0.10, step.reduced_factor)

        # Boundary is strict: 0.125 is not < 1/8, but is < 1/4, so +4.
        boundary = rt.radius_growth_step(
            radius=2.0,
            hd_upper_bound=100.0,
            cell_diagonal=0.5,
            last_input_count=1000,
            next_input_count=875,
            mode="adaptive",
        )
        self.assertEqual(2.0, boundary.expanded_by)
        self.assertEqual(4.0, boundary.next_radius)

    def test_double_and_add_modes(self):
        doubled = rt.radius_growth_step(
            radius=3.0,
            hd_upper_bound=100.0,
            cell_diagonal=0.5,
            last_input_count=10,
            next_input_count=8,
            mode="double",
        )
        self.assertEqual(3.0, doubled.expanded_by)
        self.assertEqual(6.0, doubled.next_radius)

        added = rt.radius_growth_step(
            radius=3.0,
            hd_upper_bound=100.0,
            cell_diagonal=0.5,
            last_input_count=10,
            next_input_count=8,
            mode="add",
        )
        self.assertEqual(0.5, added.expanded_by)
        self.assertEqual(3.5, added.next_radius)

    def test_clamps_and_stops_like_author_loop_guard(self):
        clamped = rt.radius_growth_step(
            radius=9.0,
            hd_upper_bound=10.0,
            cell_diagonal=2.0,
            last_input_count=100,
            next_input_count=99,
            mode="adaptive",
        )
        self.assertEqual(10.0, clamped.next_radius)
        self.assertTrue(clamped.clamp_applied)

        no_unresolved = rt.radius_growth_step(
            radius=9.0,
            hd_upper_bound=10.0,
            cell_diagonal=2.0,
            last_input_count=100,
            next_input_count=0,
            mode="adaptive",
        )
        self.assertEqual(9.0, no_unresolved.next_radius)
        self.assertFalse(no_unresolved.update_applied)
        self.assertIsNone(no_unresolved.reduced_factor)

        at_upper = rt.radius_growth_step(
            radius=10.0,
            hd_upper_bound=10.0,
            cell_diagonal=2.0,
            last_input_count=100,
            next_input_count=50,
            mode="double",
        )
        self.assertEqual(10.0, at_upper.next_radius)
        self.assertFalse(at_upper.update_applied)

    def test_trace_uses_previous_step_radius(self):
        trace = rt.radius_growth_trace(
            initial_radius=1.0,
            hd_upper_bound=10.0,
            cell_diagonal=1.0,
            input_counts=[100, 90, 45],
            mode="add",
        )
        self.assertEqual([2.0, 3.0], [step.next_radius for step in trace])

    def test_fail_closed_bad_inputs(self):
        with self.assertRaisesRegex(ValueError, "mode"):
            rt.radius_growth_step(
                radius=1.0,
                hd_upper_bound=2.0,
                cell_diagonal=1.0,
                last_input_count=10,
                next_input_count=5,
                mode="quadruple",  # type: ignore[arg-type]
            )
        with self.assertRaisesRegex(ValueError, "must not exceed"):
            rt.radius_growth_step(
                radius=1.0,
                hd_upper_bound=2.0,
                cell_diagonal=1.0,
                last_input_count=10,
                next_input_count=11,
                mode="add",
            )

    def test_non_xhd_retry_radius_consumer(self):
        # Generic use case: a retrying approximate neighbor search expands its
        # candidate radius based on unresolved request counts.
        trace = rt.radius_growth_trace(
            initial_radius=0.25,
            hd_upper_bound=5.0,
            cell_diagonal=0.25,
            input_counts=[20, 18, 9, 3],
            mode="adaptive",
        )
        radii = [round(step.next_radius, 6) for step in trace]
        self.assertEqual([2.25, 2.5, 2.75], radii)
        for step in trace:
            self.assertEqual("none", step.app_semantics)
            self.assertEqual(rt.RADIUS_GROWTH_SCHEDULE_CONTRACT_VERSION, step.contract)

    def test_goal5354_artifact_keeps_route_mapping_unclaimed(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            "radius_growth_schedule_helper_ready__route_mapping_not_yet_enabled",
            payload["status"],
        )
        adaptive = payload["examples"]["adaptive"]
        self.assertEqual(
            2.0,
            adaptive["strict_boundary_one_eighth_adds_4_diagonals"]["expanded_by"],
        )
        self.assertEqual(
            0.5,
            adaptive["half_reduction_adds_1_diagonal"]["expanded_by"],
        )
        mapping = payload["current_xhd_mapping_status"]
        self.assertTrue(mapping["helper_semantics_available"])
        self.assertFalse(mapping["route_uses_helper"])
        self.assertTrue(mapping["run_xhd_rtdl_hd_exec_explicit_tune_radius_still_fail_closed"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)


if __name__ == "__main__":
    unittest.main()
