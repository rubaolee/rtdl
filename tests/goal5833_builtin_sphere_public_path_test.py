from __future__ import annotations

from dataclasses import replace
import hashlib
import importlib.util
import os
from pathlib import Path
import struct
import subprocess
import sys
import textwrap
import unittest

from rtdsl.v4_builtin_sphere_standard_library import (
    build_first_contact_authority,
    compile_first_contact_callback,
)
from rtdsl.v4_callback_ir import CallbackRole
from rtdsl.v4_sphere_physical_schema import (
    BuiltinSpherePhysicalSchema,
    SpherePhysicalSchemaError,
    SphereTargetProfile,
    verify_builtin_sphere_physical_schema,
    verify_motion_segments,
    verify_reference_sphere_contents,
)


ROOT = Path(__file__).resolve().parents[1]
ORACLE_PATH = ROOT / "examples/first_contact_sphere/first_contact_oracle.py"
SPEC = importlib.util.spec_from_file_location("goal5833_first_contact_oracle", ORACLE_PATH)
ORACLE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(ORACLE)


def target():
    return SphereTargetProfile("optix", "9.0.0", "8.9", "1" * 64)


class Goal5833BuiltinSpherePublicPathTest(unittest.TestCase):
    def test_public_sphere_import_is_compiler_and_native_quiet(self):
        code = textwrap.dedent("""
            import ctypes
            import subprocess
            import sys
            baseline = set(sys.modules)
            def forbidden(*args, **kwargs):
                raise AssertionError('native/compiler action during sphere import')
            ctypes.CDLL = forbidden
            subprocess.Popen = forbidden
            import rtdsl.v4_sphere as public
            public.first_contact_source()
            newly_forbidden = sorted(name for name in set(sys.modules) - baseline if
                name == 'cupy' or name.startswith('cupy.') or
                'optix_compiler' in name or 'prepared_runtime' in name or
                name == 'rtdsl.v4_callback_numba_codegen')
            if newly_forbidden:
                raise SystemExit('new backend imports: ' + repr(newly_forbidden))
        """)
        environment = dict(os.environ)
        environment["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(ROOT)))
        completed = subprocess.run(
            [sys.executable, "-c", code], cwd=ROOT, env=environment,
            text=True, capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_public_v4_surface_exposes_complete_sphere_lifecycle(self):
        import rtdsl.v4_sphere as public
        for name in (
            "BuiltinSphereStaticInput", "MotionSegmentBatch", "V4SphereTarget",
            "VerifiedBuiltinSphereSource", "VerifiedBuiltinSphereProgram",
            "MaterializedBuiltinSphereProgram", "PreparedBuiltinSphereProgram",
            "first_contact_source", "compile_builtin_sphere_callback_program",
            "materialize_builtin_sphere_callback_program",
        ):
            self.assertIn(name, public.__all__)
            self.assertTrue(hasattr(public, name), name)

    def test_native_route_uses_optix_builtin_sphere_and_live_descriptor(self):
        core = (ROOT / "src/native/optix/rtdl_optix_core.cpp").read_text("utf-8")
        poc = (ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text(
            "utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text("utf-8")
        self.assertIn("optixBuiltinISModuleGet", core)
        for literal in (
            "OPTIX_BUILD_INPUT_TYPE_SPHERES",
            "OPTIX_PRIMITIVE_TYPE_SPHERE",
            "OPTIX_PRIMITIVE_TYPE_FLAGS_SPHERE",
            "OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL",
            "describe_v4_prepared_builtin_sphere",
        ):
            self.assertIn(literal, poc)
        for symbol in (
            "rtdl_optix_v4_prepare_builtin_sphere_callback_v1",
            "rtdl_optix_v4_execute_prepared_builtin_sphere_callback_v1",
            "rtdl_optix_v4_describe_prepared_builtin_sphere_callback_v1",
            "rtdl_optix_v4_destroy_prepared_builtin_sphere_callback_v1",
        ):
            self.assertIn(symbol, api)
        descriptor = poc.split(
            "static std::string describe_v4_prepared_builtin_sphere", 1)[1].split(
                "static void execute_v4_prepared_builtin_sphere_callback", 1)[0]
        self.assertIn("facts.build_input_type", descriptor)
        self.assertIn("facts.primitive_type", descriptor)
        self.assertIn("prepared->compiled_optix_version", descriptor)
        self.assertIn("prepared->cuda_compute_capability_major", descriptor)
        self.assertNotIn("OPTIX_BUILD_INPUT_TYPE_SPHERES", descriptor)
        self.assertNotIn("OPTIX_PRIMITIVE_TYPE_SPHERE", descriptor)
        self.assertIn("device_static_input_fingerprint", poc)
        self.assertIn(
            "download(observed_centers.data(), prepared->accel.center_buf",
            poc)

    def test_independent_oracle_has_no_rtdl_dependency(self):
        source = ORACLE_PATH.read_text("utf-8")
        self.assertNotIn("import rtdsl", source)
        self.assertNotIn("from rtdsl", source)

    def test_frozen_goal5755_schema_bytes_remain_unchanged(self):
        expected = {
            "src/rtdsl/v4_typed_physical_schema.py":
                "f1b093da9aa10465767beec8f22f804e080a6691abd7ec1873de231328cc7e5d",
            "src/rtdsl/v4_callback_abi.py":
                "3f4be4d998ee91600c6a1f4bba4fadbb435f23d193a49f4cbf6dc50522d74fb5",
            "src/rtdsl/v4.py":
                "5800a38193275b3c6e37dfc6a0aadfe6d3fbdd6c108af93ef3799dc296c7f582",
        }
        for relative, digest in expected.items():
            self.assertEqual(
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), digest,
                relative)

    def test_four_role_source_and_sphere_authority_compile(self):
        callback = compile_first_contact_callback()
        roles = {item.role for item in callback.program.functions}
        self.assertEqual(roles, {
            CallbackRole.MAKE_RAY, CallbackRole.CLOSEST_HIT,
            CallbackRole.MISS, CallbackRole.FINALIZE,
        })
        authority, abi, wrapper = build_first_contact_authority(target())
        self.assertEqual(authority.callback, callback)
        self.assertFalse(authority.canonical_plan.executable)
        self.assertEqual(len(abi.roles), 4)
        self.assertIn("__anyhit__rtdl_v4_sphere_canonical", wrapper.source)
        self.assertIn("application_id<current_id", wrapper.source)
        self.assertNotIn("primitive<current_primitive", wrapper.source)
        self.assertEqual(
            authority.schema.stable_order,
            ("ordered_float32_t", "application_id"),
        )
        self.assertNotIn("__intersection__", wrapper.source)
        self.assertEqual(hashlib.sha256(wrapper.source.encode()).hexdigest(), wrapper.source_sha256)

    def test_schema_cannot_rebind_callback_or_relax_static_gas(self):
        callback = compile_first_contact_callback()
        good = BuiltinSpherePhysicalSchema(
            callback.ir_sha256, callback.effect_digest,
            "sphere_centers", "sphere_radii", "application_ids",
            "motion_segments", "first_contacts", "device_status")
        verify_builtin_sphere_physical_schema(callback, good, target=target())
        with self.assertRaisesRegex(SpherePhysicalSchemaError, "callback_binding"):
            verify_builtin_sphere_physical_schema(
                callback,
                BuiltinSpherePhysicalSchema(
                    "0" * 64, callback.effect_digest,
                    "sphere_centers", "sphere_radii", "application_ids",
                    "motion_segments", "first_contacts", "device_status"),
                target=target(),
            )

    def test_closed_field_ids_and_target_versions_are_decision_bearing(self):
        callback = compile_first_contact_callback()
        good = BuiltinSpherePhysicalSchema(
            callback.ir_sha256, callback.effect_digest,
            "sphere_centers", "sphere_radii", "application_ids",
            "motion_segments", "first_contacts", "device_status")
        for field in (
            "center_field_id", "radius_field_id", "application_id_field_id",
            "query_field_id", "output_field_id", "status_field_id",
        ):
            with self.subTest(field=field), self.assertRaisesRegex(
                    SpherePhysicalSchemaError, "field_identity"):
                verify_builtin_sphere_physical_schema(
                    callback, replace(good, **{field: f"mutated_{field}"}),
                    target=target())
        for optix_sdk, compute_capability in (
            ("NOT_AN_OPTIX_VERSION", "8.9"),
            ("9.0", "8.9"),
            ("09.0.0", "8.9"),
            ("9.0.0", "NOT_A_COMPUTE_CAPABILITY"),
            ("9.0.0", "8"),
            ("9.0.0", "08.9"),
        ):
            with self.subTest(
                    optix_sdk=optix_sdk,
                    compute_capability=compute_capability), self.assertRaisesRegex(
                        SpherePhysicalSchemaError, "target_version"):
                SphereTargetProfile(
                    "optix", optix_sdk, compute_capability, "1" * 64)
        with self.assertRaisesRegex(SpherePhysicalSchemaError, "gas_contract"):
            verify_builtin_sphere_physical_schema(
                callback,
                BuiltinSpherePhysicalSchema(
                    callback.ir_sha256, callback.effect_digest,
                    "sphere_centers", "sphere_radii", "application_ids",
                    "motion_segments", "first_contacts", "device_status",
                    motion_blur=True),
                target=target(),
            )

    def test_static_and_query_contract_fail_before_launch(self):
        centers, radii, ids = verify_reference_sphere_contents(
            ((2.0, 0.0, 0.0),), (1.0,), (7,))
        self.assertEqual(len(verify_motion_segments(
            ((0.0, 0.0, 0.0),), ((4.0, 0.0, 0.0),),
            centers=centers, radii=radii)), 1)
        for invalid_radii in ((0.0,), (float("nan"),), (-1.0,)):
            with self.assertRaises(SpherePhysicalSchemaError):
                verify_reference_sphere_contents(centers, invalid_radii, ids)
        with self.assertRaisesRegex(SpherePhysicalSchemaError, "duplicate_application_id"):
            verify_reference_sphere_contents(
                ((2.0, 0.0, 0.0), (4.0, 0.0, 0.0)), (1.0, 1.0), (7, 7))
        with self.assertRaisesRegex(SpherePhysicalSchemaError, "zero_direction"):
            verify_motion_segments(((0.0, 0.0, 0.0),), ((0.0, 0.0, 0.0),),
                                   centers=centers, radii=radii)
        with self.assertRaisesRegex(SpherePhysicalSchemaError, "start_not_strictly_outside"):
            verify_motion_segments(((2.0, 0.0, 0.0),), ((4.0, 0.0, 0.0),),
                                   centers=centers, radii=radii)

    def test_independent_oracle_reader_checkable_fixtures(self):
        bits_half = struct.unpack("<I", struct.pack("<f", 0.5))[0]
        self.assertEqual(ORACLE.first_contact(
            (0, 0, 0), (4, 0, 0), ((3, 0, 0),), (1,), (7,)),
            (1, bits_half, 7))
        self.assertEqual(ORACLE.first_contact(
            (0, 0, 0), (4, 0, 0), ((2, 3, 0),), (1,), (7,))[0], 0)
        self.assertEqual(ORACLE.first_contact(
            (0, 0, 0), (4, 0, 0), ((6, 0, 0),), (1,), (7,))[0], 0)
        self.assertEqual(ORACLE.first_contact(
            (0, 0, 0), (4, 0, 0), ((3, 0, 0), (3, 0, 0)), (1, 1), (9, 2)),
            (1, bits_half, 2))
        self.assertEqual(ORACLE.first_contact(
            (0, 0, 0), (8, 0, 0), ((5, 0, 0), (3, 0, 0)), (1, 1), (2, 99))[2], 99)
        self.assertEqual(ORACLE.first_contact(
            (0, 0, 0), (4, 0, 0), ((2, 1, 0),), (1,), (11,)),
            (1, bits_half, 11))


if __name__ == "__main__":
    unittest.main()
