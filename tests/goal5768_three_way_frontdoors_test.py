from __future__ import annotations

from pathlib import Path
import unittest

from scripts.goal5768_three_way_frontdoors import (
    LANES, METHODS, V2, V3, V4, _particle_project, _rayjoin_finish, _v4,
)


ROOT = Path(__file__).resolve().parents[1]


class ThreeWayFrontdoorsTest(unittest.TestCase):
    def test_frozen_scope_is_nine_apps_thirteen_lanes_three_methods(self):
        self.assertEqual(len(LANES), 13)
        self.assertEqual(len({lane.app for lane in LANES}), 9)
        self.assertEqual(METHODS, (V2, V3, V4))
        self.assertEqual(len({lane.lane_id for lane in LANES}), 13)

    def test_every_lane_builds_one_real_application_input(self):
        for lane in LANES:
            module = _v4(lane)
            if lane.app == "triangle_counting":
                data = module.build_v4_input(lane.paper_algorithm)
            elif lane.app in {"librts", "rayjoin"}:
                data = module.build_v4_input(lane.paper_algorithm)
            else:
                data = module.build_v4_input()
            digest = getattr(data, "input_sha256", None) or data["input_sha256"]
            self.assertRegex(digest, r"^[0-9a-f]{64}$", lane.lane_id)

    def test_particle_predecessors_are_explicit_new_backports(self):
        lane = next(row for row in LANES if row.app == "particle_tracking")
        self.assertEqual(
            lane.predecessor_provenance,
            "new_fair_comparison_backports_frozen_before_any_v4_timing",
        )

    def test_xhd_v2_is_the_strongest_frozen_cell_mbr_true_optix_route(self):
        source = (ROOT / "scripts/goal5768_three_way_frontdoors.py").read_text(
            encoding="utf-8")
        self.assertIn("run_loaded_cell_mbr_true_optix_direct", source)
        self.assertNotIn(
            "raw = module.run_loaded_true_optix_direct(data", source)

    def test_particle_projection_matches_independent_oracle(self):
        lane = next(row for row in LANES if row.app == "particle_tracking")
        data = _v4(lane).build_v4_input()
        hit_t = (0.7, 0.5)
        rows = tuple({
            "ray_id": ray_id,
            "triangle_id": int(expected[2]),
            "t": hit_t[ray_id],
        } for ray_id, expected in enumerate(data["expected"]))
        self.assertEqual(_particle_project(data, rows), data["expected"])

    def test_particle_shared_boundary_owner_is_gpu_order_independent(self):
        lane = next(row for row in LANES if row.app == "particle_tracking")
        data = _v4(lane).build_v4_input()
        rows_face_4 = (
            {"ray_id": 0, "triangle_id": 3, "t": 0.7},
            {"ray_id": 1, "triangle_id": 4, "t": 0.5},
        )
        rows_face_5 = (
            {"ray_id": 0, "triangle_id": 3, "t": 0.7},
            {"ray_id": 1, "triangle_id": 5, "t": 0.5},
        )
        self.assertEqual(_particle_project(data, rows_face_4), data["expected"])
        self.assertEqual(_particle_project(data, rows_face_5), data["expected"])

    def test_particle_malformed_hit_evidence_fails_closed(self):
        lane = next(row for row in LANES if row.app == "particle_tracking")
        data = _v4(lane).build_v4_input()
        with self.assertRaisesRegex(ValueError, "distance is not exact evidence"):
            _particle_project(data, ({
                "ray_id": 0, "triangle_id": 3, "t": 0.125,
            },))

    def test_rayjoin_exact_continuations_match_application_expectations(self):
        for lane in (row for row in LANES if row.app == "rayjoin"):
            data = _v4(lane).build_v4_input(lane.paper_algorithm)
            actual, expected = _rayjoin_finish(
                lane, data, data["candidate_rows"])
            self.assertEqual(actual, expected, lane.lane_id)

    def test_product_and_app_frontdoors_do_not_import_goal_or_test_fixtures(self):
        product = tuple((ROOT / "src/rtdsl").glob("v4_*standard_library.py"))
        apps = tuple((ROOT / "Paper-reproduction-apps").glob("*/v4_whole_app.py"))
        for path in (*product, *apps):
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("from scripts.", source, str(path))
            self.assertNotIn("from tests.", source, str(path))


if __name__ == "__main__":
    unittest.main()
