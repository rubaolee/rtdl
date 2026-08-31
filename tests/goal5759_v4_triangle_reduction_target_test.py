from __future__ import annotations

import dataclasses
from pathlib import Path
import unittest

from rtdsl.v4_callback_abi import AnyHitProofAuthority
from rtdsl.v4_callback_frontend import parse_callback_source
from rtdsl.v4_callback_ir import (
    AnyHitDeliveryContract,
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    CallbackRole,
)
from rtdsl.v4_triangle_reduction import (
    compile_triangle_reduction_abi,
    compile_triangle_reduction_contract,
    verify_triangle_reduction_schema,
)
from rtdsl.v4_triangle_reduction_optix_compiler import (
    generate_triangle_reduction_numba_leaf,
)
from rtdsl.v4_triangle_reduction_optix_wrapper_codegen import (
    generate_trusted_optix_triangle_reduction_wrapper_v1,
)
from rtdsl.v4_typed_physical_schema import (
    GeometryFamily,
    ReferenceTargetProfile,
    verify_callback_program_for_geometry,
)
from scripts.goal5758_m1_consumer_fixtures import (
    COUNT_SOURCE, all_hit_schema,
    compile_count_callback,
    compile_keyed_callback,
    keyed_schema,
    weighted_schema,
)


ROOT = Path(__file__).resolve().parents[1]


def _target():
    return ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256="a" * 64,
        supports_custom_aabb=True, supports_builtin_triangle=True,
    )


def _proof(callback):
    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256="b" * 64,
        proof_kind="external_machine_checked_order_independence_v1",
    )


def _compiled(callback, schema):
    authority = verify_triangle_reduction_schema(callback, schema, target=_target())
    proof = _proof(callback)
    abi = compile_triangle_reduction_abi(
        authority, any_hit_proof_authority=proof)
    contract = compile_triangle_reduction_contract(
        authority, abi_sha256=abi.abi_sha256)
    return authority, proof, abi, contract


