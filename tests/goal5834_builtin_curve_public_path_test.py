"""Goal5834 app-neutral built-in round-linear-curve public-path tests."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import importlib.util
from pathlib import Path
import struct
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_builtin_curve_standard_library import (  # noqa: E402
    CURVE_FIRST_CONTACT_SOURCE,
    curve_first_contact_manifest,
)
from rtdsl.v4_curve import (  # noqa: E402
    BuiltinCurveStaticInput,
    CurveMotionSegmentBatch,
    V4CurveTarget,
    curve_first_contact_source,
)
from rtdsl.v4_curve_physical_schema import (  # noqa: E402
    BuiltinCurvePhysicalSchema,
    CurvePhysicalSchemaError,
    CurveTargetProfile,
    verify_builtin_curve_physical_schema,
    verify_curve_motion_segments,
    verify_reference_curve_contents,
)
from rtdsl.v4_public_builtin_curve import (  # noqa: E402
    verify_builtin_curve_callback_source,
)


ORACLE_PATH = ROOT / "examples/first_contact_curve/first_contact_oracle.py"
_ORACLE_SPEC = importlib.util.spec_from_file_location(
    "goal5834_independent_oracle", ORACLE_PATH)
assert _ORACLE_SPEC is not None and _ORACLE_SPEC.loader is not None
ORACLE = importlib.util.module_from_spec(_ORACLE_SPEC)
_ORACLE_SPEC.loader.exec_module(ORACLE)


def _target() -> CurveTargetProfile:
    return CurveTargetProfile("optix", "9.0.0", "8.9", "1" * 64)


def _authority():
    source = verify_builtin_curve_callback_source(
        CURVE_FIRST_CONTACT_SOURCE, curve_first_contact_manifest())
    callback = source.callback
    schema = BuiltinCurvePhysicalSchema(
        callback.ir_sha256, callback.effect_digest,
        "curve_control_points", "curve_widths", "curve_segment_indices",
        "application_ids", "motion_segments", "first_contacts",
        "device_status",
    )
    return verify_builtin_curve_physical_schema(
        callback, schema, target=_target())


class Goal5834BuiltinCurvePublicPathTest(unittest.TestCase):
    def test_public_surface_compiles_one_canonical_curve_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            native = Path(directory) / "librtdl_optix.so"
            native.write_bytes(b"goal5834-native-identity")
            target = V4CurveTarget.from_native(
                native, optix_sdk="9.0.0", compute_capability="8.9")
            source = curve_first_contact_source()
            program = source.compile(target=target)
        self.assertEqual(
            program.authority.schema.geometry_family,
            "builtin_round_linear_curve")
        self.assertEqual(program.authority.schema.curve_type, "round_linear")
        self.assertFalse(program.authority.canonical_plan.executable)
        self.assertIn("__raygen__rtdl_v4_curve", program.wrapper.source)
        self.assertIn(
            "__anyhit__rtdl_v4_curve_canonical", program.wrapper.source)
        self.assertNotIn("__intersection__", program.wrapper.source)
        self.assertNotIn("__raygen__rtdl_v4_sphere", program.wrapper.source)
        self.assertEqual(len(program.abi.roles), 4)

    def test_native_route_uses_builtin_round_linear_and_no_user_is(self):
        core = (ROOT / "src/native/optix/rtdl_optix_core.cpp").read_text()
        native = (
            ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
        ).read_text()
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text()
        required = (
            "OPTIX_BUILD_INPUT_TYPE_CURVES",
            "OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR",
            "OPTIX_CURVE_ENDCAP_DEFAULT",
            "OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL",
            "__raygen__rtdl_v4_curve",
            "__miss__rtdl_v4_curve",
            "__anyhit__rtdl_v4_curve_canonical",
            "rtdl.v4.native_builtin_curve_descriptor.v1",
        )
        for text in required:
            self.assertIn(text, native)
        self.assertIn(
            "builtin_options.curveEndcapFlags = "
            "spec.builtin_is_curve_endcap_flags", core)
        for symbol in (
            "rtdl_optix_v4_prepare_builtin_curve_callback_v1",
            "rtdl_optix_v4_execute_prepared_builtin_curve_callback_v1",
            "rtdl_optix_v4_describe_prepared_builtin_curve_callback_v1",
            "rtdl_optix_v4_destroy_prepared_builtin_curve_callback_v1",
        ):
            self.assertIn(symbol, api)
        curve_prepare = native.split(
            "static uint64_t prepare_v4_builtin_curve_callback", 1)[1].split(
                "static std::shared_ptr<V4PreparedBuiltinCurve>", 1)[0]
        self.assertNotIn("const char* intersection_program", curve_prepare)
        self.assertIn(
            "facts.builtin_is_module = "
            "prepared->pipeline->builtin_is_module != nullptr",
            curve_prepare)
        self.assertIn(
            "facts.user_intersection_program = spec.intersection_name != nullptr",
            curve_prepare)

    def test_every_curve_schema_leaf_is_decision_bearing(self):
        authority = _authority()
        good = authority.schema
        mutations = {
            "control_point_field_id": "different_control_points",
            "width_field_id": "different_widths",
            "segment_index_field_id": "different_indices",
            "application_id_field_id": "different_ids",
            "query_field_id": "different_queries",
            "output_field_id": "different_outputs",
            "status_field_id": "different_status",
            "contract_name": "different_contract",
            "template_id": "different_template",
            "geometry_family": "different_family",
            "curve_type": "round_quadratic",
            "endcap_policy": "flat",
            "width_policy": "tapered",
            "gas_update_policy": "updateable",
            "graph_depth": 2,
            "sbt_record_count": 2,
            "motion_blur": True,
            "primitive_index_offset": 1,
            "stable_order": ("application_id",),
            "schema_id": "different_schema",
            "schema_version": "v2",
        }
        for field, value in mutations.items():
            with self.subTest(field=field), self.assertRaises(
                    CurvePhysicalSchemaError):
                verify_builtin_curve_physical_schema(
                    authority.callback, replace(good, **{field: value}),
                    target=authority.target)
        for changes in (
            {"supports_builtin_round_linear_curve": False},
            {"max_graph_depth": 2},
        ):
            with self.assertRaises(CurvePhysicalSchemaError):
                replace(authority.target, **changes)

    def test_static_input_boundary_accepts_capsules_and_rejects_extensions(self):
        valid = verify_reference_curve_contents(
            ((0, -1, 0), (0, 1, 0), (2, 0, 0), (3, 0, 0)),
            (0.25, 0.25, 0.5, 0.5), (0, 2), (10, 20))
        self.assertEqual(valid[2], (0, 2))
        self.assertEqual(
            BuiltinCurveStaticInput(*valid).application_ids, (10, 20))
        cases = (
            (((0, 0, 0),), (1,), (0,), (1,)),
            (((0, 0, 0), (0, 0, 0)), (1, 1), (0,), (1,)),
            (((0, 0, 0), (1, 0, 0)), (0, 0), (0,), (1,)),
            (((0, 0, 0), (1, 0, 0)), (1, 2), (0,), (1,)),
            (((0, 0, 0), (1, 0, 0)), (1, 1), (1,), (1,)),
            (((0, 0, 0), (1, 0, 0), (2, 0, 0)),
             (1, 1, 1), (0, 0), (1, 2)),
            (((0, 0, 0), (1, 0, 0), (2, 0, 0)),
             (1, 1, 1), (0, 1), (1, 1)),
        )
        for values in cases:
            with self.subTest(values=values), self.assertRaises(
                    CurvePhysicalSchemaError):
                verify_reference_curve_contents(*values)

    def test_independent_oracle_covers_side_miss_endcap_nearest_tie_and_radii(self):
        points = (
            (0, -1, 0), (0, 1, 0),
            (0, -1, 0), (0, 1, 0),
            (-0.5, -1, 3), (-0.5, 1, 3),
            (0.5, -1, 3), (0.5, 1, 3),
            (2, 0, 6), (3, 0, 6),
        )
        widths = (0.25, 0.25, 0.25, 0.25,
                  0.125, 0.125, 0.25, 0.25, 0.5, 0.5)
        indices = (0, 2, 4, 6, 8)
        ids = (100, 50, 900, 1, 77)
        queries = (
            ((-1, 0, 0), (1, 0, 0)),
            ((-1, 2, 0), (1, 2, 0)),
            ((-1, 0, 3), (1, 0, 3)),
            ((1.75, 1, 6), (1.75, -1, 6)),
        )
        expected = ORACLE.first_contact(
            points, widths, indices, ids, queries)
        self.assertEqual(expected, (
            (1, struct.unpack("<I", struct.pack("<f", 0.375))[0], 50),
            (0, struct.unpack("<I", struct.pack("<f", 1.0))[0], 0xFFFFFFFF),
            (1, struct.unpack("<I", struct.pack("<f", 0.1875))[0], 900),
            (1, 1049699860, 77),
        ))
        normalized = verify_reference_curve_contents(
            points, widths, indices, ids)
        rows = verify_curve_motion_segments(
            tuple(row[0] for row in queries), tuple(row[1] for row in queries),
            control_points=normalized[0], widths=normalized[1],
            segment_indices=normalized[2])
        self.assertEqual(len(rows), 4)
        self.assertEqual(len(CurveMotionSegmentBatch(queries).queries), 4)
        with self.assertRaisesRegex(
                CurvePhysicalSchemaError, "near_parallel_curve_query"):
            verify_curve_motion_segments(
                ((1.0, 0.0, 6.0),), ((2.5, 0.0, 6.0),),
                control_points=normalized[0], widths=normalized[1],
                segment_indices=normalized[2])

    def test_oracle_orders_float32_time_before_application_id(self):
        points = (
            (0.0, -1.0, 0.0), (0.0, 1.0, 0.0),
            (0.01, -1.0, 0.0), (0.01, 1.0, 0.0),
        )
        widths = (0.25, 0.25, 0.25, 0.25)
        indices = (0, 2)
        ids = (100, 1)
        queries = (((-1.0e6, 0.0, 0.0), (1.0e6, 0.0, 0.0)),)
        normalized = verify_reference_curve_contents(
            points, widths, indices, ids)
        verify_curve_motion_segments(
            tuple(row[0] for row in queries),
            tuple(row[1] for row in queries),
            control_points=normalized[0], widths=normalized[1],
            segment_indices=normalized[2])
        self.assertEqual(
            ORACLE.first_contact(points, widths, indices, ids, queries),
            ((1, 0x3EFFFFFC, 1),),
        )

    def test_oracle_is_independent_and_public_source_is_exact(self):
        oracle = ORACLE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("rtdsl", oracle.lower())
        self.assertEqual(
            curve_first_contact_source().source_sha256,
            hashlib.sha256(CURVE_FIRST_CONTACT_SOURCE.encode()).hexdigest())


if __name__ == "__main__":
    unittest.main()
