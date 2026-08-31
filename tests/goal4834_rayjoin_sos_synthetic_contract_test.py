import math
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def _norm_slope(slope: float) -> float:
    return max(0.0, min(1.0, (math.atan(slope) + math.pi / 2.0) / math.pi))


def _tie_breaker(slope: float, query_map_id: int) -> float:
    normalized = _norm_slope(slope)
    return normalized if query_map_id == 0 else 1.0 - normalized


def _reported_t(edge_t: float, slope: float, query_map_id: int) -> float:
    factor = edge_t if edge_t > 1.0 else 1.0
    return edge_t + factor * (1.0 - _tie_breaker(slope, query_map_id)) * 1.0e-14


def _winner(candidates: list[tuple[int, float, float]], query_map_id: int) -> int:
    # candidates are (segment_id, equal_primary_t, slope). OptiX accepts the
    # smallest reported t, so the preferred SoS candidate must report slightly
    # smaller t even when all primary t values are equal.
    return min(
        candidates,
        key=lambda item: (_reported_t(item[1], item[2], query_map_id), item[0]),
    )[0]


def _source_order_winner(candidates: list[tuple[int, float, float]], query_map_id: int) -> int:
    best = candidates[0]
    for current in candidates[1:]:
        _, current_t, current_slope = current
        _, best_t, best_slope = best
        if current_t < best_t:
            best = current
        elif current_t == best_t:
            if current_slope > best_slope:
                flag = True
            else:
                flag = False
            # This mirrors the author kernel exactly:
            # map 0 rejects equal/lower slope, map 1 rejects strictly larger slope.
            if (query_map_id == 0 and not flag) or (query_map_id != 0 and flag):
                continue
            best = current
    return best[0]


def _endpoint_allowed(point_x: int, x0: int, x1: int, query_map_id: int) -> bool:
    x_min = min(x0, x1)
    x_max = max(x0, x1)
    excluded_x = x_min if query_map_id == 0 else x_max
    return x_min <= point_x <= x_max and point_x != excluded_x


def _author_boundary_accepts(a: int, b: int, point_sy: int, numerator: int, query_map_id: int) -> bool:
    # Mirrors the scaled directed point-location boundary rule. The equality
    # case must be detected in integer/rational space; converting to double
    # first can miss exact boundary hits and accept the wrong side.
    diff_numerator = point_sy * b - numerator
    if diff_numerator == 0:
        sos_diff = -a if query_map_id == 0 else a
        if sos_diff == 0:
            sos_diff = -b if query_map_id == 0 else b
        return sos_diff <= 0
    return diff_numerator <= 0


