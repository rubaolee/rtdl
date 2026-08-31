from __future__ import annotations

import dataclasses
from pathlib import Path
import hashlib
import json
import unittest

from rtdsl.v4_exact_predicate_witness import (
    CandidateProducerKind,
    ExactCompositionError,
    ExactPartnerAlgebra,
    ExactPoint2D,
    ExactPredicateWitnessSchema,
    ExactSegment2D,
    directed_point_location_sos,
    exact_segment_aabb_projection,
    exact_vertical_ray_aabb_projection,
    global_max_nearest_witness_f32,
    grouped_exact_segment_pair_counts,
    product_source_has_forbidden_identity_dispatch,
    rayjoin_sos_segment_pair_intersects,
    verify_exact_predicate_witness_schema,
)


ROOT = Path(__file__).resolve().parents[1]
H0 = "0" * 64
H1 = "1" * 64
H2 = "2" * 64
H3 = "3" * 64


def _schema(producer=CandidateProducerKind.CLOSED_AABB_RELATION):
    algebras = (
        (ExactPartnerAlgebra.GLOBAL_MAX_NEAREST_WITNESS_F32,)
        if producer is CandidateProducerKind.SPHERE_NEAREST
        else (
            ExactPartnerAlgebra.DIRECTED_POINT_LOCATION_SOS_I46,
            ExactPartnerAlgebra.SEGMENT_PAIR_GROUPED_COUNT_SOS_I46,
        )
    )
    return ExactPredicateWitnessSchema(
        callback_ir_sha256=H0,
        effect_digest=H1,
        physical_schema_sha256=H2,
        source_authority_nonce=H3,
        producer_kind=producer,
        partner_algebras=algebras,
        maximum_candidate_capacity=4096,
    )


