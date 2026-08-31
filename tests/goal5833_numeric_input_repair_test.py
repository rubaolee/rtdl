"""Focused regression tests for the Goal5833 A3 numeric/input repairs."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import struct
import unittest


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ORACLE = _load(
    "goal5833_numeric_repair_oracle",
    ROOT / "examples" / "first_contact_sphere" / "first_contact_oracle.py",
)
VALIDATION = _load(
    "goal5833_numeric_repair_validation",
    ROOT / "scripts" / "goal5833_home_builtin_sphere_validation.py",
)


class Goal5833NumericInputRepairTest(unittest.TestCase):
    def test_raw_t_evidence_preserves_nan_f32_bits_in_strict_json(self):
        payload_bits = 0xFFC12345
        payload_nan = struct.unpack("<f", struct.pack("<I", payload_bits))[0]
        self.assertTrue(math.isnan(payload_nan))
        values, bits = VALIDATION._raw_t_evidence((payload_nan, 0.5))
        self.assertEqual(values, [None, 0.5])
        self.assertEqual(bits, [payload_bits, ORACLE.f32_bits(0.5)])
        json.dumps({"values": values, "bits": bits}, allow_nan=False)

    def test_oracle_projects_all_inputs_to_binary32_before_solving(self):
        raw = ORACLE.first_contact(
            (0.0, 0.0, 0.0), (1.0, 0.0, 0.0),
            ((0.20030000007, 0.0, 0.0),), (0.00110000018,), (7,),
        )
        projected = ORACLE.first_contact(
            tuple(map(ORACLE.f32, (0.0, 0.0, 0.0))),
            tuple(map(ORACLE.f32, (1.0, 0.0, 0.0))),
            (tuple(map(ORACLE.f32, (0.20030000007, 0.0, 0.0))),),
            (ORACLE.f32(0.00110000018),), (7,),
        )
        self.assertEqual(raw, projected)
        self.assertEqual(raw[1], 1045166869)

    def test_exact_discriminant_prevents_cancellation_false_tangent(self):
        self.assertEqual(
            ORACLE.first_contact(
                (0.0, 0.0, 0.0), (200000.0, 0.0, 0.0),
                ((100000.0, 1.0000001192092896, 0.0),), (1.0,), (4,),
            ),
            (0, ORACLE.f32_bits(1.0), ORACLE.U32_MAX),
        )

    def test_cancellation_case_is_rejected_by_public_conditioning_gate(self):
        from rtdsl.v4_sphere_physical_schema import (
            SpherePhysicalSchemaError, verify_motion_segments,
            verify_reference_sphere_contents,
        )

        centers, radii, _ = verify_reference_sphere_contents(
            ((100000.0, 1.0000001192092896, 0.0),), (1.0,), (4,))
        with self.assertRaisesRegex(
                SpherePhysicalSchemaError, "near_degenerate_contact"):
            verify_motion_segments(
                ((0.0, 0.0, 0.0),), ((200000.0, 0.0, 0.0),),
                centers=centers, radii=radii,
            )

    def test_conditioning_boundary_is_dimensionless_and_frozen(self):
        from rtdsl.v4_sphere_physical_schema import (
            BINARY32_UNIT_ROUNDOFF,
            SPHERE_DISCRIMINANT_GUARD_UNIT_ROUNDOFFS,
            SPHERE_DISCRIMINANT_SEPARATION_MIN,
        )

        self.assertEqual(
            SPHERE_DISCRIMINANT_SEPARATION_MIN,
            BINARY32_UNIT_ROUNDOFF
            * SPHERE_DISCRIMINANT_GUARD_UNIT_ROUNDOFFS,
        )
        self.assertEqual(SPHERE_DISCRIMINANT_SEPARATION_MIN.denominator, 1 << 12)

    def test_conditioning_rule_rejects_below_and_accepts_above_boundary(self):
        from rtdsl.v4_sphere_physical_schema import (
            SpherePhysicalSchemaError, verify_motion_segments,
            verify_reference_sphere_contents,
        )

        # For center (1,y), radius 1, and the x-axis, the dimensionless
        # separation is |1-y^2|/(1+y^2).  y=1+2^-12 lies just below the
        # frozen 2^-12 boundary; y=1+2^-11 lies above it.
        below_centers, below_radii, _ = verify_reference_sphere_contents(
            ((1.0, 1.0 + 2.0 ** -12, 0.0),), (1.0,), (1,))
        with self.assertRaisesRegex(
                SpherePhysicalSchemaError, "near_degenerate_contact"):
            verify_motion_segments(
                ((0.0, 0.0, 0.0),), ((2.0, 0.0, 0.0),),
                centers=below_centers, radii=below_radii)
        above_centers, above_radii, _ = verify_reference_sphere_contents(
            ((1.0, 1.0 + 2.0 ** -11, 0.0),), (1.0,), (1,))
        self.assertEqual(len(verify_motion_segments(
            ((0.0, 0.0, 0.0),), ((2.0, 0.0, 0.0),),
            centers=above_centers, radii=above_radii)), 1)

    def test_oracle_retains_exact_tangent_but_public_path_rejects_it(self):
        self.assertEqual(
            ORACLE.first_contact(
                (0.0, 8.0, 0.0), (4.0, 8.0, 0.0),
                ((2.0, 9.0, 0.0),), (1.0,), (11,),
            ),
            (1, struct.unpack("<I", struct.pack("<f", 0.5))[0], 11),
        )
        from rtdsl.v4_sphere_physical_schema import (
            verify_motion_segments, verify_reference_sphere_contents,
        )
        centers, radii, _ = verify_reference_sphere_contents(
            ((2.0, 9.0, 0.0),), (1.0,), (11,))
        from rtdsl.v4_sphere_physical_schema import SpherePhysicalSchemaError
        with self.assertRaisesRegex(
                SpherePhysicalSchemaError,
                "exact_tangent_unsupported_by_optix9_front_face_contract"):
            verify_motion_segments(
                ((0.0, 8.0, 0.0),), ((4.0, 8.0, 0.0),),
                centers=centers, radii=radii,
            )

    def test_uncertified_exact_tangent_is_rejected(self):
        from rtdsl.v4_sphere_physical_schema import (
            SpherePhysicalSchemaError, verify_motion_segments,
            verify_reference_sphere_contents,
        )

        # Exact tangent to a diagonal line: a=100, half_b=-50, c=25,
        # discriminant=0.  Geometry orientation cannot change the frozen
        # prelaunch rejection of a grazing equality.
        centers, radii, _ = verify_reference_sphere_contents(
            ((4.0, -3.0, 0.0),), (5.0,), (1,))
        with self.assertRaisesRegex(
                SpherePhysicalSchemaError,
                "exact_tangent_unsupported_by_optix9_front_face_contract"):
            verify_motion_segments(
                ((-3.0, -4.0, 0.0),), ((3.0, 4.0, 0.0),),
                centers=centers, radii=radii,
            )

    def test_front_entry_guard_rejects_both_closed_trace_boundaries(self):
        from rtdsl.v4_sphere_physical_schema import (
            SPHERE_FRONT_ENTRY_ENDPOINT_MARGIN,
            SpherePhysicalSchemaError, verify_motion_segments,
            verify_reference_sphere_contents,
        )

        self.assertEqual(SPHERE_FRONT_ENTRY_ENDPOINT_MARGIN.denominator, 1 << 12)
        f32_predecessor_of_one = struct.unpack(
            "<f", struct.pack("<I", 0x3F7FFFFF))[0]

        cases = (
            # The exact front entry is 1 + 2^-24 after f32 projection.
            (((2.0, 0.0, 0.0),), (f32_predecessor_of_one,),
             ((0.0, 0.0, 0.0),), ((1.0, 0.0, 0.0),)),
            # Exact tmax equality is also inside the frozen closed-boundary guard.
            (((2.0, 0.0, 0.0),), (1.0,),
             ((0.0, 0.0, 0.0),), ((1.0, 0.0, 0.0),)),
            # The exact front entry is 1 - predecessor(1), just above tmin.
            (((1.0, 0.0, 0.0),), (f32_predecessor_of_one,),
             ((0.0, 0.0, 0.0),), ((1.0, 0.0, 0.0),)),
        )
        for raw_centers, raw_radii, starts, ends in cases:
            with self.subTest(centers=raw_centers, radii=raw_radii):
                centers, radii, _ = verify_reference_sphere_contents(
                    raw_centers, raw_radii, (7,))
                with self.assertRaisesRegex(
                        SpherePhysicalSchemaError,
                        "front_entry_near_closed_trace_interval_boundary"):
                    verify_motion_segments(
                        starts, ends, centers=centers, radii=radii)

    def test_front_entry_guard_keeps_interior_hit_and_far_exterior_miss(self):
        from rtdsl.v4_sphere_physical_schema import (
            verify_motion_segments, verify_reference_sphere_contents,
        )

        centers, radii, _ = verify_reference_sphere_contents(
            ((3.0, 0.0, 0.0),), (1.0,), (7,))
        interior = verify_motion_segments(
            ((0.0, 0.0, 0.0),), ((4.0, 0.0, 0.0),),
            centers=centers, radii=radii)
        far_exterior = verify_motion_segments(
            ((0.0, 0.0, 0.0),), ((1.0, 0.0, 0.0),),
            centers=centers, radii=radii)
        self.assertEqual(len(interior), 1)
        self.assertEqual(len(far_exterior), 1)
        self.assertEqual(
            ORACLE.first_contact(
                (0.0, 0.0, 0.0), (4.0, 0.0, 0.0),
                centers, radii, (7,)),
            (1, ORACLE.f32_bits(0.5), 7),
        )
        self.assertEqual(
            ORACLE.first_contact(
                (0.0, 0.0, 0.0), (1.0, 0.0, 0.0),
                centers, radii, (7,)),
            (0, ORACLE.f32_bits(1.0), ORACLE.U32_MAX),
        )

    def test_output_policy_exact_bits_and_nonexact_ulp_bound(self):
        from rtdsl.v4_sphere_physical_schema import (
            SpherePhysicalSchemaError, verify_first_contact_expected_outputs,
            verify_motion_segments, verify_reference_sphere_contents,
        )

        centers, radii, ids = verify_reference_sphere_contents(
            ((0.2, 0.0, 0.0),), (0.03,), (7,))
        queries = verify_motion_segments(
            ((0.0, 0.0, 0.0),), ((1.0, 0.0, 0.0),),
            centers=centers, radii=radii,
        )
        expected = (ORACLE.first_contact(
            (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), centers, radii, ids),)
        observed = ((expected[0][0], expected[0][1] + 4, expected[0][2]),)
        self.assertEqual(verify_first_contact_expected_outputs(
            observed, expected, queries, centers=centers, radii=radii,
            application_ids=ids), ("nonexact_t_ulp_le_4",))
        observed_minus = ((expected[0][0], expected[0][1] - 4, expected[0][2]),)
        self.assertEqual(verify_first_contact_expected_outputs(
            observed_minus, expected, queries, centers=centers, radii=radii,
            application_ids=ids), ("nonexact_t_ulp_le_4",))
        with self.assertRaisesRegex(SpherePhysicalSchemaError, "expected_output_t_ulp"):
            verify_first_contact_expected_outputs(
                ((1, expected[0][1] + 5, 7),), expected, queries,
                centers=centers, radii=radii, application_ids=ids)

        exact_centers, exact_radii, exact_ids = verify_reference_sphere_contents(
            ((3.0, 0.0, 0.0),), (1.0,), (9,))
        exact_queries = verify_motion_segments(
            ((0.0, 0.0, 0.0),), ((4.0, 0.0, 0.0),),
            centers=exact_centers, radii=exact_radii)
        exact_expected = (ORACLE.first_contact(
            (0, 0, 0), (4, 0, 0), exact_centers, exact_radii, exact_ids),)
        with self.assertRaisesRegex(
                SpherePhysicalSchemaError, "expected_output_exact_root_bits"):
            verify_first_contact_expected_outputs(
                ((1, exact_expected[0][1] + 1, 9),), exact_expected,
                exact_queries, centers=exact_centers, radii=exact_radii,
                application_ids=exact_ids)
        with self.assertRaisesRegex(
                SpherePhysicalSchemaError, "expected_output_exact_root_bits"):
            verify_first_contact_expected_outputs(
                ((1, exact_expected[0][1] - 1, 9),), exact_expected,
                exact_queries, centers=exact_centers, radii=exact_radii,
                application_ids=exact_ids)

    def test_motion_batch_rejects_extra_row_item_without_truncation(self):
        from rtdsl.v4_public_builtin_sphere import (
            MotionSegmentBatch, PublicSphereLifecycleError,
        )

        with self.assertRaisesRegex(PublicSphereLifecycleError, "GS014_QUERY_SHAPE"):
            MotionSegmentBatch((((0, 0, 0), (1, 0, 0), "discard-me"),))

    def test_motion_batch_rejects_non_vec3_endpoint(self):
        from rtdsl.v4_public_builtin_sphere import (
            MotionSegmentBatch, PublicSphereLifecycleError,
        )

        with self.assertRaisesRegex(PublicSphereLifecycleError, "GS014_QUERY_SHAPE"):
            MotionSegmentBatch((((0, 0, 0, 0), (1, 0, 0)),))

    def test_home_fixture_has_heterogeneous_radii_and_grazing_front_entry(self):
        fixture = VALIDATION._first_contact_fixture()
        self.assertGreater(len(set(fixture["radii"])), 1)
        grazing_index = fixture["fixture_names"].index(
            "grazing_front_face_entry")
        start, end = fixture["queries"][grazing_index]
        center = fixture["centers"][-1]
        radius = fixture["radii"][-1]
        direction = tuple(end[i] - start[i] for i in range(3))
        numerator = sum(
            (center[i] - start[i]) * direction[i] for i in range(3))
        denominator = sum(value * value for value in direction)
        t = numerator / denominator
        closest = tuple(start[i] + t * direction[i] for i in range(3))
        distance2 = sum((closest[i] - center[i]) ** 2 for i in range(3))
        self.assertLess(distance2, radius * radius)
        self.assertEqual(ORACLE.first_contact(
            start, end, (center,), (radius,), (11,)),
            (1, ORACLE.f32_bits(0.3125), 11))

        # The associated exact grazing equality remains a mathematical hit in
        # the closed-sphere oracle and is deliberately outside the GPU domain.
        tangent_start = (0.0, 7.75, 0.0)
        tangent_end = (4.0, 7.75, 0.0)
        self.assertEqual(ORACLE.first_contact(
            tangent_start, tangent_end, (center,), (radius,), (11,)),
            (1, ORACLE.f32_bits(0.5), 11))


if __name__ == "__main__":
    unittest.main()
