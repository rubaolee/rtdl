from __future__ import annotations

import ast
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import goal5774_prepared_three_way_frontdoors as frontdoors


class Goal5774V2V4PreparedFrontdoorsTest(unittest.TestCase):
    def test_scope_is_exactly_v2_direct_and_v4(self):
        self.assertEqual(frontdoors.METHODS, (frontdoors.V2, frontdoors.V4))
        self.assertEqual(len(frontdoors.LANES), 13)
        self.assertNotIn(frontdoors.V3, frontdoors.METHODS)

    def test_every_lane_has_two_distinct_dynamic_requests_and_activation(self):
        for lane in frontdoors.LANES:
            module = frontdoors._v4(lane)
            data = (
                module.build_v4_input(lane.paper_algorithm)
                if lane.app in {"triangle_counting", "librts", "rayjoin"}
                else module.build_v4_input()
            )
            first = frontdoors._dynamic_request(lane, data, 0)
            second = frontdoors._dynamic_request(lane, data, 1)
            activation = frontdoors._dynamic_request(lane, data, 2)
            digests = {
                frontdoors._dynamic_input_digest(lane, request)
                for request in (first, second, activation)
            }
            self.assertEqual(len(digests), 3, lane.lane_id)

    def test_prepared_execute_does_not_call_cold_goal5768_frontdoor(self):
        path = ROOT / "scripts/goal5774_prepared_three_way_frontdoors.py"
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertNotIn("run_complete", called)
        self.assertNotIn("_v4_run", called)
        self.assertNotIn("run_v4_complete", called)

    def test_v3_is_fail_closed_for_goal5774(self):
        lane = frontdoors.LANES[0]
        with self.assertRaises(ValueError):
            frontdoors.prepare_three_way(lane.lane_id, frontdoors.V3, runtime={})

    def test_new_core_wrappers_are_application_neutral(self):
        for relative in (
            "src/rtdsl/action_ray_triangle_scalar_summary.py",
            "src/rtdsl/generic_primitives.py",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8").lower()
            for forbidden in (
                'if app ==', 'if application ==', 'triangle_counting',
                'particle_tracking', 'paper_algorithm ==',
            ):
                self.assertNotIn(forbidden, text, relative)


if __name__ == "__main__":
    unittest.main()
