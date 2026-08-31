from __future__ import annotations

import dataclasses
import json
import math
import unittest

from rtdsl.v4_callback_frontend import compile_callback_source, parse_callback_source
from rtdsl.v4_callback_interpreter import CallbackRuntimeError, RuntimeRecord, execute_callback_role
from rtdsl.v4_callback_ir import (
    F32, U32, AnyHitDeliveryContract, CallbackField, CallbackModuleManifest,
    CallbackRecord, CallbackRole, CallbackVerificationError, FrozenConstant,
    GeometryAdmission, GeometryContract, LinkageMechanism, NumericContract,
    GeometryProofAuthority, RecordPurpose, ResourceBudget, RuntimeStatus,
    callback_program_from_dict, record_type, verify_callback_program,
)


SOURCE = r'''
@optix.payload
class SearchPayload:
    best_t: f32
    best_id: u32

@optix.record
class Primitive:
    center: vec3f32
    radius: f32
    item_id: u32

@optix.record
class Query:
    origin: vec3f32
    tmax: f32

@optix.output
class SearchOutput:
    item_id: u32
    distance: f32

@optix.helper
def stable_distance(value: f32) -> f32:
    result = value
    for index in range(LOOP_BOUND):
        result += ZERO_INCREMENT
    return result

@optix.program(
    payload=SearchPayload,
    output=SearchOutput,
    attributes=(u32,),
    max_trace_depth=1,
    max_callable_depth=0,
)
class SearchProgram:
    @optix.bounds
    def bounds(primitive: Primitive) -> Aabb3f:
        extent = vec3f32(primitive.radius, primitive.radius, primitive.radius)
        return optix.aabb(
            lower=primitive.center - extent,
            upper=primitive.center + extent,
        )

    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[Query]) -> TraceRequest:
        query = queries[launch_id]
        initial = SearchPayload(best_t=query.tmax, best_id=U32_MAX)
        return optix.trace_request(
            origin=query.origin,
            direction=vec3f32(1.0, 0.0, 0.0),
            tmin=0.0,
            tmax=query.tmax,
            payload=initial,
        )

    @optix.intersection
    def intersection(ray: Ray3f, primitive: Primitive) -> IntersectionEffect:
        offset = ray.origin - primitive.center
        b = optix.dot(offset, ray.direction)
        c = optix.dot(offset, offset) - primitive.radius * primitive.radius
        discriminant = b * b - c
        if discriminant >= 0.0:
            root = optix.sqrt(discriminant)
            near_t = -b - root
            far_t = -b + root
            selected_t = near_t if near_t >= ray.tmin else far_t
            if selected_t >= ray.tmin and selected_t <= ray.tmax:
                return optix.hit(t=selected_t, hit_kind=primitive.item_id, attributes=(primitive.item_id,))
            else:
                return optix.no_hit()
        else:
            return optix.no_hit()

    @optix.any_hit
    def any_hit(hit: Hit, payload: SearchPayload) -> AnyHitEffect:
        if hit.t < payload.best_t or (hit.t == payload.best_t and hit.hit_kind < payload.best_id):
            updated = SearchPayload(best_t=hit.t, best_id=hit.hit_kind)
            return optix.accept_continue(payload=updated)
        else:
            return optix.accept_continue(payload=payload)

    @optix.closest_hit
    def closest_hit(hit: Hit, payload: SearchPayload) -> SearchPayload:
        updated = SearchPayload(best_t=hit.t, best_id=hit.hit_kind)
        return optix.payload(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: SearchPayload) -> SearchPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: SearchPayload) -> SearchOutput:
        distance = stable_distance(payload.best_t)
        value = SearchOutput(item_id=payload.best_id, distance=distance)
        return optix.output(value=value)
'''


