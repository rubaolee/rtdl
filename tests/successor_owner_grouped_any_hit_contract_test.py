import dataclasses
import ctypes
import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from rtdsl.v4_curve_owner_grouped_any_hit import (
    BuiltinCurveOwnerGroupedAnyHitPhysicalSchema,
    CurveOwnerGroupedAnyHitError,
    verify_curve_owner_grouped_any_hit_physical_schema,
)
from rtdsl.v4_curve_owner_grouped_any_hit_standard_library import (
    build_curve_owner_grouped_any_hit_authority,
    compile_curve_owner_grouped_any_hit_callback,
)
from rtdsl.v4_curve_owner_grouped_any_hit_optix_wrapper_codegen import (
    generate_trusted_optix_curve_owner_grouped_any_hit_wrapper_v1,
)
from rtdsl.v4_curve_owner_grouped_any_hit_optix_compiler import (
    generate_curve_owner_grouped_any_hit_numba_leaf,
)
from rtdsl.v4_callback_ir import CallbackRole
from rtdsl.v4_curve_physical_schema import CurveTargetProfile
from rtdsl.v4_curve_owner_grouped_any_hit_public import (
    OwnerGroupedCurveQueryBatch,
    OwnerGroupedCurveStaticInput,
    V4CurveTarget,
    curve_owner_grouped_any_hit_source,
)
from rtdsl.v4_curve_owner_grouped_any_hit_prepared_runtime import (
    PreparedCurveOwnerGroupedAnyHit,
    _destroy_failed_prepare,
    _native_counter_fingerprint,
    _native_output_fingerprint,
    _native_query_fingerprint,
    _native_status_fingerprint,
    _read_descriptor,
    _require_descriptor_transition,
    _require_native_target_binding,
)
from rtdsl.v4_owner_grouped_any_hit import (
    OwnerGroupedAnyHitError,
    OwnerGroupedAnyHitSchema,
    compile_owner_grouped_any_hit_abi,
    derive_owner_grouped_any_hit_proof,
    execute_owner_grouped_any_hit_reference,
    owner_grouped_any_hit_output_sha256,
    verify_owner_grouped_any_hit_abi,
    verify_owner_grouped_any_hit_schema,
)