class Goal5762ExactPredicateWitnessTest(unittest.TestCase):
    def test_schema_binds_closed_algebra_to_verified_producer_kind(self):
        schema = _schema()
        authority = verify_exact_predicate_witness_schema(
            callback_ir_sha256=H0, effect_digest=H1,
            physical_schema_sha256=H2, source_authority_nonce=H3,
            schema=schema)
        self.assertEqual(authority.schema, schema)
        with self.assertRaisesRegex(ExactCompositionError, "identity_binding"):
            verify_exact_predicate_witness_schema(
                callback_ir_sha256=H0, effect_digest=H1,
                physical_schema_sha256=H2, source_authority_nonce="4" * 64,
                schema=schema)
        with self.assertRaisesRegex(ExactCompositionError, "producer_algebra_binding"):
            verify_exact_predicate_witness_schema(
                callback_ir_sha256=H0, effect_digest=H1,
                physical_schema_sha256=H2, source_authority_nonce=H3,
                schema=dataclasses.replace(
                    schema,
                    partner_algebras=(
                        ExactPartnerAlgebra.GLOBAL_MAX_NEAREST_WITNESS_F32,
                    )))

    def test_global_witness_is_complete_and_ties_by_source_then_item(self):
        result = global_max_nearest_witness_f32(
            ((0, 9, 1, 4.0), (1, 7, 1, 9.0), (2, 3, 1, 9.0)),
            expected_query_ids=(0, 1, 2), source_ids=(100, 80, 70))
        self.assertEqual((result["source_id"], result["item_id"], result["value"]),
                         (70, 3, 3.0))
        with self.assertRaisesRegex(ExactCompositionError, "incomplete_query_coverage"):
            global_max_nearest_witness_f32(
                ((0, 9, 1, 4.0),), expected_query_ids=(0, 1))
        with self.assertRaisesRegex(ExactCompositionError, "duplicate_query"):
            global_max_nearest_witness_f32(
                ((0, 9, 1, 4.0), (0, 8, 1, 4.0)), expected_query_ids=(0,))

    def test_segment_sos_is_exact_on_crossing_endpoint_and_duplicate_cases(self):
        crossing_left = ExactSegment2D(1, 0, 0, 10, 10, group_id=5)
        crossing_right = ExactSegment2D(2, 0, 10, 10, 0, group_id=7)
        disjoint = ExactSegment2D(3, 20, 0, 30, 10, group_id=7)
        duplicate = ExactSegment2D(4, 10, 10, 0, 0, group_id=7)
        endpoint = ExactSegment2D(5, 10, 10, 20, 0, group_id=7)
        self.assertTrue(rayjoin_sos_segment_pair_intersects(
            crossing_left, crossing_right))
        self.assertFalse(rayjoin_sos_segment_pair_intersects(
            crossing_left, disjoint))
        self.assertFalse(rayjoin_sos_segment_pair_intersects(
            crossing_left, duplicate))
        # The asymmetric paper SoS assigns this endpoint touch away from the
        # left/right ordering used here; it is intentionally not an inclusive
        # geometric-segment predicate.
        self.assertFalse(rayjoin_sos_segment_pair_intersects(
            crossing_left, endpoint))
        self.assertTrue(rayjoin_sos_segment_pair_intersects(
            ExactSegment2D(6, 20, 0, 30, 10),
            ExactSegment2D(7, 10, 10, 20, 0)))

    def test_grouped_count_recomputes_exact_predicate_not_candidate_count(self):
        left = (
            ExactSegment2D(10, 0, 0, 10, 10, group_id=1),
            ExactSegment2D(11, 0, 20, 10, 30, group_id=1),
        )
        right = (
            ExactSegment2D(20, 0, 10, 10, 0, group_id=2),
            ExactSegment2D(21, 20, 0, 30, 10, group_id=2),
        )
        result = grouped_exact_segment_pair_counts(
            left, right,
            ((10, 20), (10, 21), (11, 20), (11, 21)), capacity=8)
        self.assertEqual(result["candidate_count"], 4)
        self.assertEqual(result["exact_pairs"], ((10, 20),))
        self.assertEqual(result["grouped_counts"], ((1, 2, 1),))
        with self.assertRaisesRegex(ExactCompositionError, "capacity_overflow"):
            grouped_exact_segment_pair_counts(
                left, right, ((10, 20), (10, 21)), capacity=1)

    def test_point_location_preserves_directed_endpoint_and_boundary_sos(self):
        segment = ExactSegment2D(
            50, 0, 10, 10, 10, left_face_id=41, right_face_id=42)
        interior = ExactPoint2D(1, 5, 5)
        boundary = ExactPoint2D(2, 5, 10)
        map0 = directed_point_location_sos(
            (interior, boundary), (segment,), ((1, 50), (2, 50)),
            query_map_id=0, capacity=4)
        map1 = directed_point_location_sos(
            (interior, boundary), (segment,), ((1, 50), (2, 50)),
            query_map_id=1, capacity=4)
        self.assertEqual(map0["rows"], ((1, 42, 50), (2, 42, 50)))
        self.assertEqual(map1["rows"], ((1, 42, 50), (2, 0, 0xFFFFFFFF)))

    def test_point_location_chooses_nearest_exact_rational_height(self):
        lower = ExactSegment2D(
            7, 0, 12, 10, 8, left_face_id=70, right_face_id=71)
        upper = ExactSegment2D(
            8, 0, 30, 10, 20, left_face_id=80, right_face_id=81)
        point = ExactPoint2D(9, 5, 0)
        result = directed_point_location_sos(
            (point,), (upper, lower), ((9, 8), (9, 7)),
            query_map_id=0, capacity=4)
        self.assertEqual(result["rows"], ((9, 71, 7),))

    def test_point_location_equal_slope_preserves_author_source_order_policy(self):
        first = ExactSegment2D(
            20, 0, 5, 10, 5, left_face_id=200, right_face_id=201)
        second = ExactSegment2D(
            10, 0, 5, 10, 5, left_face_id=100, right_face_id=101)
        point = ExactPoint2D(99, 5, 0)
        map0 = directed_point_location_sos(
            (point,), (first, second), ((99, 20), (99, 10)),
            query_map_id=0, capacity=4)
        map1 = directed_point_location_sos(
            (point,), (first, second), ((99, 20), (99, 10)),
            query_map_id=1, capacity=4)
        self.assertEqual(map0["rows"], ((99, 201, 20),))
        self.assertEqual(map1["rows"], ((99, 101, 10),))

    def test_exact_predicates_remain_integer_near_signed_i46_limit(self):
        maximum = (1 << 46) - 1
        left = ExactSegment2D(
            1, maximum - 10, maximum - 10, maximum, maximum, group_id=3)
        right = ExactSegment2D(
            2, maximum - 10, maximum, maximum, maximum - 10, group_id=4)
        self.assertTrue(rayjoin_sos_segment_pair_intersects(left, right))
        boxes = exact_segment_aabb_projection((left, right))
        for segment, box in zip((left, right), boxes):
            self.assertLessEqual(box[0], min(segment.x0, segment.x1))
            self.assertLessEqual(box[1], min(segment.y0, segment.y1))
            self.assertGreaterEqual(box[2], max(segment.x0, segment.x1))
            self.assertGreaterEqual(box[3], max(segment.y0, segment.y1))

    def test_vertical_ray_projection_is_conservative_and_identity_bound(self):
        point = ExactPoint2D(7, 5, 6)
        segment = ExactSegment2D(8, 0, 10, 10, 12)
        box = exact_vertical_ray_aabb_projection((point,), (segment,))[0]
        self.assertLessEqual(box[0], point.x)
        self.assertLessEqual(box[1], point.y)
        self.assertGreaterEqual(box[2], point.x)
        self.assertGreaterEqual(box[3], 12)
        self.assertEqual(box[4], point.point_id)

    def test_i46_and_identity_domains_fail_closed(self):
        with self.assertRaisesRegex(ExactCompositionError, "coordinate_domain"):
            ExactPoint2D(1, 1 << 46, 0)
        segment = ExactSegment2D(1, 0, 0, 10, 10)
        with self.assertRaisesRegex(ExactCompositionError, "duplicate_candidate"):
            grouped_exact_segment_pair_counts(
                (segment,), (ExactSegment2D(2, 0, 10, 10, 0),),
                ((1, 2), (1, 2)), capacity=4)

    def test_product_source_has_no_application_dispatch_or_opaque_callback(self):
        path = ROOT / "src/rtdsl/v4_exact_predicate_witness.py"
        source = path.read_text(encoding="utf-8")
        self.assertFalse(product_source_has_forbidden_identity_dispatch(source))
        for forbidden in (
            "user_callback", "callback_provider", "exec(",
            "importlib", "Paper-reproduction-apps",
        ):
            self.assertNotIn(forbidden, source)

    def test_successor_manifest_binds_m3_and_exact_new_product(self):
        path = ROOT / "history/internal_docs/goal5762_v4_core_successor_manifest_20260812.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        predecessor = ROOT / payload["predecessor_successor_manifest"]
        self.assertEqual(
            payload["predecessor_successor_manifest_sha256"],
            hashlib.sha256(predecessor.read_bytes()).hexdigest())
        self.assertEqual(payload["authorized_replacements"], [])
        for relative, expected in payload["added_product_modules"]:
            self.assertEqual(
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected)


if __name__ == "__main__":
    unittest.main()
