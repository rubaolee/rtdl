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
from rtdsl.v4_callback_poc import DeviceFunctionArtifact
from rtdsl.v4_callback_ptx_composer import ComposedCallbackPtx
from rtdsl import v4_triangle_optix_compiler as triangle_compiler
from rtdsl.v4_triangle_optix_runtime import run_builtin_triangle_callback
from rtdsl.v4_triangle_optix_wrapper_codegen import (
    generate_trusted_optix_triangle_wrapper_v1,
)
from rtdsl.v4_typed_physical_schema import (
    TriangleHitSelectionPolicy,
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
    def test_triangle_compiler_batches_all_fallback_leaves_in_one_child(self):
        with mock.patch(
            "tests.goal5755_v4_typed_physical_schema_test.author_source_bytes",
            return_value=b"goal5756-batch-fixture",
        ):
            authority = admitted()
        plan, abi, _wrapper = compiled(authority)
        wrapper_ptx = (
            ".version 8.4\n.target sm_89\n.address_size 64\n")

        def compile_batch(leaves, **kwargs):
            self.assertEqual(
                tuple(item.role for item in leaves),
                (
                    CallbackRole.MAKE_RAY,
                    CallbackRole.CLOSEST_HIT,
                    CallbackRole.MISS,
                    CallbackRole.FINALIZE,
                ),
            )
            return tuple(
                DeviceFunctionArtifact(
                    schema="rtdl.v4.formal_device_function_artifact.v1",
                    role=leaf.role.value,
                    abi_name=leaf.abi_name,
                    compute_capability=kwargs["compute_capability"],
                    numeric_mode=leaf.numeric_mode,
                    generated_source_sha256=leaf.generated_source_sha256,
                    ir_sha256=leaf.callback_ir_sha256,
                    ptx=f"// {leaf.role.value}\n",
                    ptx_sha256=hashlib.sha256(
                        f"// {leaf.role.value}\n".encode()).hexdigest(),
                    ptx_version="8.4",
                    ptx_target="sm_89",
                    external_symbols=(),
                    numba_version=kwargs["expected_numba_version"],
                    python_version=kwargs["expected_python_version"],
                    nonce_word=leaf.nonce_word,
                    compiler_function_count=leaf.compiler_function_count,
                )
                for leaf in leaves
            )

        def compose(_wrapper_ptx, leaves, *, exact_symbols_by_role):
            self.assertEqual(_wrapper_ptx, wrapper_ptx)
            return ComposedCallbackPtx(
                ptx="composed-ptx",
                ptx_sha256=hashlib.sha256(b"composed-ptx").hexdigest(),
                ptx_version="8.4",
                ptx_target="sm_89",
                address_size="64",
                wrapper_ptx_sha256=hashlib.sha256(
                    wrapper_ptx.encode()).hexdigest(),
                leaf_bindings=tuple(
                    (leaf.role, exact_symbols_by_role[leaf.role])
                    for leaf in leaves
                ),
                stripped_wrapper_externs=tuple(exact_symbols_by_role.values()),
                stripped_numba_environments=(),
            )

        with mock.patch.object(
            triangle_compiler,
            "compile_formal_numba_leaves_isolated",
            side_effect=compile_batch,
        ) as batch, mock.patch.object(
            triangle_compiler,
            "_compile_nvrtc",
            return_value=(wrapper_ptx, "test log"),
        ), mock.patch.object(
            triangle_compiler,
            "compose_callback_ptx",
            side_effect=compose,
        ):
            executable, log = triangle_compiler.compile_verified_triangle_executable(
                authority,
                plan,
                abi,
                compute_capability=(8, 9),
                optix_include="/optix/include",
                cuda_include="/cuda/include",
                expected_python_version="3.12.0",
                expected_numba_version="0.65.1",
                expected_numpy_version="2.4.4",
            )

        batch.assert_called_once()
        self.assertEqual(log, "test log")
        self.assertEqual(
            tuple(item.role for item in executable.compiled_leaves),
            tuple(role.value for role in (
                CallbackRole.MAKE_RAY,
                CallbackRole.CLOSEST_HIT,
                CallbackRole.MISS,
                CallbackRole.FINALIZE,
            )),
        )

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

    def test_provider_native_closest_policy_is_explicit_and_distinct(self):
        authority = admitted()
        plan = lower_canonical_reference_plan(
            authority, default_reference_templates())
        abi = compile_callback_abi(
            authority.callback, physical_schema_authority=authority)
        canonical = generate_trusted_optix_triangle_wrapper_v1(
            authority, plan, abi)
        native = generate_trusted_optix_triangle_wrapper_v1(
            authority,
            plan,
            abi,
            hit_selection_policy=(
                TriangleHitSelectionPolicy.PROVIDER_NATIVE_CLOSEST),
        )
        self.assertEqual(
            canonical.physical_template,
            "builtin_triangle_adjacency_u32x3_v1",
        )
        self.assertEqual(
            native.physical_template,
            "builtin_triangle_u32x3_provider_native_closest_v1",
        )
        self.assertNotEqual(canonical.source_sha256, native.source_sha256)
        self.assertIn(
            "__closesthit__rtdl_v4_triangle_native", native.source)
        self.assertIn("OPTIX_RAY_FLAG_DISABLE_ANYHIT", native.source)
        self.assertNotIn(
            "__anyhit__rtdl_v4_triangle_canonical", native.source)
        self.assertNotIn("optixIgnoreIntersection()", native.source)
        with self.assertRaisesRegex(Exception, "hit_selection_policy"):
            generate_trusted_optix_triangle_wrapper_v1(
                authority, plan, abi, hit_selection_policy="native")

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
            "TriangleAccelHolder accel = build_v4_triangle_accel", native)
        self.assertIn("OPTIX_PRIMITIVE_TYPE_FLAGS_TRIANGLE", native)
        self.assertIn('"__anyhit__rtdl_v4_triangle_canonical"', native)
        self.assertIn('"__closesthit__rtdl_v4_triangle_native"', native)
        self.assertIn("OPTIX_GEOMETRY_FLAG_DISABLE_ANYHIT", native)
        self.assertIn("v4_ptx_declares_entry_point", native)
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