class SuccessorOwnerGroupedAnyHitContractTest(unittest.TestCase):
    @staticmethod
    def _initial_native_descriptor():
        return {
            "schema": "rtdl.v4.native_curve_owner_grouped_descriptor.v1",
            "native_build_id": "9" * 64,
            "build_input_type": 0x2145,
            "primitive_type": 0x2503,
            "primitive_type_flags": 1 << 3,
            "builtin_is_build_flags": 1 << 2,
            "builtin_is_curve_endcap_flags": 0,
            "builtin_is_module": True,
            "user_intersection_program": False,
            "uses_motion_blur": False,
            "build_flags": 1 << 2,
            "geometry_flags": 1 << 1,
            "vertex_stride_bytes": 12,
            "width_stride_bytes": 4,
            "index_stride_bytes": 4,
            "normal_buffers_present": False,
            "primitive_index_offset": 0,
            "sbt_record_count": 1,
            "gas_count": 1,
            "primitive_count": 2,
            "vertex_count": 4,
            "owner_count": 2,
            "motion_key_count": 0,
            "endcap_flags": 0,
            "traversable_graph_flags": 1 << 0,
            "max_payload_values": 1,
            "max_attribute_values": 0,
            "max_trace_depth": 1,
            "program_group_count": 3,
            "compiled_optix_version": 90000,
            "compiled_optix_major": 9,
            "compiled_optix_minor": 0,
            "compiled_optix_patch": 0,
            "cuda_device_ordinal": 0,
            "cuda_compute_capability_major": 8,
            "cuda_compute_capability_minor": 9,
            "cuda_driver_version": 12000,
            "static_input_fingerprint": "a" * 64,
            "device_static_input_fingerprint": "a" * 64,
            "vertex_device_pointer": 1,
            "width_device_pointer": 2,
            "index_device_pointer": 3,
            "owner_id_device_pointer": 4,
            "traversable_identity": 5,
            "execution_count": 0,
            "last_execution_present": False,
            "last_status_failed": False,
            "last_query_count": 0,
            "last_status_d2h_call_count": 0,
            "last_application_output_d2h_call_count": 0,
            "last_output_after_status_failure_count": 0,
            "last_query_fingerprint": "",
            "last_status_fingerprint": "",
            "last_counter_fingerprint": "",
            "last_output_fingerprint": "",
        }

    @staticmethod
    def _describe(descriptor):
        payload = json.dumps(
            descriptor, sort_keys=True, separators=(",", ":")).encode("utf-8")

        class Describe:
            def __call__(self, token, output, capacity, size_pointer, error, error_size):
                ctypes.cast(
                    size_pointer, ctypes.POINTER(ctypes.c_size_t))[0] = len(payload)
                if output is not None:
                    if capacity < len(payload):
                        return 1
                    ctypes.memmove(output, payload, len(payload))
                return 0

        return Describe()

    def test_reference_is_order_and_duplicate_invariant(self):
        owners = (0, 1, 1, 3)
        rows = ((9, 1), (2, 0), (3, 2), (9, 1))
        first = execute_owner_grouped_any_hit_reference(owners, 4, rows)
        second = execute_owner_grouped_any_hit_reference(
            owners, 4, tuple(reversed(rows)))
        self.assertEqual(first.owner_hit_bits, (1, 1, 0, 0))
        self.assertEqual(first.owner_hit_bits, second.owner_hit_bits)
        self.assertEqual(first.output_sha256, second.output_sha256)
        self.assertEqual(first.accepted_event_count, 4)
        self.assertEqual(first.hit_owner_count, 2)
        self.assertEqual(
            first.output_sha256,
            owner_grouped_any_hit_output_sha256(first.owner_hit_bits),
        )

    def test_reference_fails_closed_on_owner_or_primitive_bounds(self):
        with self.assertRaises(OwnerGroupedAnyHitError) as caught:
            execute_owner_grouped_any_hit_reference((0, 2), 2, ((0, 0),))
        self.assertEqual(caught.exception.code, "owner_out_of_bounds")
        with self.assertRaises(OwnerGroupedAnyHitError) as caught:
            execute_owner_grouped_any_hit_reference((0, 1), 2, ((0, 2),))
        self.assertEqual(caught.exception.code, "primitive_out_of_bounds")

    def test_schema_rejects_capacity_and_identity_drift(self):
        callback = compile_curve_owner_grouped_any_hit_callback()
        proof = derive_owner_grouped_any_hit_proof(callback)
        schema = OwnerGroupedAnyHitSchema(
            callback.ir_sha256, callback.effect_digest,
            maximum_owner_count=0)
        with self.assertRaises(OwnerGroupedAnyHitError) as caught:
            verify_owner_grouped_any_hit_schema(callback, schema, proof)
        self.assertEqual(caught.exception.code, "owner_capacity")

    def test_curve_callback_contract_abi_and_artifact_round_trip(self):
        callback = compile_curve_owner_grouped_any_hit_callback()
        proof = derive_owner_grouped_any_hit_proof(callback)
        schema = OwnerGroupedAnyHitSchema(
            callback.ir_sha256, callback.effect_digest)
        contract = verify_owner_grouped_any_hit_schema(
            callback, schema, proof)
        abi = compile_owner_grouped_any_hit_abi(contract)
        self.assertIs(verify_owner_grouped_any_hit_abi(abi, contract), abi)
        self.assertEqual(
            tuple(item.role.value for item in abi.roles),
            ("make_ray", "any_hit", "miss", "finalize"),
        )
        self.assertEqual(abi.any_hit_delivery_contract, "idempotent_monotone")
        with self.assertRaises(OwnerGroupedAnyHitError) as caught:
            verify_owner_grouped_any_hit_abi(
                dataclasses.replace(abi, abi_sha256="f" * 64), contract)
        self.assertEqual(caught.exception.code, "abi_recompile_mismatch")

    def test_curve_physical_authority_binds_behavior_and_target(self):
        target = CurveTargetProfile(
            "optix", "9.0.0", "8.9", "a" * 64)
        authority, proof = build_curve_owner_grouped_any_hit_authority(target)
        self.assertEqual(authority.behavior.proof, proof)
        self.assertEqual(
            authority.canonical_plan.template_id,
            "builtin_round_linear_curve_owner_grouped_any_hit_bool_or_v1",
        )
        hostile = BuiltinCurveOwnerGroupedAnyHitPhysicalSchema(
            authority.callback.ir_sha256,
            authority.callback.effect_digest,
            "b" * 64,
        )
        with self.assertRaises(CurveOwnerGroupedAnyHitError) as caught:
            verify_curve_owner_grouped_any_hit_physical_schema(
                authority.behavior, hostile, target=target)
        self.assertEqual(caught.exception.code, "authority_binding")

    def test_every_behavior_schema_field_is_closed_or_identity_bearing(self):
        target = CurveTargetProfile(
            "optix", "9.0.0", "8.9", "a" * 64)
        authority, proof = build_curve_owner_grouped_any_hit_authority(target)
        callback = authority.callback
        schema = authority.behavior.schema
        mutations = {
            "callback_ir_sha256": "b" * 64,
            "callback_effect_digest": "c" * 64,
            "owner_semantic_id": "primitive.other_owner",
            "owner_field_id": "other_owner_ids",
            "output_field_id": "other_bits",
            "owner_domain": "primitive",
            "reduction": "bool_or",
            "maximum_owner_count": 0,
            "schema_id": schema.schema_id + ".hostile",
            "schema_version": "v2",
        }
        self.assertEqual(set(mutations), set(schema.__dataclass_fields__))
        for field, value in mutations.items():
            hostile = dataclasses.replace(schema, **{field: value})
            with self.subTest(field=field):
                with self.assertRaises(OwnerGroupedAnyHitError):
                    verify_owner_grouped_any_hit_schema(
                        callback, hostile, proof)

        capacity = dataclasses.replace(
            schema, maximum_owner_count=schema.maximum_owner_count - 1)
        verified = verify_owner_grouped_any_hit_schema(
            callback, capacity, proof)
        self.assertNotEqual(verified.schema.schema_sha256,
                            schema.schema_sha256)
        self.assertNotEqual(verified.authority_sha256,
                            authority.behavior.authority_sha256)

    def test_every_curve_physical_schema_field_is_closed(self):
        target = CurveTargetProfile(
            "optix", "9.0.0", "8.9", "a" * 64)
        authority, _proof = build_curve_owner_grouped_any_hit_authority(target)
        schema = authority.schema
        mutations = {
            "callback_ir_sha256": "b" * 64,
            "callback_effect_digest": "c" * 64,
            "behavior_schema_sha256": "d" * 64,
            "control_point_field_id": "other_points",
            "width_field_id": "other_widths",
            "segment_index_field_id": "other_indices",
            "owner_field_id": "other_owners",
            "query_field_id": "other_queries",
            "owner_output_field_id": "other_bits",
            "query_completion_field_id": "other_completion",
            "status_field_id": "other_status",
            "contract_name": "other_contract",
            "template_id": "other_template",
            "geometry_family": "other_geometry",
            "curve_type": "other_curve",
            "endcap_policy": "other_endcap",
            "width_policy": "other_width_policy",
            "gas_update_policy": "dynamic",
            "graph_depth": 2,
            "sbt_record_count": 2,
            "motion_blur": True,
            "primitive_index_offset": 1,
            "schema_id": schema.schema_id + ".hostile",
            "schema_version": "v2",
        }
        self.assertEqual(set(mutations), set(schema.__dataclass_fields__))
        for field, value in mutations.items():
            hostile = dataclasses.replace(schema, **{field: value})
            with self.subTest(field=field):
                with self.assertRaises(CurveOwnerGroupedAnyHitError):
                    verify_curve_owner_grouped_any_hit_physical_schema(
                        authority.behavior, hostile, target=target)

    def test_generated_wrapper_is_generic_real_any_hit_and_fail_closed(self):
        target = CurveTargetProfile(
            "optix", "9.0.0", "8.9", "a" * 64)
        authority, _proof = build_curve_owner_grouped_any_hit_authority(target)
        abi = compile_owner_grouped_any_hit_abi(authority.behavior)
        wrapper = generate_trusted_optix_curve_owner_grouped_any_hit_wrapper_v1(
            authority, abi)
        source = wrapper.source
        self.assertIn("optixTrace(params.traversable", source)
        self.assertIn("__anyhit__rtdl_v4_curve_owner_grouped", source)
        self.assertIn("atomicOr(params.owner_hit_bits + owner, 1u)", source)
        self.assertIn("owner >= params.owner_count", source)
        self.assertIn("optixIgnoreIntersection()", source)
        self.assertIn("OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT", source)
        for forbidden in ("collision", "trajectory", "robot", "pose", "raydb"):
            self.assertNotIn(forbidden, source.lower())

    def test_all_four_numba_leaves_generate_deterministically(self):
        target = CurveTargetProfile(
            "optix", "9.0.0", "8.9", "a" * 64)
        authority, _proof = build_curve_owner_grouped_any_hit_authority(target)
        abi = compile_owner_grouped_any_hit_abi(authority.behavior)
        roles = (
            CallbackRole.MAKE_RAY,
            CallbackRole.ANY_HIT,
            CallbackRole.MISS,
            CallbackRole.FINALIZE,
        )
        first = tuple(generate_curve_owner_grouped_any_hit_numba_leaf(
            authority, abi, role) for role in roles)
        second = tuple(generate_curve_owner_grouped_any_hit_numba_leaf(
            authority, abi, role) for role in roles)
        self.assertEqual(first, second)
        self.assertEqual(tuple(item.role for item in first), roles)
        self.assertTrue(all(item.callback_abi_sha256 == abi.abi_sha256
                            for item in first))

    def test_public_static_input_allows_many_primitives_per_owner(self):
        static = OwnerGroupedCurveStaticInput(
            ((0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)),
            (0.1, 0.1, 0.2, 0.2),
            (0, 2),
            (3, 3),
            4,
        )
        self.assertEqual(static.owner_ids, (3, 3))
        batch = OwnerGroupedCurveQueryBatch((
            ((0, -1, 0), (0, 2, 0)),
        ))
        self.assertEqual(len(batch.queries), 1)

    def test_public_source_compiles_without_native_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            native = Path(directory) / "librtdl_optix.so"
            native.write_bytes(b"owner-grouped-native-identity")
            target = V4CurveTarget.from_native(
                native, optix_sdk="9.0.0", compute_capability="8.9")
            source = curve_owner_grouped_any_hit_source()
            program = source.compile(target=target)
        self.assertEqual(
            program.target.profile.native_sha256,
            hashlib.sha256(b"owner-grouped-native-identity").hexdigest())
        self.assertIn(
            "__anyhit__rtdl_v4_curve_owner_grouped", program.wrapper.source)

    def test_contract_first_package_surface_exports_public_lifecycle(self):
        import rtdsl
        from rtdsl.v4_curve_owner_grouped_any_hit_public import (
            OwnerGroupedCurveQueryBatch as DirectBatch,
            OwnerGroupedCurveStaticInput as DirectStatic,
            PreparedCurveOwnerGroupedAnyHitProgram as DirectPrepared,
            V4CurveTarget as DirectTarget,
            curve_owner_grouped_any_hit_source as direct_source,
        )

        self.assertIs(rtdsl.OwnerGroupedCurveQueryBatch, DirectBatch)
        self.assertIs(rtdsl.OwnerGroupedCurveStaticInput, DirectStatic)
        self.assertIs(rtdsl.PreparedCurveOwnerGroupedAnyHitProgram,
                      DirectPrepared)
        self.assertIs(rtdsl.V4CurveTarget, DirectTarget)
        self.assertIs(rtdsl.curve_owner_grouped_any_hit_source, direct_source)
        for name in (
            "OwnerGroupedCurveQueryBatch", "OwnerGroupedCurveStaticInput",
            "PreparedCurveOwnerGroupedAnyHitProgram", "V4CurveTarget",
            "curve_owner_grouped_any_hit_source",
        ):
            self.assertIn(name, dir(rtdsl))
            self.assertIn(name, rtdsl.__all__)

    def test_native_descriptor_contract_accepts_exact_initial_state(self):
        descriptor = self._initial_native_descriptor()
        observed = _read_descriptor(self._describe(descriptor), 7)
        self.assertEqual(observed, descriptor)
        target = CurveTargetProfile("optix", "9.0.0", "8.9", "a" * 64)
        _require_native_target_binding(observed, target)

    def test_native_descriptor_rejects_shape_type_and_initial_state_drift(self):
        descriptor = self._initial_native_descriptor()
        mutations = (
            {**descriptor, "unexpected": 0},
            {key: value for key, value in descriptor.items()
             if key != "geometry_flags"},
            {**descriptor, "primitive_count": True},
            {**descriptor, "last_execution_present": 1},
            {**descriptor, "execution_count": 1},
            {**descriptor, "native_build_id": "x" * 64},
            {**descriptor, "device_static_input_fingerprint": "b" * 64},
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                with self.assertRaises(RuntimeError):
                    _read_descriptor(self._describe(mutation), 7)

    def test_native_descriptor_rejects_output_copy_after_status_failure(self):
        descriptor = {
            **self._initial_native_descriptor(),
            "execution_count": 1,
            "last_execution_present": True,
            "last_status_failed": True,
            "last_query_count": 1,
            "last_status_d2h_call_count": 2,
            "last_application_output_d2h_call_count": 2,
            "last_query_fingerprint": "b" * 64,
            "last_status_fingerprint": "c" * 64,
            "last_counter_fingerprint": "d" * 64,
            "last_output_fingerprint": "e" * 64,
        }
        with self.assertRaisesRegex(RuntimeError, "copied output"):
            _read_descriptor(self._describe(descriptor), 7)

    def test_prepare_validation_cleanup_preserves_both_failures(self):
        primary = ValueError("hostile descriptor")

        def cleanup_failure(_token, error, _capacity):
            ctypes.memmove(error, b"native destroy failed\0", 22)
            return 9

        with self.assertRaisesRegex(
                RuntimeError, "hostile descriptor.*native destroy failed") as caught:
            _destroy_failed_prepare(cleanup_failure, 7, primary)
        self.assertIs(caught.exception.__cause__, primary)

        def cleanup_raise(_token, _error, _capacity):
            raise OSError("destroy unavailable")

        with self.assertRaisesRegex(
                RuntimeError, "hostile descriptor.*destroy unavailable") as caught:
            _destroy_failed_prepare(cleanup_raise, 7, primary)
        self.assertIs(caught.exception.__cause__, primary)

    def test_prepared_close_is_idempotent_and_context_preserves_both_failures(self):
        owner = object.__new__(PreparedCurveOwnerGroupedAnyHit)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._active = threading.Lock()
        owner._token = 7
        destroy_calls = []

        def destroy(token, _error, _capacity):
            destroy_calls.append(token)
            return 0

        owner._destroy = destroy
        owner.close()
        owner.close()
        self.assertEqual(destroy_calls, [7])

        owner = object.__new__(PreparedCurveOwnerGroupedAnyHit)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._active = threading.Lock()
        owner._token = 11

        def failing_destroy(_token, error, _capacity):
            ctypes.memmove(error, b"destroy failed\0", 15)
            return 3

        owner._destroy = failing_destroy
        primary = ValueError("body failed")
        with self.assertRaisesRegex(
                RuntimeError, "body failed.*destroy failed") as caught:
            owner.__exit__(ValueError, primary, None)
        self.assertIs(caught.exception.__cause__, primary)
        self.assertFalse(owner._closed)

    def test_native_descriptor_rejects_fact_and_target_mutation(self):
        descriptor = self._initial_native_descriptor()
        target = CurveTargetProfile("optix", "9.0.0", "8.9", "a" * 64)
        with self.assertRaisesRegex(RuntimeError, "target"):
            _require_native_target_binding(
                {**descriptor, "cuda_compute_capability_minor": 6}, target)
        after = {**descriptor, "execution_count": 1}
        _require_descriptor_transition(descriptor, after)
        with self.assertRaisesRegex(RuntimeError, "static descriptor"):
            _require_descriptor_transition(
                descriptor, {**after, "geometry_flags": 0})

    def test_native_execution_fingerprints_bind_every_output_class(self):
        normalized = ((0.0, 0.0, 0.0, 1.0, 0.0, 0.0),)
        statuses = ({
            "first_error_claimed": 0,
            "error_code": 0,
            "stage": 0,
            "role": 0,
            "launch_index": 0,
            "error_site": 0,
            "effect_tag": 0,
            "nonce_word": 0,
            "invocation_mask": 98,
        },)
        counters = (0, 1, 0, 2, 0, 1, 1)
        fingerprints = (
            _native_query_fingerprint(normalized),
            _native_status_fingerprint(statuses),
            _native_counter_fingerprint(counters),
            _native_output_fingerprint((1, 0), (0,)),
        )
        self.assertEqual(len(set(fingerprints)), 4)
        self.assertTrue(all(len(value) == 64 for value in fingerprints))
        self.assertNotEqual(
            _native_output_fingerprint((1, 0), (0,)),
            _native_output_fingerprint((0, 1), (0,)),
        )


if __name__ == "__main__":
    unittest.main()
