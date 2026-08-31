from __future__ import annotations

import dataclasses
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from rtdsl.v4_callback_abi import CallbackAbiError, compile_callback_abi
from rtdsl.v4_callback_ir import CallbackRole
from rtdsl.v4_callback_numba_codegen import generate_formal_numba_leaf
from rtdsl.v4_triangle_optix_runtime import run_builtin_triangle_callback
from rtdsl.v4_triangle_optix_wrapper_codegen import (
    generate_trusted_optix_triangle_wrapper_v1,
)
from rtdsl.v4_typed_physical_schema import (
    default_reference_templates,
    lower_canonical_reference_plan,
    verify_typed_physical_schema,
)
from tests.goal5755_v4_typed_physical_schema_test import (
    orientation_authority,
    target,
    triangle_schema,
    verified_callback,
)


ROOT = Path(__file__).resolve().parents[1]


def admitted(native_sha256: str = "a" * 64):
    callback = verified_callback()
    orientation = orientation_authority(callback)
    return verify_typed_physical_schema(
        callback,
        triangle_schema(callback),
        target=target(native_sha256=native_sha256),
        orientation_authorities={orientation.authority_sha256: orientation},
    )


def compiled(authority):
    plan = lower_canonical_reference_plan(authority, default_reference_templates())
    abi = compile_callback_abi(
        authority.callback, physical_schema_authority=authority)
    wrapper = generate_trusted_optix_triangle_wrapper_v1(authority, plan, abi)
    return plan, abi, wrapper


class _FakeSymbol:
    argtypes = None
    restype = None

    def __call__(self, *args):
        output_0, output_1, output_2 = args[11], args[12], args[13]
        observed_primitive, observed_hit_kind = args[14], args[15]
        observed_barycentric_x, observed_barycentric_y = args[16], args[17]
        statuses, counters = args[18], args[19]
        # One front-facing hit followed by one miss.
        output_0[0], output_1[0], output_2[0] = 11, 13, 0
        output_0[1] = output_1[1] = output_2[1] = 0xFFFFFFFF
        observed_primitive[0], observed_hit_kind[0] = 0, 0xFE
        observed_barycentric_x[0], observed_barycentric_y[0] = 0.2, 0.2
        observed_primitive[1] = observed_hit_kind[1] = 0xFFFFFFFF
        required = (1 << 1) | (1 << 6)
        statuses[0].invocation_mask = required | (1 << 4)
        statuses[1].invocation_mask = required | (1 << 5)
        counters[1] = 2
        counters[4] = 1
        counters[5] = 1
        counters[6] = 2
        return 0


class _FakeLibrary:
    def __init__(self):
        self.rtdl_optix_v4_run_builtin_triangle_callback_v1 = _FakeSymbol()


class _FakeSession:
    aborted = False

    def finish(self, **kwargs):
        return {
            "physical_executor_classification": "optix_traversal_observed",
            "semantic_digest": kwargs["semantic_digest"],
            "output_digest": kwargs["output_digest"],
        }

    def abort(self):
        self.aborted = True


