from __future__ import annotations

import dataclasses
import copy
import hashlib
import json
import unittest

from rtdsl.v4_callback_abi import (
    AnyHitProofAuthority,
    CallbackAbiError,
    callback_abi_from_dict,
    compile_callback_abi,
    derive_compiler_recognized_any_hit_proof,
    verify_compiled_callback_abi,
)
from rtdsl.v4_callback_frontend import compile_callback_source, parse_callback_source
from rtdsl.v4_callback_ir import (
    CallbackRole,
    GeometryAdmission,
    GeometryContract,
    GeometryProofAuthority,
    VerifiedCallbackProgram,
    verify_callback_program,
)
from tests.goal5750_v4_callback_ir_test import SOURCE, manifest


def authority(program: VerifiedCallbackProgram) -> AnyHitProofAuthority:
    contract = program.program.manifest.any_hit_delivery
    assert contract is not None
    return AnyHitProofAuthority(
        callback_ir_sha256=program.ir_sha256,
        effect_digest=program.effect_digest,
        delivery_contract=contract,
        proof_sha256="a" * 64,
        proof_kind="external_machine_checked_order_independence_v1",
    )


class Goal5751CallbackAbiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.program = compile_callback_source(SOURCE, manifest())

    def test_complete_seven_role_abi_is_deterministic(self):
        first = compile_callback_abi(
            self.program, any_hit_proof_authority=authority(self.program)
        )
        second = compile_callback_abi(
            self.program, any_hit_proof_authority=authority(self.program)
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first.roles), 7)
        self.assertEqual({item.role for item in first.roles}, set(CallbackRole))
        payload = first.to_dict()
        self.assertEqual(
            json.loads(json.dumps(payload, sort_keys=True)), payload
        )
        self.assertEqual(len(first.abi_sha256), 64)
        self.assertEqual(callback_abi_from_dict(first.to_dict()), first)
        self.assertEqual(
            verify_compiled_callback_abi(
                first.to_dict(),
                self.program,
                any_hit_proof_authority=authority(self.program),
            ),
            first,
        )

    def test_self_consistent_hostile_layout_cannot_override_ir_recompilation(self):
        compiled = compile_callback_abi(
            self.program, any_hit_proof_authority=authority(self.program)
        )
        hostile = copy.deepcopy(compiled.to_dict())
        hostile["roles"][0]["inputs"][0]["scalar"] = "f64"
        payload = dict(hostile)
        payload.pop("abi_sha256")
        hostile["abi_sha256"] = hashlib.sha256(
            json.dumps(
                payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
        ).hexdigest()
        # Structurally valid and self-consistent, but not authoritative for the
        # exact Callback IR it names.
        callback_abi_from_dict(hostile)
        with self.assertRaises(CallbackAbiError) as caught:
            verify_compiled_callback_abi(
                hostile,
                self.program,
                any_hit_proof_authority=authority(self.program),
            )
        self.assertEqual(caught.exception.code, "artifact_ir_recompile_mismatch")

    def test_serialized_abi_mutations_fail_closed_even_with_recomputed_json(self):
        compiled = compile_callback_abi(
            self.program, any_hit_proof_authority=authority(self.program)
        )
        attacks = []
        bad_nonce = copy.deepcopy(compiled.to_dict())
        bad_nonce["roles"][0]["nonce_word"] ^= 1
        attacks.append(bad_nonce)
        bad_status = copy.deepcopy(compiled.to_dict())
        bad_status["roles"][0]["status"][0]["path"] = "status.claimed_success"
        attacks.append(bad_status)
        bad_order = copy.deepcopy(compiled.to_dict())
        bad_order["roles"][0]["parameter_order"].reverse()
        attacks.append(bad_order)
        bad_kind = copy.deepcopy(compiled.to_dict())
        bad_kind["any_hit_proof_kind"] = "unreviewed_claim"
        attacks.append(bad_kind)
        bad_digest = copy.deepcopy(compiled.to_dict())
        bad_digest["abi_sha256"] = "0" * 64
        attacks.append(bad_digest)
        for item in attacks:
            with self.subTest(item=item):
                with self.assertRaises(CallbackAbiError):
                    callback_abi_from_dict(item)

    def test_input_records_vectors_views_and_builtins_have_explicit_layouts(self):
        compiled = compile_callback_abi(
            self.program, any_hit_proof_authority=authority(self.program)
        )
        roles = {item.role: item for item in compiled.roles}
        bounds_paths = {item.path for item in roles[CallbackRole.BOUNDS].inputs}
        self.assertIn("in.primitive.center.x", bounds_paths)
        self.assertIn("in.primitive.radius", bounds_paths)
        ray_paths = {item.path for item in roles[CallbackRole.INTERSECTION].inputs}
        self.assertIn("in.ray.origin.x", ray_paths)
        self.assertIn("in.ray.tmax", ray_paths)
        make_ray = {item.path: item for item in roles[CallbackRole.MAKE_RAY].inputs}
        self.assertEqual(
            make_ray["in.queries.columns.origin.x"].scalar, "device_ptr<f32>"
        )
        self.assertTrue(make_ray["in.queries.columns.origin.x"].readonly)
        self.assertEqual(
            make_ray["in.queries.columns.tmax"].scalar, "device_ptr<f32>"
        )
        self.assertEqual(make_ray["in.queries.length"].scalar, "u64")

    def test_every_role_has_race_safe_per_launch_status_and_tagged_effects(self):
        compiled = compile_callback_abi(
            self.program, any_hit_proof_authority=authority(self.program)
        )
        for role in compiled.roles:
            status_paths = {item.path for item in role.status}
            self.assertIn("status.launch_index", status_paths)
            self.assertIn("status.first_error_claimed", status_paths)
            self.assertIn("atomic_compare_exchange", role.first_error_policy)
            self.assertTrue(role.effects)
            self.assertEqual(len({item.tag for item in role.effects}), len(role.effects))
            self.assertEqual(len(role.parameter_order), len(set(role.parameter_order)))
            self.assertEqual(role.parameter_order[0], role.inputs[0].path)
        intersection = next(item for item in compiled.roles if item.role is CallbackRole.INTERSECTION)
        self.assertEqual({item.kind.value for item in intersection.effects}, {"hit", "no_hit"})

    def test_any_hit_manifest_declaration_is_not_a_codegen_proof(self):
        with self.assertRaises(CallbackAbiError) as caught:
            compile_callback_abi(self.program)
        self.assertEqual(caught.exception.code, "any_hit_proof_required")

    def test_compiler_recognized_minimum_proof_is_rederived_not_trusted(self):
        proof = derive_compiler_recognized_any_hit_proof(self.program)
        self.assertEqual(
            proof.proof_kind,
            "compiler_recognized_commutative_idempotent_reduction_v1",
        )
        compiled = compile_callback_abi(
            self.program, any_hit_proof_authority=proof)
        self.assertEqual(compiled.any_hit_proof_sha256, proof.proof_sha256)
        with self.assertRaises(CallbackAbiError) as forged:
            compile_callback_abi(
                self.program,
                any_hit_proof_authority=dataclasses.replace(
                    proof, proof_sha256="f" * 64),
            )
        self.assertEqual(forged.exception.code, "any_hit_compiler_proof_mismatch")
        reversed_tie = compile_callback_source(
            SOURCE.replace("hit.hit_kind < payload.best_id", "hit.hit_kind > payload.best_id"),
            manifest(),
        )
        with self.assertRaises(CallbackAbiError) as unrecognized:
            derive_compiler_recognized_any_hit_proof(reversed_tie)
        self.assertEqual(unrecognized.exception.code, "any_hit_compiler_proof_shape")

    def test_stale_forged_or_malformed_any_hit_proof_fails_closed(self):
        attacks = (
            dataclasses.replace(authority(self.program), callback_ir_sha256="0" * 64),
            dataclasses.replace(authority(self.program), effect_digest="1" * 64),
            dataclasses.replace(authority(self.program), proof_sha256="bad"),
            dataclasses.replace(authority(self.program), proof_kind="unreviewed_claim"),
        )
        for item in attacks:
            with self.subTest(item=item):
                with self.assertRaises(CallbackAbiError):
                    compile_callback_abi(self.program, any_hit_proof_authority=item)

    def test_forged_verified_dataclass_is_reverified(self):
        forged = dataclasses.replace(self.program, effect_digest="0" * 64)
        with self.assertRaises(CallbackAbiError) as caught:
            compile_callback_abi(forged, any_hit_proof_authority=authority(self.program))
        self.assertEqual(caught.exception.code, "verified_identity_mismatch")

    def test_verified_geometry_authority_is_required_again_at_abi_boundary(self):
        parsed = parse_callback_source(SOURCE, manifest())
        proof = "b" * 64
        geometry = GeometryContract(
            GeometryAdmission.VERIFIED_CONTRACT,
            "analytic_sphere_f32_outward_v1",
            True,
            proof,
        )
        geometry_authority = GeometryProofAuthority(
            contract_name=geometry.contract_name,
            callback_source_sha256=parsed.source_sha256,
            proof_sha256=proof,
            target_f32_outward_rounding=True,
        )
        verified = compile_callback_source(
            SOURCE,
            manifest(geometry=geometry),
            geometry_proof_authorities={geometry.contract_name: geometry_authority},
        )
        with self.assertRaises(CallbackAbiError) as missing:
            compile_callback_abi(
                verified,
                any_hit_proof_authority=authority(verified),
            )
        self.assertEqual(missing.exception.code, "callback_ir_reverification")
        compiled = compile_callback_abi(
            verified,
            any_hit_proof_authority=authority(verified),
            geometry_proof_authorities={geometry.contract_name: geometry_authority},
        )
        self.assertEqual(compiled.callback_ir_sha256, verified.ir_sha256)

    def test_proof_is_rejected_when_any_hit_role_is_absent(self):
        spec = dataclasses.replace(
            self.program.program,
            manifest=dataclasses.replace(self.program.program.manifest, any_hit_delivery=None),
            functions=tuple(
                item for item in self.program.program.functions if item.role is not CallbackRole.ANY_HIT
            ),
        )
        verified = verify_callback_program(spec)
        with self.assertRaises(CallbackAbiError) as caught:
            compile_callback_abi(verified, any_hit_proof_authority=authority(self.program))
        self.assertEqual(caught.exception.code, "unused_any_hit_proof")


if __name__ == "__main__":
    unittest.main()
