from __future__ import annotations

import dataclasses
import unittest

from rtdsl.v4_callback_abi import AnyHitProofAuthority, compile_callback_abi
from rtdsl.v4_callback_frontend import compile_callback_source
from rtdsl.v4_callback_ir import CallbackRole, GeometryContract, GeometryAdmission
from rtdsl.v4_callback_optix_wrapper_codegen import (
    CallbackWrapperCodegenError,
    generate_trusted_optix_wrapper_v1,
)
from tests.goal5750_v4_callback_ir_test import SOURCE, manifest


FORMAL_SOURCE = SOURCE.replace(
    '''    @optix.closest_hit
    def closest_hit(hit: Hit, payload: SearchPayload) -> SearchPayload:
        updated = SearchPayload(best_t=hit.t, best_id=hit.hit_kind)
        return optix.payload(payload=updated)
''',
    '''    @optix.closest_hit
    def closest_hit(hit: Hit, payload: SearchPayload) -> SearchPayload:
        return optix.payload(payload=payload)
''',
)
assert FORMAL_SOURCE != SOURCE


class Goal5751OptixWrapperCodegenTest(unittest.TestCase):
    def setUp(self):
        self.program = compile_callback_source(FORMAL_SOURCE, manifest())
        delivery = self.program.program.manifest.any_hit_delivery
        assert delivery is not None
        self.proof = AnyHitProofAuthority(
            self.program.ir_sha256,
            self.program.effect_digest,
            delivery,
            "a" * 64,
            "external_machine_checked_order_independence_v1",
        )
        self.abi = compile_callback_abi(
            self.program, any_hit_proof_authority=self.proof
        )

    def test_all_seven_roles_drive_one_deterministic_trusted_wrapper(self):
        first = generate_trusted_optix_wrapper_v1(
            self.program, self.abi, any_hit_proof_authority=self.proof
        )
        second = generate_trusted_optix_wrapper_v1(
            self.program, self.abi, any_hit_proof_authority=self.proof
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first.role_symbols), 7)
        for role, symbol in first.role_symbols:
            self.assertIn(symbol, first.source)
            self.assertIn(role, {item.value for item in CallbackRole})
        for entry in ("raygen", "intersection", "anyhit", "closesthit", "miss"):
            self.assertIn(f"__{entry}__rtdl_v4_formal", first.source)

    def test_wrapper_owns_atomic_status_and_never_exposes_user_dispatch(self):
        wrapper = generate_trusted_optix_wrapper_v1(
            self.program, self.abi, any_hit_proof_authority=self.proof
        ).source
        self.assertIn("atomicCAS(&record->first_error_claimed", wrapper)
        self.assertIn("atomicOr(&params.status[query].invocation_mask", wrapper)
        self.assertIn("optixTrace(", wrapper)
        self.assertIn("optixReportIntersection(", wrapper)
        self.assertNotIn("SearchProgram", wrapper)
        self.assertNotIn("Arkade", wrapper)
        self.assertNotIn("RayJoin", wrapper)
        self.assertNotIn("user_callback", wrapper)
        self.assertNotIn("candidate_override", wrapper)

    def test_wrapper_call_order_is_the_exact_canonical_abi_order(self):
        wrapper = generate_trusted_optix_wrapper_v1(
            self.program, self.abi, any_hit_proof_authority=self.proof
        ).source
        # Canonical RoleAbi.parameter_order sorts the union of effect fields.
        # In particular, make-ray direction precedes origin.  The first real
        # device execution caught that the old wrapper iterated effect variants
        # instead, so this is a load-bearing ABI regression assertion.
        call = next(
            line for line in wrapper.splitlines()
            if line.strip().startswith("(void)rtdl_v4_make_ray_")
        )
        self.assertLess(
            call.index("&mr_out_trace_request_direction_x"),
            call.index("&mr_out_trace_request_origin_x"),
        )
        self.assertLess(
            call.index("&mr_out_trace_request_payload_best_id"),
            call.index("&mr_out_trace_request_payload_best_t"),
        )

    def test_stale_abi_or_any_hit_proof_fails_closed(self):
        with self.assertRaises(CallbackWrapperCodegenError):
            generate_trusted_optix_wrapper_v1(
                self.program,
                dataclasses.replace(self.abi, abi_sha256="0" * 64),
                any_hit_proof_authority=self.proof,
            )
        with self.assertRaises(CallbackWrapperCodegenError):
            generate_trusted_optix_wrapper_v1(
                self.program,
                self.abi,
                any_hit_proof_authority=dataclasses.replace(
                    self.proof, proof_sha256="b" * 64
                ),
            )

    def test_unknown_geometry_template_fails_closed(self):
        changed = compile_callback_source(
            FORMAL_SOURCE,
            manifest(geometry=GeometryContract(
                GeometryAdmission.TESTED_USER_GEOMETRY,
                "unknown_geometry",
                False,
            )),
        )
        delivery = changed.program.manifest.any_hit_delivery
        assert delivery is not None
        proof = dataclasses.replace(
            self.proof,
            callback_ir_sha256=changed.ir_sha256,
            effect_digest=changed.effect_digest,
        )
        abi = compile_callback_abi(changed, any_hit_proof_authority=proof)
        with self.assertRaises(CallbackWrapperCodegenError) as caught:
            generate_trusted_optix_wrapper_v1(
                changed, abi, any_hit_proof_authority=proof
            )
        self.assertEqual(caught.exception.code, "physical_template")

    def test_closest_hit_cannot_overwrite_order_independent_any_hit_payload(self):
        unsafe = compile_callback_source(SOURCE, manifest())
        delivery = unsafe.program.manifest.any_hit_delivery
        assert delivery is not None
        proof = AnyHitProofAuthority(
            unsafe.ir_sha256, unsafe.effect_digest, delivery,
            "a" * 64, "external_machine_checked_order_independence_v1",
        )
        abi = compile_callback_abi(unsafe, any_hit_proof_authority=proof)
        with self.assertRaises(CallbackWrapperCodegenError) as caught:
            generate_trusted_optix_wrapper_v1(
                unsafe, abi, any_hit_proof_authority=proof
            )
        self.assertEqual(caught.exception.code, "closest_hit_confluence")


if __name__ == "__main__":
    unittest.main()