class Goal5756BuiltinTriangleRuntimeTest(unittest.TestCase):
    def test_triangle_abi_and_all_four_numba_leaves_are_generated(self):
        authority = admitted()
        _plan, abi, _wrapper = compiled(authority)
        self.assertEqual(
            [item.role for item in abi.roles],
            [
                CallbackRole.MAKE_RAY,
                CallbackRole.CLOSEST_HIT,
                CallbackRole.MISS,
                CallbackRole.FINALIZE,
            ],
        )
        generated = [
            generate_formal_numba_leaf(
                authority.callback,
                abi,
                role,
                physical_schema_authority=authority,
            )
            for role in (
                CallbackRole.MAKE_RAY,
                CallbackRole.CLOSEST_HIT,
                CallbackRole.MISS,
                CallbackRole.FINALIZE,
            )
        ]
        self.assertEqual(len({item.generated_source_sha256 for item in generated}), 4)
        self.assertIn("in_hit_primitive_index", generated[1].generated_source)
        self.assertIn("in_first_side_columns", generated[1].generated_source)

    def test_wrapper_uses_optix_owned_deterministic_triangle_channels(self):
        _plan, _abi, wrapper = compiled(admitted())
        self.assertIn("optixGetPrimitiveIndex()", wrapper.source)
        self.assertIn("optixGetHitKind()", wrapper.source)
        self.assertIn("optixGetTriangleBarycentrics()", wrapper.source)
        self.assertIn("__anyhit__rtdl_v4_triangle_canonical", wrapper.source)
        self.assertIn("OPTIX_RAY_FLAG_NONE", wrapper.source)
        self.assertIn(
            "hit_t == current_t && canonical_primitive < current_primitive",
            wrapper.source,
        )
        self.assertIn("optixIgnoreIntersection()", wrapper.source)
        self.assertIn("params.boundary_owner[primitive_index * 7u", wrapper.source)
        self.assertIn("params.triangle_indices[selected_primitive_index]", wrapper.source)
        self.assertIn("direction_dot_normal < 0.0f ? 0xfeu : 0xffu", wrapper.source)
        self.assertNotIn("__intersection__", wrapper.source)
        # The any-hit collector is trusted wrapper code, never a user role.
        self.assertNotIn("CallbackRole.ANY_HIT", wrapper.source)

    def test_serialized_or_forged_authority_cannot_enter_abi_or_wrapper(self):
        authority = admitted()
        plan, abi, _wrapper = compiled(authority)
        with self.assertRaisesRegex(CallbackAbiError, "physical_schema_authority_required"):
            compile_callback_abi(
                authority.callback,
                physical_schema_authority=authority.schema.to_dict(),
            )
        attacked = dataclasses.replace(authority, authority_nonce="0" * 64)
        with self.assertRaisesRegex(CallbackAbiError, "physical_schema_authority_reverification"):
            compile_callback_abi(
                authority.callback, physical_schema_authority=attacked)
        with self.assertRaisesRegex(Exception, "canonical_plan_binding"):
            generate_trusted_optix_triangle_wrapper_v1(
                authority, dataclasses.replace(plan, target_sha256="0" * 64), abi)

    def test_runtime_rechecks_native_plan_bindings_and_per_launch_lifecycle(self):
        with tempfile.TemporaryDirectory() as temporary:
            native_path = Path(temporary) / "librtdl_optix.so"
            native_path.write_bytes(b"goal5756-fake-native")
            native_sha = hashlib.sha256(native_path.read_bytes()).hexdigest()
            authority = admitted(native_sha)
            plan, abi, wrapper = compiled(authority)
            session = _FakeSession()
            with mock.patch(
                    "rtdsl.v4_triangle_optix_runtime.OptixTraversalAuditSession.open",
                    return_value=session), mock.patch(
                    "rtdsl.v4_triangle_optix_runtime.consume_verified_triangle_executable",
                    return_value=wrapper.source):
                result = run_builtin_triangle_callback(
                    authority,
                    plan,
                    abi,
                    object(),
                    vertices=((0, 0, 0), (1, 0, 0), (0, 1, 0)),
                    triangles=((0, 1, 2),),
                    front_values=(11,),
                    back_values=(13,),
                    queries=(
                        ((0.2, 0.2, 1.0), (0, 0, -1), 10.0),
                        ((2.0, 2.0, 1.0), (0, 0, -1), 10.0),
                    ),
                    expected_output=((11, 13, 0), (0xFFFFFFFF,) * 3),
                    library=_FakeLibrary(),
                    native_library_path=native_path,
                )
            self.assertEqual(result.output[0], (11, 13, 0))
            self.assertEqual(result.hit_observations[0]["primitive_index"], 0)
            self.assertEqual(result.hit_observations[0]["hit_kind"], 0xFE)
            self.assertIsNone(result.hit_observations[1]["primitive_index"])
            self.assertEqual(result.role_counters[4:7], (1, 1, 2))
            self.assertFalse(session.aborted)
            attacked = dataclasses.replace(
                authority,
                target=dataclasses.replace(authority.target, native_sha256="0" * 64),
            )
            with self.assertRaisesRegex(RuntimeError, "authority does not rederive"):
                run_builtin_triangle_callback(
                    attacked, plan, abi, object(),
                    vertices=((0, 0, 0), (1, 0, 0), (0, 1, 0)),
                    triangles=((0, 1, 2),), front_values=(11,), back_values=(13,),
                    queries=(((0.2, 0.2, 1), (0, 0, -1), 10),),
                    library=_FakeLibrary(), native_library_path=native_path,
                )

    def test_raw_or_serialized_ptx_cannot_enter_runtime(self):
        authority = admitted()
        plan, abi, wrapper = compiled(authority)
        with self.assertRaisesRegex(TypeError, "live VerifiedTriangleExecutable"):
            run_builtin_triangle_callback(
                authority, plan, abi, wrapper.source,
                vertices=((0, 0, 0), (1, 0, 0), (0, 1, 0)),
                triangles=((0, 1, 2),), front_values=(11,), back_values=(13,),
                queries=(((0.2, 0.2, 1), (0, 0, -1), 10),),
            )

    def test_native_route_is_builtin_triangle_and_has_no_user_intersection_parameter(self):
        native = (ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text()
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text()
        self.assertIn(
            "TriangleAccelHolder accel = build_v4_triangle_anyhit_accel", native)
        self.assertIn("OPTIX_PRIMITIVE_TYPE_FLAGS_TRIANGLE", native)
        self.assertIn('"__anyhit__rtdl_v4_triangle_canonical"', native)
        self.assertIn("std::vector<uint32_t> boundary_owner", native)
        self.assertIn("parameters.boundary_owner", native)
        section = api.split("rtdl_optix_v4_run_builtin_triangle_callback_v1", 1)[1]
        section = section.split("// Goal5752", 1)[0]
        self.assertNotIn("intersection_ptx", section)

    def test_product_modules_have_no_application_or_publication_dispatch(self):
        for relative in (
            "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
            "src/rtdsl/v4_triangle_optix_compiler.py",
            "src/rtdsl/v4_triangle_optix_runtime.py",
        ):
            source = (ROOT / relative).read_text().lower()
            for forbidden in (
                "particle_tracking", "arkade", "rtnn", "paper-reproduction",
                "goal5753",
            ):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