class Goal5759TriangleReductionTargetTests(unittest.TestCase):
    def test_count_intrinsic_requires_the_exact_standard_callback_ir(self):
        callback = compile_count_callback()
        authority, proof, abi, contract = _compiled(
            callback, all_hit_schema(callback))
        standard = generate_trusted_optix_triangle_reduction_wrapper_v1(
            authority, contract, abi, any_hit_proof_authority=proof)
        self.assertTrue(standard.linked_role_symbols)
        self.assertIn(
            "__raygen__rtdl_v4_triangle_reduction_diagnostic",
            standard.source,
        )
        self.assertIn(
            "query >= params.query_count || params.fast_control == nullptr",
            standard.source,
        )

        # Mutate one decision-bearing leaf while preserving the same public
        # callback shape.  The replacement is still valid Callback IR, but it
        # must use the generic lowering rather than the count intrinsic.
        mutated_source = COUNT_SOURCE.replace(
            "payload.count + 1", "payload.count + 2", 1)
        self.assertNotEqual(mutated_source, COUNT_SOURCE)
        mutated_program = parse_callback_source(
            mutated_source,
            callback.program.manifest,
            schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
        )
        mutated = verify_callback_program_for_geometry(
            mutated_program, GeometryFamily.BUILTIN_TRIANGLE)
        self.assertNotEqual(callback.ir_sha256, mutated.ir_sha256)
        mutated_authority, mutated_proof, mutated_abi, mutated_contract = \
            _compiled(mutated, all_hit_schema(mutated))
        generic = generate_trusted_optix_triangle_reduction_wrapper_v1(
            mutated_authority, mutated_contract, mutated_abi,
            any_hit_proof_authority=mutated_proof)
        self.assertTrue(generic.linked_role_symbols)
        for _, symbol in generic.role_symbols:
            self.assertIn(symbol, generic.source)
        self.assertIn("v4_commit_leaf_status", generic.source)
        self.assertNotIn(
            "__raygen__rtdl_v4_triangle_reduction_diagnostic",
            generic.source,
        )
        self.assertNotIn(
            "query >= params.query_count || params.fast_control == nullptr",
            generic.source,
        )

    def test_all_three_m1_contracts_generate_deterministically(self):
        callback = compile_count_callback()
        for schema in (all_hit_schema(callback), weighted_schema(callback)):
            authority, proof, abi, contract = _compiled(callback, schema)
            first = generate_trusted_optix_triangle_reduction_wrapper_v1(
                authority, contract, abi, any_hit_proof_authority=proof)
            second = generate_trusted_optix_triangle_reduction_wrapper_v1(
                authority, contract, abi, any_hit_proof_authority=proof)
            self.assertEqual(first, second)
        callback = compile_keyed_callback()
        authority, proof, abi, contract = _compiled(callback, keyed_schema(callback))
        self.assertEqual(
            generate_trusted_optix_triangle_reduction_wrapper_v1(
                authority, contract, abi, any_hit_proof_authority=proof),
            generate_trusted_optix_triangle_reduction_wrapper_v1(
                authority, contract, abi, any_hit_proof_authority=proof),
        )

    def test_integer_add_lowering_guards_before_device_add(self):
        callback = compile_count_callback()
        authority, proof, abi, _ = _compiled(callback, all_hit_schema(callback))
        leaf = generate_triangle_reduction_numba_leaf(
            authority, abi, CallbackRole.ANY_HIT,
            any_hit_proof_authority=proof)
        source = leaf.generated_source
        guard = source.index("if 1 > 18446744073709551615 - in_payload_count:")
        addition = source.index("_rtdl_checked_add_1 = in_payload_count + 1")
        self.assertLess(guard, addition)
        self.assertIn("status_error_code[0] = 4", source[guard:addition])
        self.assertNotIn("integer_numeric_codegen_pending", source)

    def test_wrapper_is_builtin_triangle_true_optix_and_app_neutral(self):
        callback = compile_keyed_callback()
        authority, proof, abi, contract = _compiled(callback, keyed_schema(callback))
        source = generate_trusted_optix_triangle_reduction_wrapper_v1(
            authority, contract, abi, any_hit_proof_authority=proof).source
        self.assertIn("optixTrace", source)
        self.assertIn("optixGetTriangleBarycentrics", source)
        self.assertIn("optixIgnoreIntersection", source)
        self.assertIn("__anyhit__rtdl_v4_triangle_reduction", source)
        for forbidden in ("raydb", "triangle_counting", "rt-1a2", "rt-2a1"):
            self.assertNotIn(forbidden, source.lower())

    def test_wrapper_binds_event_channels_and_race_safe_capacity(self):
        callback = compile_keyed_callback()
        authority, proof, abi, contract = _compiled(callback, keyed_schema(callback))
        source = generate_trusted_optix_triangle_reduction_wrapper_v1(
            authority, contract, abi, any_hit_proof_authority=proof).source
        self.assertIn("atomicAdd(params.event_count", source)
        self.assertIn("slot >= params.event_capacity", source)
        self.assertIn("params.event_stable_id[slot]", source)
        self.assertIn("params.event_signed_value[slot]", source)
        self.assertIn("params.event_include[slot]", source)

    def test_proof_and_contract_drift_fail_closed(self):
        callback = compile_count_callback()
        authority, proof, abi, contract = _compiled(callback, all_hit_schema(callback))
        forged_proof = dataclasses.replace(proof, proof_sha256="c" * 64)
        with self.assertRaisesRegex(Exception, "abi_binding"):
            generate_trusted_optix_triangle_reduction_wrapper_v1(
                authority, contract, abi,
                any_hit_proof_authority=forged_proof)
        forged_contract = dataclasses.replace(contract, abi_sha256="d" * 64)
        with self.assertRaisesRegex(Exception, "contract_binding"):
            generate_trusted_optix_triangle_reduction_wrapper_v1(
                authority, forged_contract, abi,
                any_hit_proof_authority=proof)

    def test_native_c_abi_exports_one_generic_triangle_reduction_symbol(self):
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text()
        implementation = (
            ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text()
        symbol = "rtdl_optix_v4_run_builtin_triangle_reduction_callback_v1"
        self.assertEqual(api.count(symbol), 1)
        self.assertIn("run_v4_builtin_triangle_reduction_callback", api)
        # The current native contract requires one any-hit callback delivery
        # per logical primitive.  Goal5776 made this explicit for both the
        # host-column and partner device-column GAS builders; the older NONE
        # assertion predated that correctness repair.
        self.assertGreaterEqual(
            implementation.count("OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL"),
            2,
        )
        for forbidden in ("raydb", "triangle_counting", "rt-1a2", "rt-2a1"):
            self.assertNotIn(forbidden, implementation.lower())


if __name__ == "__main__":
    unittest.main()