class Goal4834RayjoinSosSyntheticContractTest(unittest.TestCase):
    def test_reported_t_prefers_larger_slope_for_query_map_0(self) -> None:
        low = _reported_t(10.0, -2.0, 0)
        high = _reported_t(10.0, 3.0, 0)

        self.assertLess(high, low)

    def test_reported_t_prefers_smaller_slope_for_query_map_1(self) -> None:
        low = _reported_t(10.0, -2.0, 1)
        high = _reported_t(10.0, 3.0, 1)

        self.assertLess(low, high)

    def test_equal_height_winner_is_independent_of_candidate_order(self) -> None:
        candidates = [(10, 5.0, -1.0), (20, 5.0, 4.0)]

        self.assertEqual(_winner(candidates, 0), 20)
        self.assertEqual(_winner(list(reversed(candidates)), 0), 20)
        self.assertEqual(_winner(candidates, 1), 10)
        self.assertEqual(_winner(list(reversed(candidates)), 1), 10)

    def test_equal_slope_tie_matches_author_source_order_contract(self) -> None:
        candidates = [(20, 5.0, 3.0), (10, 5.0, 3.0)]

        self.assertEqual(_source_order_winner(candidates, 0), 20)
        self.assertEqual(_source_order_winner(candidates, 1), 10)

    def test_same_height_same_slope_tie_keeps_author_source_order_contract(self) -> None:
        # AuthorPatch encodes only the slope SoS perturbation. When candidates
        # have the same height and the same slope, the source kernel has no
        # geometry/id fallback: map 0 keeps the first equal-slope candidate,
        # while map 1 accepts the later equal-slope candidate. Exact
        # reproduction must therefore align primitive grouping/order with the
        # author route, not invent a new direction/id fallback.
        first = [(15_219_356, 5.0, 0.0), (15_220_835, 5.0, 0.0)]
        second = list(reversed(first))

        self.assertEqual(_source_order_winner(first, 0), 15_219_356)
        self.assertEqual(_source_order_winner(second, 0), 15_220_835)
        self.assertEqual(_source_order_winner(first, 1), 15_220_835)
        self.assertEqual(_source_order_winner(second, 1), 15_219_356)

    def test_endpoint_exclusion_is_map_directed(self) -> None:
        self.assertFalse(_endpoint_allowed(0, 0, 10, 0))
        self.assertTrue(_endpoint_allowed(10, 0, 10, 0))

        self.assertTrue(_endpoint_allowed(0, 0, 10, 1))
        self.assertFalse(_endpoint_allowed(10, 0, 10, 1))

    def test_exact_boundary_uses_integer_sos_before_double_conversion(self) -> None:
        point_sy = 6_221_994_945_795
        b = 5_205_604_535
        numerator = point_sy * b

        self.assertFalse(
            _author_boundary_accepts(
                a=-18_358_140_695,
                b=b,
                point_sy=point_sy,
                numerator=numerator,
                query_map_id=0,
            )
        )
        self.assertTrue(
            _author_boundary_accepts(
                a=18_358_140_695,
                b=b,
                point_sy=point_sy,
                numerator=numerator,
                query_map_id=0,
            )
        )

    def test_rtdl_optix_internal_comparator_matches_reported_t_direction(self) -> None:
        core = (ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp").read_text(
            encoding="utf-8"
        )

        self.assertIn("directed_segment_sos_segment_is_better", core)
        self.assertNotIn("directed_segment_sos_direction_is_preferred", core)
        self.assertNotIn("current_segment.id > best_segment.id", core)
        self.assertNotIn("better = segment.id < params.segments[best_segment_index].id", core)
        self.assertNotIn("current_line.b > best_line.b", core)
        self.assertNotIn("current_reverse_x", core)
        self.assertNotIn("return current_reverse_x", core)
        self.assertNotIn("current_segment.id < best_segment.id", core)
        self.assertIn(
            "if (current_slope == best_slope) {\n"
            "        (void)current_segment;\n"
            "        (void)best_segment;\n"
            "        (void)query_map_id;\n"
            "        return false;\n"
            "    }",
            core,
        )
        self.assertIn("return query_map_id == 0u ? normalized_slope : (1.0 - normalized_slope)", core)
        self.assertIn("factor * (1.0 - tie_breaker) * 1.0e-14", core)
        self.assertNotIn("const __int128 diff_numerator", core)
        self.assertIn(
            "const double xsect_y = static_cast<double>(numerator) / static_cast<double>(line.b)",
            core,
        )
        self.assertIn("double diff_y = static_cast<double>(point.sy) - xsect_y", core)
        self.assertIn(
            "diff_y = query_map_id == 0u ? -static_cast<double>(line.a) : static_cast<double>(line.a)",
            core,
        )
        self.assertIn("double scale_rry;", core)
        self.assertIn("params.scale_rry", core)
        self.assertIn(") * scale_rry", core)

    def test_custom_accel_allow_compaction_performs_actual_compaction(self) -> None:
        core = (ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp").read_text(
            encoding="utf-8"
        )

        self.assertIn("OPTIX_PROPERTY_TYPE_COMPACTED_SIZE", core)
        self.assertIn("emit_desc.result = compacted_size_buf.ptr;", core)
        self.assertIn("optixAccelCompact(", core)
        self.assertIn("result.output_buf = compacted_buf;", core)
        self.assertIn("result.handle = compacted_handle;", core)

    def test_equal_slope_duplicate_edge_heuristics_are_not_a_contract(self) -> None:
        # These Block x Water Section 5.7 witnesses exposed why the remaining
        # duplicate-edge mismatch cannot be solved by inventing a second-order
        # geometry/id rule. Larger-b and reverse-x rules each fixed one local
        # witness while regressing another earlier in the output stream. The
        # product contract must follow the author source: slope SoS plus the
        # same primitive grouping/AABB/traversal order, not a new fallback.
        witnesses = [
            {
                "point_index": 1069665,
                "candidate_b": [456390313, 456550523],
                "candidate_reverse_x": [True, False],
                "expected_candidate": 1,
                "reason": "larger_b",
            },
            {
                "point_index": 5693875,
                "candidate_b": [2348568130, 2348568130],
                "candidate_reverse_x": [True, False],
                "expected_candidate": 0,
                "reason": "same_b_reverse_x",
            },
            {
                "point_index": 7906217,
                "candidate_b": [218785282, 218785282],
                "candidate_reverse_x": [False, True],
                "expected_candidate": 1,
                "reason": "same_b_reverse_x",
            },
            {
                "point_index": 7386601,
                "candidate_b": [1, 1],
                "candidate_reverse_x": [False, True],
                "expected_candidate": 0,
                "reason": "same_b_forward_x",
            },
            {
                "point_index": 9926545,
                "candidate_b": [673939513, 673921028],
                "candidate_reverse_x": [False, True],
                "expected_candidate": 0,
                "reason": "larger_b",
            },
        ]

        def larger_b_then_reverse_x(witness: dict[str, object]) -> int:
            spans = witness["candidate_b"]
            reverse_x = witness["candidate_reverse_x"]
            assert isinstance(spans, list)
            assert isinstance(reverse_x, list)
            if spans[0] != spans[1]:
                return 0 if spans[0] > spans[1] else 1
            if reverse_x[0] != reverse_x[1]:
                return 0 if reverse_x[0] else 1
            return 0

        mismatched_points = []
        for witness in witnesses:
            selected = larger_b_then_reverse_x(witness)
            if selected != witness["expected_candidate"]:
                mismatched_points.append(witness["point_index"])

        self.assertIn(7386601, mismatched_points)

    def test_cdb_point_location_aabb_uses_author_style_rounding_and_height(self) -> None:
        workloads = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )

        self.assertIn("next_float_from_double", workloads)
        self.assertIn("std::nextafter(out, target)", workloads)
        self.assertIn("aabb.minZ = -0.005f;", workloads)
        self.assertIn("aabb.maxZ = 0.005f;", workloads)
        self.assertIn("if (!stable_count) {", workloads)
        self.assertIn("aabbs[range_index] = rounded(bounds);", workloads)
        self.assertIn("aabbs.push_back(rounded(range.bounds));", workloads)
        self.assertIn("aabbs.push_back(rounded(bounds));", workloads)
        self.assertIn(
            "accel = build_custom_accel_with_flags(\n"
            "                get_optix_context(),\n"
            "                aabbs,\n"
            "                OPTIX_BUILD_FLAG_ALLOW_COMPACTION);",
            workloads,
        )

    def test_scaled_query_points_are_available_for_exact_cdb_midpoints(self) -> None:
        prelude = (ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h").read_text(
            encoding="utf-8"
        )
        workloads = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )
        runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        overlay = (ROOT / "src" / "rtdsl" / "rayjoin_overlay.py").read_text(encoding="utf-8")

        self.assertIn("struct RtdlRayjoinCdbScaledPoint", prelude)
        self.assertIn("rtdl_optix_run_prepared_rayjoin_cdb_point_location_scaled_points_2d", prelude)
        self.assertIn("make_rayjoin_cdb_gpu_scaled_points", workloads)
        self.assertIn("PackedRayjoinCdbScaledPoints", runtime)
        self.assertIn("OPTIX_RAYJOIN_CDB_POINT_LOCATION_RUN_SCALED_POINTS_SYMBOL", runtime)
        self.assertIn("_packed_scaled_points_from_midpoints", overlay)
        self.assertIn("scaled_midpoints=scaled_midpoints", overlay)

    def test_midpoint_faces_are_per_directed_map(self) -> None:
        from rtdsl.rayjoin_overlay import RayjoinOverlayIntersection
        from rtdsl.rayjoin_overlay import _assign_midpoint_faces
        from rtdsl.rayjoin_overlay import _midpoint_face_for_map

        owner = RayjoinOverlayIntersection(eid0=1, eid1=2, x=0.0, y=0.0)

        _assign_midpoint_faces([owner], [1113], map_index=0)
        _assign_midpoint_faces([owner], [17], map_index=1)

        self.assertEqual(_midpoint_face_for_map(owner, 0), 1113)
        self.assertEqual(_midpoint_face_for_map(owner, 1), 17)

    def test_output_chain_xsect_points_use_author_display_coordinates_for_identity(self) -> None:
        from rtdsl.rayjoin_overlay import RayjoinOverlayIntersection
        from rtdsl.rayjoin_overlay import _dedupe_consecutive_point_pairs
        from rtdsl.rayjoin_overlay import _xsect_output_point

        first = RayjoinOverlayIntersection(
            eid0=4946696,
            eid1=16154422,
            x=-82.64204540975516,
            y=28.85265862488361,
            display_x=-82.64204540975521,
            display_y=28.85265862488388,
        )
        second = RayjoinOverlayIntersection(
            eid0=4946696,
            eid1=16156961,
            x=-82.64204540975510,
            y=28.85265862488362,
            display_x=-82.64204540975521,
            display_y=28.85265862488388,
        )

        points = [_xsect_output_point(first), _xsect_output_point(second)]
        deduped, display = _dedupe_consecutive_point_pairs(points, points)

        self.assertEqual(deduped, [points[0]])
        self.assertEqual(display, [points[0]])

    def test_output_chain_keeps_distinct_author_double_points_even_if_text_rounds_equal(self) -> None:
        from rtdsl.rayjoin_overlay import _dedupe_consecutive_point_pairs

        points = [
            (-86.78435510, 32.32442010),
            (-86.78435540, 32.32442040),
        ]

        deduped, display = _dedupe_consecutive_point_pairs(points, points)

        self.assertEqual(deduped, points)
        self.assertEqual(display, points)

    def test_negative_half_unit_midpoint_matches_author_internal_cast(self) -> None:
        from fractions import Fraction

        from rtdsl.rayjoin_overlay import RayjoinOverlayIntersection
        from rtdsl.rayjoin_overlay import _midpoints_for_sorted_xsects

        scale_bounds = (-179.148909, 179.778465, -14.548692, 71.390482)
        scaled_midpoints: list[tuple[int, int] | None] = []
        intersections = [
            RayjoinOverlayIntersection(
                eid0=43212,
                eid1=8522815,
                x=-86.6849394999989,
                y=34.080121799998686,
                scaled_x=-33924059549368.0,
                scaled_y=9057003035586.0,
                scaled_x_rational=Fraction(
                    -849631005185907902183936852,
                    25045086480569,
                ),
                scaled_y_rational=Fraction(
                    2041500818529247127170970804,
                    225405778325121,
                ),
            ),
            RayjoinOverlayIntersection(
                eid0=43212,
                eid1=8522816,
                x=-86.68493949999633,
                y=34.08012180000119,
                scaled_x=-33924059549367.0,
                scaled_y=9057003035590.0,
                scaled_x_rational=Fraction(
                    -42704545359037305450425626652,
                    1258827685315555,
                ),
                scaled_y_rational=Fraction(
                    11401206167187807083092783964,
                    1258827685315555,
                ),
            ),
        ]

        _midpoints_for_sorted_xsects(
            intersections,
            0,
            scale_bounds=scale_bounds,
            scaled_midpoints=scaled_midpoints,
        )

        self.assertEqual(scaled_midpoints, [(-33924059549367, 9057003035588)])


if __name__ == "__main__":
    unittest.main()