def manifest(**changes) -> CallbackModuleManifest:
    base = CallbackModuleManifest(
        name="search_program",
        payload_record="SearchPayload",
        output_record="SearchOutput",
        attribute_types=(U32,),
        constants=(
            FrozenConstant("LOOP_BOUND", U32, 2),
            FrozenConstant("U32_MAX", U32, 0xFFFFFFFF),
            FrozenConstant("ZERO_INCREMENT", F32, 0.0),
        ),
        numeric=NumericContract(),
        resources=ResourceBudget(),
        geometry=GeometryContract(
            GeometryAdmission.TESTED_USER_GEOMETRY,
            "tested_analytic_sphere_v1",
            False,
        ),
        any_hit_delivery=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason="Goal5749 Home and modern-RTX functional evidence",
    )
    return dataclasses.replace(base, **changes)


class Goal5750CallbackIrTest(unittest.TestCase):
    def test_source_compiles_to_stable_backend_neutral_ir(self):
        first = compile_callback_source(SOURCE, manifest())
        second = compile_callback_source("\n" + SOURCE, manifest())
        self.assertEqual(first.ir_sha256, second.ir_sha256)
        self.assertEqual(first.program.source_sha256, second.program.source_sha256)
        self.assertEqual(first.payload_u32_slots, 2)
        self.assertEqual(first.attribute_u32_slots, 1)
        self.assertEqual(first.total_static_iterations, 2)
        self.assertEqual(first.helper_call_depth, 1)
        self.assertEqual(
            {item.role for item in first.program.functions if item.role is not None},
            set(CallbackRole),
        )

    def test_all_roles_execute_with_exact_deterministic_semantics(self):
        program = compile_callback_source(SOURCE, manifest())
        bounds = execute_callback_role(program, CallbackRole.BOUNDS, {
            "primitive": {"center": (5.0, 0.0, 0.0), "radius": 1.0, "item_id": 3},
        })
        self.assertEqual(bounds.effect.field("lower"), (4.0, -1.0, -1.0))
        self.assertEqual(bounds.effect.field("upper"), (6.0, 1.0, 1.0))

        make_ray = execute_callback_role(program, CallbackRole.MAKE_RAY, {
            "launch_id": 0,
            "queries": ({"origin": (0.0, 0.0, 0.0), "tmax": 100.0},),
        })
        self.assertEqual(make_ray.effect.field("origin"), (0.0, 0.0, 0.0))
        self.assertEqual(make_ray.effect.field("direction"), (1.0, 0.0, 0.0))

        intersection = execute_callback_role(program, CallbackRole.INTERSECTION, {
            "ray": {"origin": (0.0, 0.0, 0.0), "direction": (1.0, 0.0, 0.0), "tmin": 0.0, "tmax": 100.0},
            "primitive": {"center": (5.0, 0.0, 0.0), "radius": 1.0, "item_id": 3},
        })
        self.assertEqual(intersection.effect.field("t"), 4.0)
        self.assertEqual(intersection.effect.field("attributes"), (3,))

        payload = {"best_t": 100.0, "best_id": 0xFFFFFFFF}
        any_hit = execute_callback_role(program, CallbackRole.ANY_HIT, {
            "hit": {"t": 4.0, "hit_kind": 3}, "payload": payload,
        })
        updated = any_hit.effect.field("payload")
        self.assertIsInstance(updated, RuntimeRecord)
        self.assertEqual(updated.field("best_id"), 3)
        closest = execute_callback_role(program, CallbackRole.CLOSEST_HIT, {
            "hit": {"t": 4.0, "hit_kind": 3}, "payload": payload,
        })
        self.assertEqual(closest.effect.field("payload").field("best_t"), 4.0)
        missed = execute_callback_role(program, CallbackRole.MISS, {
            "ray": {"origin": (0.0, 0.0, 0.0), "direction": (1.0, 0.0, 0.0), "tmin": 0.0, "tmax": 100.0},
            "payload": payload,
        })
        self.assertEqual(missed.effect.field("payload").field("best_id"), 0xFFFFFFFF)
        final = execute_callback_role(program, CallbackRole.FINALIZE, {"payload": payload})
        self.assertEqual(final.effect.field("value").field("distance"), 100.0)
        self.assertEqual(final.executed_static_iterations, 2)
        self.assertEqual(final.helper_invocation_count, 1)
        self.assertEqual(
            final.semantic_sha256,
            execute_callback_role(program, CallbackRole.FINALIZE, {"payload": payload}).semantic_sha256,
        )

    def test_source_is_never_executed_and_dynamic_python_fails_closed(self):
        for bad in (
            "import os\n" + SOURCE,
            "open('bad','w')\n" + SOURCE,
            SOURCE.replace("optix.sqrt(discriminant)", "evil(discriminant)"),
            SOURCE.replace("for index in range(LOOP_BOUND):", "while True:"),
            SOURCE.replace("result += ZERO_INCREMENT", "result = globals()"),
        ):
            with self.assertRaises(CallbackVerificationError):
                compile_callback_source(bad, manifest())

    def test_python_escape_and_allocation_attack_matrix_fails_closed(self):
        attacks = {
            "lambda": SOURCE.replace(
                "distance = stable_distance(payload.best_t)",
                "distance = (lambda value: value)(payload.best_t)",
            ),
            "list_allocation": SOURCE.replace(
                "distance = stable_distance(payload.best_t)",
                "distance = [payload.best_t][0]",
            ),
            "comprehension": SOURCE.replace(
                "distance = stable_distance(payload.best_t)",
                "distance = tuple(value for value in (payload.best_t,))[0]",
            ),
            "dictionary": SOURCE.replace(
                "distance = stable_distance(payload.best_t)",
                "distance = {'value': payload.best_t}['value']",
            ),
            "arbitrary_attribute": SOURCE.replace(
                "distance = stable_distance(payload.best_t)",
                "distance = payload.__class__",
            ),
            "atomic": SOURCE.replace(
                "distance = stable_distance(payload.best_t)",
                "distance = optix.atomic_add(payload.best_t, 1.0)",
            ),
            "exception": SOURCE.replace(
                "distance = stable_distance(payload.best_t)",
                "raise RuntimeError('escape')",
            ),
            "nested_function": SOURCE.replace(
                "result = value",
                "def hidden():\n        return value\n    result = hidden()",
                1,
            ),
            "default_argument": SOURCE.replace(
                "def stable_distance(value: f32) -> f32:",
                "def stable_distance(value: f32 = 0.0) -> f32:",
            ),
            "variadic": SOURCE.replace(
                "def stable_distance(value: f32) -> f32:",
                "def stable_distance(value: f32, *rest: f32) -> f32:",
            ),
            "yield": SOURCE.replace(
                "return result",
                "yield result",
                1,
            ),
            "async": SOURCE.replace(
                "def stable_distance(value: f32) -> f32:",
                "async def stable_distance(value: f32) -> f32:",
            ),
        }
        for name, source in attacks.items():
            with self.subTest(name=name):
                with self.assertRaises((CallbackVerificationError, SyntaxError)):
                    compile_callback_source(source, manifest())

    def test_role_effect_type_and_resource_violations_fail_closed(self):
        with self.assertRaises(CallbackVerificationError):
            compile_callback_source(SOURCE.replace(
                "return optix.no_hit()", "return optix.payload(payload=SearchPayload(best_t=ray.tmax, best_id=0))", 1
            ), manifest())
        with self.assertRaises(CallbackVerificationError):
            compile_callback_source(SOURCE.replace("item_id: u32", "item_id: f32", 1), manifest())
        with self.assertRaises(CallbackVerificationError):
            compile_callback_source(SOURCE, manifest(any_hit_delivery=None))
        with self.assertRaises(CallbackVerificationError):
            compile_callback_source(SOURCE, manifest(resources=dataclasses.replace(ResourceBudget(), max_payload_u32_slots=1)))
        with self.assertRaises(CallbackVerificationError):
            compile_callback_source(SOURCE, manifest(attribute_types=(U32,) * 9))

    def test_diagnostic_linkage_cannot_be_promoted(self):
        with self.assertRaises(CallbackVerificationError) as caught:
            compile_callback_source(
                SOURCE,
                manifest(selected_linkage=LinkageMechanism.TWO_MODULE_ORDINARY_DIAGNOSTIC),
            )
        self.assertEqual(caught.exception.code, "production_linkage_not_reviewed")

    def test_manifest_and_source_identity_fail_closed(self):
        spec = parse_callback_source(SOURCE, manifest())
        with self.assertRaises(CallbackVerificationError):
            verify_callback_program(dataclasses.replace(spec, source_sha256="0" * 64))
        with self.assertRaises(CallbackVerificationError):
            compile_callback_source(SOURCE.replace("attributes=(u32,)", "attributes=(f32,)"), manifest())
        with self.assertRaises(CallbackVerificationError):
            compile_callback_source(SOURCE, manifest(numeric=dataclasses.replace(NumericContract(), implicit_fast_math=True)))

    def test_canonical_json_roundtrip_is_strict_and_reverified(self):
        original = compile_callback_source(SOURCE, manifest())
        payload = json.loads(json.dumps(original.program.to_dict(), sort_keys=True))
        restored = callback_program_from_dict(payload)
        self.assertEqual(restored.ir_sha256, original.ir_sha256)
        self.assertEqual(verify_callback_program(restored).effect_digest, original.effect_digest)

        payload["unexpected"] = True
        with self.assertRaises(CallbackVerificationError) as caught:
            callback_program_from_dict(payload)
        self.assertEqual(caught.exception.code, "object_keys")

        mutated = json.loads(json.dumps(original.program.to_dict(), sort_keys=True))
        bounds = next(item for item in mutated["functions"] if item["role"] == "bounds")
        bounds["body"][-1]["effect"]["kind"] = "trace_request"
        with self.assertRaises(CallbackVerificationError) as semantic:
            callback_program_from_dict(mutated)
        self.assertEqual(semantic.exception.code, "role_effect")

        unknown_enum = json.loads(json.dumps(original.program.to_dict(), sort_keys=True))
        unknown_enum["manifest"]["selected_linkage"] = "unknown_linkage"
        with self.assertRaises(CallbackVerificationError) as enum_error:
            callback_program_from_dict(unknown_enum)
        self.assertEqual(enum_error.exception.code, "decode_error")

        malformed = json.loads(json.dumps(original.program.to_dict(), sort_keys=True))
        malformed["functions"][0]["body"][0] = {"kind": "return_effect"}
        with self.assertRaises(CallbackVerificationError) as shape_error:
            callback_program_from_dict(malformed)
        self.assertIn(shape_error.exception.code, {"object_keys", "decode_error"})

    def test_verified_geometry_requires_external_exact_source_authority(self):
        tested_spec = parse_callback_source(SOURCE, manifest())
        proof_sha = "1" * 64
        verified_geometry = GeometryContract(
            GeometryAdmission.VERIFIED_CONTRACT,
            "analytic_sphere_f32_outward_v1",
            True,
            proof_sha,
        )
        verified_manifest = manifest(geometry=verified_geometry)
        authority = GeometryProofAuthority(
            contract_name=verified_geometry.contract_name,
            callback_source_sha256=tested_spec.source_sha256,
            proof_sha256=proof_sha,
            target_f32_outward_rounding=True,
        )
        with self.assertRaises(CallbackVerificationError) as missing:
            compile_callback_source(SOURCE, verified_manifest)
        self.assertEqual(missing.exception.code, "geometry_proof_authority_missing")

        verified = compile_callback_source(
            SOURCE,
            verified_manifest,
            geometry_proof_authorities={authority.contract_name: authority},
        )
        self.assertEqual(verified.program.source_sha256, authority.callback_source_sha256)
        with self.assertRaises(CallbackVerificationError) as mismatch:
            compile_callback_source(
                SOURCE,
                verified_manifest,
                geometry_proof_authorities={
                    authority.contract_name: dataclasses.replace(
                        authority, callback_source_sha256="2" * 64
                    )
                },
            )
        self.assertEqual(mismatch.exception.code, "geometry_proof_authority_mismatch")

    def test_helper_recursion_and_unbounded_control_fail_closed(self):
        recursive = SOURCE.replace("return result", "return stable_distance(result)", 1)
        with self.assertRaises(CallbackVerificationError) as caught:
            compile_callback_source(recursive, manifest())
        self.assertEqual(caught.exception.code, "recursive_helper")
        dynamic = SOURCE.replace("range(LOOP_BOUND)", "range(value)")
        with self.assertRaises(CallbackVerificationError):
            compile_callback_source(dynamic, manifest())
        too_large = SOURCE.replace("range(LOOP_BOUND)", "range(1025)")
        with self.assertRaises(CallbackVerificationError):
            compile_callback_source(too_large, manifest())

    def test_runtime_faults_are_explicit_and_fail_closed(self):
        program = compile_callback_source(SOURCE, manifest())
        cases = [
            (CallbackRole.MAKE_RAY, {"launch_id": 1, "queries": ({"origin": (0, 0, 0), "tmax": 1.0},)}, RuntimeStatus.VIEW_OUT_OF_BOUNDS),
            (CallbackRole.MAKE_RAY, {"launch_id": 0, "queries": ({"origin": (0, 0, 0), "tmax": math.inf},)}, RuntimeStatus.NONFINITE_INPUT),
            (CallbackRole.BOUNDS, {"primitive": {"center": (0, 0, 0), "radius": -1.0, "item_id": 1}}, RuntimeStatus.INVALID_AABB),
            (CallbackRole.INTERSECTION, {"ray": {"origin": (0, 0, 0), "direction": (1, 0, 0), "tmin": 0, "tmax": 10}, "primitive": {"center": (0, 0, 0), "radius": 1.0, "item_id": 999}}, RuntimeStatus.INVALID_EFFECT),
        ]
        for role, arguments, status in cases:
            with self.subTest(role=role, status=status):
                with self.assertRaises(CallbackRuntimeError) as caught:
                    execute_callback_role(program, role, arguments)
                self.assertEqual(caught.exception.status, status)

    def test_runtime_integer_overflow_division_and_invalid_sqrt_fail_closed(self):
        overflow_source = SOURCE.replace(
            "updated = SearchPayload(best_t=hit.t, best_id=hit.hit_kind)",
            "overflow_id = hit.hit_kind + U32_MAX\n            updated = SearchPayload(best_t=hit.t, best_id=overflow_id)",
            1,
        )
        overflow_program = compile_callback_source(overflow_source, manifest())
        with self.assertRaises(CallbackRuntimeError) as overflow:
            execute_callback_role(overflow_program, CallbackRole.ANY_HIT, {
                "hit": {"t": 1.0, "hit_kind": 3}, "payload": {"best_t": 9.0, "best_id": 10},
            })
        self.assertEqual(overflow.exception.status, RuntimeStatus.INTEGER_OVERFLOW)

        division_source = SOURCE.replace(
            "distance = stable_distance(payload.best_t)",
            "distance = payload.best_t / 0.0",
        )
        division_program = compile_callback_source(division_source, manifest())
        with self.assertRaises(CallbackRuntimeError) as division:
            execute_callback_role(division_program, CallbackRole.FINALIZE, {
                "payload": {"best_t": 9.0, "best_id": 1},
            })
        self.assertEqual(division.exception.status, RuntimeStatus.DIVIDE_BY_ZERO)

        sqrt_source = SOURCE.replace("root = optix.sqrt(discriminant)", "root = optix.sqrt(-1.0)")
        sqrt_program = compile_callback_source(sqrt_source, manifest())
        with self.assertRaises(CallbackRuntimeError) as sqrt:
            execute_callback_role(sqrt_program, CallbackRole.INTERSECTION, {
                "ray": {"origin": (0, 0, 0), "direction": (1, 0, 0), "tmin": 0, "tmax": 100},
                "primitive": {"center": (5, 0, 0), "radius": 1.0, "item_id": 3},
            })
        self.assertEqual(sqrt.exception.status, RuntimeStatus.INVALID_SQRT)

    def test_record_recursion_and_view_in_payload_fail_closed(self):
        recursive_source = SOURCE.replace("best_id: u32", "best_id: SearchPayload", 1)
        with self.assertRaises(CallbackVerificationError):
            compile_callback_source(recursive_source, manifest())
        view_source = SOURCE.replace("best_id: u32", "best_id: ReadOnlyView[Query]", 1)
        with self.assertRaises(CallbackVerificationError):
            compile_callback_source(view_source, manifest())


if __name__ == "__main__":
    unittest.main()
