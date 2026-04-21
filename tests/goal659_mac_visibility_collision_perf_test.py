from __future__ import annotations

import unittest

import rtdsl as rt
from scripts import goal659_mac_visibility_collision_perf as harness


class Goal659MacVisibilityCollisionPerfTest(unittest.TestCase):
    def test_scale_parser_requires_kind_name_rays_and_obstacles(self) -> None:
        self.assertEqual(
            harness._parse_scale("dense_blocked:tiny,16,4"),
            ("dense_blocked:tiny", 16, 4),
        )
        with self.assertRaises(Exception):
            harness._parse_scale("tiny,16,4")

    def test_reported_backends_exclude_cpu_engine(self) -> None:
        payload = {
            "host": {"platform": "test"},
            "cases": [
                {
                    "case": "dense_blocked:tiny",
                    "ray_count": 1,
                    "obstacle_triangle_count": 2,
                    "apple_rt_prepare_seconds": 0.05,
                    "measurements": [
                        {
                            "backend": "apple_rt",
                            "status": "ok",
                            "cold_seconds": 0.1,
                            "inner_iterations": 1,
                            "stats": {"median_seconds": 0.2},
                            "per_query_stats": {"median_seconds": 0.2},
                            "summary": {"blocked_count": 1},
                            "matches_oracle": True,
                        },
                        {
                            "backend": "apple_rt_prepared_query",
                            "status": "ok",
                            "cold_seconds": 0.11,
                            "inner_iterations": 1,
                            "stats": {"median_seconds": 0.12},
                            "per_query_stats": {"median_seconds": 0.12},
                            "summary": {"blocked_count": 1},
                            "matches_oracle": True,
                        },
                        {
                            "backend": "embree",
                            "status": "ok",
                            "cold_seconds": 0.01,
                            "inner_iterations": 1,
                            "stats": {"median_seconds": 0.02},
                            "per_query_stats": {"median_seconds": 0.02},
                            "summary": {"blocked_count": 1},
                            "matches_oracle": True,
                        },
                        {
                            "backend": "shapely_strtree",
                            "status": "ok",
                            "cold_seconds": 0.03,
                            "inner_iterations": 1,
                            "stats": {"median_seconds": 0.04},
                            "per_query_stats": {"median_seconds": 0.04},
                            "summary": {"blocked_count": 1},
                            "matches_oracle": True,
                        },
                    ],
                }
            ],
        }
        markdown = harness.render_markdown(payload)
        self.assertIn("Reported engines: Apple RT one-shot, Apple RT prepared-query, Embree, Shapely/GEOS STRtree", markdown)
        self.assertIn("CPU/oracle is used only for correctness parity", markdown)
        self.assertNotIn("`cpu`", markdown)

    def test_backend_agreement_mode_reports_reference_check(self) -> None:
        payload = {
            "host": {"platform": "test"},
            "methodology": {
                "correctness_mode": "backend_agreement",
                "note": "Full CPU/oracle is skipped for scale; successful backends are compared by backend-output agreement.",
            },
            "cases": [
                {
                    "case": "dense_blocked:large",
                    "ray_count": 1,
                    "obstacle_triangle_count": 2,
                    "apple_rt_prepare_seconds": 0.05,
                    "measurements": [
                        {
                            "backend": "apple_rt_prepared_query",
                            "status": "ok",
                            "stats": {"median_seconds": 0.12},
                            "per_query_stats": {"median_seconds": 0.12},
                            "inner_iterations": 1,
                            "summary": {"blocked_count": 1},
                            "matches_oracle": None,
                            "reference_backend": "apple_rt_prepared_query",
                            "matches_reference_backend": True,
                        },
                        {
                            "backend": "embree",
                            "status": "ok",
                            "stats": {"median_seconds": 0.02},
                            "per_query_stats": {"median_seconds": 0.02},
                            "inner_iterations": 1,
                            "summary": {"blocked_count": 1},
                            "matches_oracle": None,
                            "reference_backend": "apple_rt_prepared_query",
                            "matches_reference_backend": True,
                        },
                    ],
                }
            ],
        }
        markdown = harness.render_markdown(payload)
        self.assertIn("Correctness mode: `backend_agreement`", markdown)
        self.assertIn("apple_rt_prepared_query=True", markdown)

    def test_case_generation_uses_requested_scale(self) -> None:
        case = harness.make_case("dense_blocked", 8, 3)
        self.assertEqual(len(case["rays"]), 8)
        self.assertEqual(len(case["triangles"]), 6)

    def test_mixed_visibility_case_has_blocked_and_clear_rays(self) -> None:
        case = harness.make_case("mixed_visibility", 16, 4)
        rows = tuple(rt.ray_triangle_any_hit_cpu(case["rays"], case["triangles"]))
        blocked_count = sum(1 for row in rows if int(row["any_hit"]) != 0)
        self.assertGreater(blocked_count, 0)
        self.assertLess(blocked_count, len(rows))

    def test_prepared_apple_rt_2d_anyhit_matches_direct_when_available(self) -> None:
        try:
            rt.apple_rt_context_probe()
        except Exception as exc:
            self.skipTest(f"Apple RT unavailable: {exc}")
        case = harness.make_case("dense_blocked", 16, 4)
        try:
            direct = tuple(rt.run_apple_rt(harness.visibility_any_hit_2d_kernel, native_only=True, **case))
            with rt.prepare_apple_rt_ray_triangle_any_hit_2d(case["triangles"]) as prepared:
                prepared_rows = tuple(prepared.run(case["rays"]))
        except NotImplementedError as exc:
            self.skipTest(str(exc))
        self.assertEqual(harness._canonical_any_hit(prepared_rows), harness._canonical_any_hit(direct))

    def test_prepared_apple_rt_profile_reports_native_timing_when_available(self) -> None:
        try:
            rt.apple_rt_context_probe()
        except Exception as exc:
            self.skipTest(f"Apple RT unavailable: {exc}")
        case = harness.make_case("dense_blocked", 16, 4)
        try:
            with rt.prepare_apple_rt_ray_triangle_any_hit_2d(case["triangles"]) as prepared:
                rows_view, profile = prepared.run_profile(case["rays"])
                rows = tuple(rows_view)
                rows_view.close()
        except NotImplementedError as exc:
            self.skipTest(str(exc))
        self.assertEqual(len(rows), 16)
        self.assertEqual(profile["ray_count"], 16)
        self.assertGreaterEqual(profile["chunk_count"], 1)
        self.assertGreaterEqual(profile["total_seconds"], profile["dispatch_wait_seconds"])
        self.assertGreaterEqual(profile["hit_count"], 0)

    def test_prepared_apple_rt_count_profile_matches_rows_when_available(self) -> None:
        try:
            rt.apple_rt_context_probe()
        except Exception as exc:
            self.skipTest(f"Apple RT unavailable: {exc}")
        case = harness.make_case("dense_blocked", 16, 4)
        try:
            with rt.prepare_apple_rt_ray_triangle_any_hit_2d(case["triangles"]) as prepared:
                rows_view = prepared.run(case["rays"])
                rows = tuple(rows_view)
                rows_view.close()
                hit_count, profile = prepared.count_profile(case["rays"])
        except NotImplementedError as exc:
            self.skipTest(str(exc))
        self.assertEqual(hit_count, sum(1 for row in rows if int(row["any_hit"]) != 0))
        self.assertEqual(profile["hit_count"], hit_count)
        self.assertEqual(profile["ray_count"], 16)

    def test_prepared_apple_rt_packed_ray_buffer_matches_unpacked_when_available(self) -> None:
        try:
            rt.apple_rt_context_probe()
        except Exception as exc:
            self.skipTest(f"Apple RT unavailable: {exc}")
        case = harness.make_case("dense_blocked", 16, 4)
        try:
            packed_rays = rt.prepare_apple_rt_rays_2d(case["rays"])
            with rt.prepare_apple_rt_ray_triangle_any_hit_2d(case["triangles"]) as prepared:
                unpacked_view = prepared.run(case["rays"])
                unpacked_rows = tuple(unpacked_view)
                unpacked_view.close()
                packed_view = prepared.run_packed(packed_rays)
                packed_rows = tuple(packed_view)
                packed_view.close()
                packed_count, packed_profile = prepared.count_profile_packed(packed_rays)
        except NotImplementedError as exc:
            self.skipTest(str(exc))
        self.assertEqual(harness._canonical_any_hit(packed_rows), harness._canonical_any_hit(unpacked_rows))
        self.assertEqual(packed_count, sum(1 for row in unpacked_rows if int(row["any_hit"]) != 0))
        self.assertEqual(packed_profile["ray_count"], 16)


if __name__ == "__main__":
    unittest.main()
