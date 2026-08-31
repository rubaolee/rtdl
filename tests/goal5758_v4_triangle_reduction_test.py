from __future__ import annotations

import dataclasses
from pathlib import Path
import unittest

from rtdsl.v4_callback_abi import AnyHitProofAuthority
from rtdsl.v4_callback_frontend import parse_callback_source
from rtdsl.v4_callback_interpreter import execute_callback_role
from rtdsl.v4_callback_ir import (
    AnyHitDeliveryContract,
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    CallbackModuleManifest,
    CallbackRole,
    GeometryAdmission,
    GeometryContract,
    LinkageMechanism,
    NumericContract,
    ResourceBudget,
    ScalarKind,
)
from rtdsl.v4_triangle_reduction import (
    CheckedReducerSpec,
    DuplicatePolicy,
    MetadataDomain,
    ReducerAlgebra,
    ReducerSource,
    ReducerSourceKind,
    TriangleMetadataBinding,
    TriangleMetadataChannel,
    TriangleReductionError,
    TriangleReductionSchema,
    compile_triangle_reduction_contract,
    compile_triangle_reduction_abi,
    execute_checked_reducer,
    verify_triangle_reduction_schema,
)
from rtdsl.v4_typed_physical_schema import (
    BUILTIN_TRIANGLE_CONTRACT,
    GeometryFamily,
    ReferenceTargetProfile,
    verify_callback_program_for_geometry,
)


ROOT = Path(__file__).resolve().parents[1]

COUNT_SOURCE = r'''
@optix.payload
class CountPayload:
    count: u64

@optix.record
class RayQuery:
    origin: vec3f32
    direction: vec3f32
    tmax: f32

@optix.output
class CountOutput:
    count: u64

@optix.program(
    payload=CountPayload,
    output=CountOutput,
    attributes=(),
    max_trace_depth=1,
    max_callable_depth=0,
)
class TrianglePerRayCount:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[RayQuery]) -> TraceRequest:
        query = queries[launch_id]
        initial = CountPayload(count=0)
        return optix.trace_request(origin=query.origin, direction=query.direction, tmin=0.0, tmax=query.tmax, payload=initial)

    @optix.any_hit
    def any_hit(hit: TriangleHit, payload: CountPayload) -> AnyHitEffect:
        updated = CountPayload(count=payload.count + 1)
        return optix.accept_continue(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: CountPayload) -> CountPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: CountPayload) -> CountOutput:
        value = CountOutput(count=payload.count)
        return optix.output(value=value)
'''

KEYED_SOURCE = r'''
@optix.payload
class EventPayload:
    accepted: u64

@optix.record
class RayQuery:
    origin: vec3f32
    direction: vec3f32
    tmax: f32

@optix.output
class EventOutput:
    accepted: u64

@optix.program(
    payload=EventPayload,
    output=EventOutput,
    attributes=(),
    max_trace_depth=1,
    max_callable_depth=0,
)
class KeyedTriangleEvents:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[RayQuery]) -> TraceRequest:
        query = queries[launch_id]
        initial = EventPayload(accepted=0)
        return optix.trace_request(origin=query.origin, direction=query.direction, tmin=0.0, tmax=query.tmax, payload=initial)

    @optix.any_hit
    def any_hit(
        hit: TriangleHit,
        payload: EventPayload,
        stable_ids: ReadOnlyView[u64],
        signed_values: ReadOnlyView[i64],
        include_flags: ReadOnlyView[u32],
    ) -> AnyHitEffect:
        include = include_flags[hit.primitive_index]
        if include == 1:
            updated = EventPayload(accepted=payload.accepted + 1)
            return optix.accept_continue(payload=updated)
        else:
            return optix.ignore(payload=payload)

    @optix.miss
    def miss(ray: Ray3f, payload: EventPayload) -> EventPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: EventPayload) -> EventOutput:
        value = EventOutput(accepted=payload.accepted)
        return optix.output(value=value)
'''


def manifest(name: str, payload: str, output: str) -> CallbackModuleManifest:
    return CallbackModuleManifest(
        name=name,
        payload_record=payload,
        output_record=output,
        attribute_types=(),
        constants=(),
        numeric=NumericContract(),
        resources=ResourceBudget(),
        geometry=GeometryContract(
            GeometryAdmission.OPTIX_BUILTIN_SEMANTICS,
            BUILTIN_TRIANGLE_CONTRACT,
            False,
        ),
        any_hit_delivery=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason="closed built-in triangle checked reduction",
    )


def callback(source=COUNT_SOURCE, *, keyed=False):
    spec = parse_callback_source(
        source,
        manifest(
            "keyed_triangle_events" if keyed else "triangle_per_ray_count",
            "EventPayload" if keyed else "CountPayload",
            "EventOutput" if keyed else "CountOutput",
        ),
        schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )
    return verify_callback_program_for_geometry(spec, GeometryFamily.BUILTIN_TRIANGLE)


def target() -> ReferenceTargetProfile:
    return ReferenceTargetProfile(
        provider="optix",
        optix_sdk="9.0.0",
        compute_capability="8.9",
        native_sha256="a" * 64,
        supports_custom_aabb=True,
        supports_builtin_triangle=True,
    )


def proof(cb):
    return AnyHitProofAuthority(
        callback_ir_sha256=cb.ir_sha256,
        effect_digest=cb.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256="b" * 64,
        proof_kind="external_machine_checked_order_independence_v1",
    )


def output(name: str) -> ReducerSource:
    return ReducerSource(ReducerSourceKind.PER_RAY_OUTPUT, output_field=name)


def metadata(name: str) -> ReducerSource:
    return ReducerSource(ReducerSourceKind.METADATA, semantic_id=name)


class Goal5758TriangleReductionTests(unittest.TestCase):
    def test_keyed_i64_real_consumer_contract_and_reference(self):
        cb = callback(KEYED_SOURCE, keyed=True)
        channels = (
            TriangleMetadataChannel("primitive.stable_id", "stable_ids", ScalarKind.U64, MetadataDomain.PRIMITIVE, True),
            TriangleMetadataChannel("primitive.signed_value", "signed_values", ScalarKind.I64, MetadataDomain.PRIMITIVE, True),
            TriangleMetadataChannel("primitive.include", "include_flags", ScalarKind.U32, MetadataDomain.PRIMITIVE, True),
        )
        reducer = CheckedReducerSpec(
            ReducerAlgebra.CHECKED_KEYED_I64_SUM,
            key_sources=(
                ReducerSource(ReducerSourceKind.LAUNCH_INDEX),
            ),
            value_source=metadata("primitive.signed_value"),
            include_source=metadata("primitive.include"),
            event_identity_sources=(
                metadata("primitive.stable_id"),
                ReducerSource(ReducerSourceKind.LAUNCH_INDEX),
            ),
            duplicate_policy=DuplicatePolicy.KEYED_IDENTICAL_DEDUP,
            output_capacity=16,
        )
        schema = TriangleReductionSchema(
            cb.ir_sha256,
            cb.effect_digest,
            channels,
            (
                TriangleMetadataBinding(CallbackRole.ANY_HIT, 2, "primitive.stable_id"),
                TriangleMetadataBinding(CallbackRole.ANY_HIT, 3, "primitive.signed_value"),
                TriangleMetadataBinding(CallbackRole.ANY_HIT, 4, "primitive.include"),
            ),
            reducer,
        )
        authority = verify_triangle_reduction_schema(cb, schema, target=target())
        abi = compile_triangle_reduction_abi(
            authority, any_hit_proof_authority=proof(cb))
        contract = compile_triangle_reduction_contract(authority, abi_sha256=abi.abi_sha256)
        self.assertFalse(contract.executable)
        self.assertTrue(contract.semantic_dict()["target_execution_receipt_required"])
        rows = (
            {"launch_index": 0, "primitive_index": 3, "primitive.stable_id": 30, "primitive.signed_value": 5, "primitive.include": 1},
            {"launch_index": 0, "primitive_index": 4, "primitive.stable_id": 40, "primitive.signed_value": -2, "primitive.include": 1},
            {"launch_index": 0, "primitive_index": 4, "primitive.stable_id": 40, "primitive.signed_value": -2, "primitive.include": 1},
            {"launch_index": 1, "primitive_index": 3, "primitive.stable_id": 30, "primitive.signed_value": 99, "primitive.include": 0},
            {"launch_index": 1, "primitive_index": 8, "primitive.stable_id": 80, "primitive.signed_value": -4, "primitive.include": 1},
        )
        self.assertEqual(
            execute_checked_reducer(reducer, rows),
            (((0,), 3), ((1,), -4)),
        )
        any_hit = execute_callback_role(cb, CallbackRole.ANY_HIT, {
            "hit": {"t": 1.0, "primitive_index": 1, "hit_kind": 0xFE, "barycentrics": (0.25, 0.25)},
            "payload": {"accepted": 2},
            "stable_ids": [4, 7], "signed_values": [9, -3], "include_flags": [0, 1],
        })
        self.assertEqual(int(any_hit.effect.field("payload").field("accepted")), 3)

    def test_u64_sum_and_weighted_sum_share_one_schema_family(self):
        cb = callback()
        plain = CheckedReducerSpec(
            ReducerAlgebra.CHECKED_U64_SUM, (), output("count"), output_capacity=1)
        plain_schema = TriangleReductionSchema(
            cb.ir_sha256, cb.effect_digest, (), (), plain)
        plain_authority = verify_triangle_reduction_schema(cb, plain_schema, target=target())
        abi = compile_triangle_reduction_abi(
            plain_authority, any_hit_proof_authority=proof(cb))
        self.assertEqual(
            compile_triangle_reduction_contract(
                plain_authority, abi_sha256=abi.abi_sha256).template_id,
            "builtin_triangle_checked_reduction_v1",
        )
        self.assertEqual(execute_checked_reducer(plain, ({"count": 2}, {"count": 5})), 7)

        weight = TriangleMetadataChannel(
            "query.weight", "query_weights", ScalarKind.U64, MetadataDomain.QUERY)
        weighted = CheckedReducerSpec(
            ReducerAlgebra.CHECKED_U64_PRODUCT_SUM,
            (), output("count"), multiplicand_source=metadata("query.weight"),
            output_capacity=1,
        )
        weighted_schema = TriangleReductionSchema(
            cb.ir_sha256, cb.effect_digest, (weight,), (), weighted)
        verify_triangle_reduction_schema(cb, weighted_schema, target=target())
        self.assertEqual(
            execute_checked_reducer(weighted, (
                {"count": 2, "query.weight": 3},
                {"count": 5, "query.weight": 7},
            )),
            41,
        )

    def test_fail_closed_overflow_duplicate_capacity_and_binding(self):
        cb = callback(KEYED_SOURCE, keyed=True)
        channel = TriangleMetadataChannel(
            "primitive.signed_value", "values", ScalarKind.I64,
            MetadataDomain.PRIMITIVE, True)
        bad_schema = TriangleReductionSchema(
            cb.ir_sha256, cb.effect_digest, (channel,), (),
            CheckedReducerSpec(
                ReducerAlgebra.CHECKED_KEYED_I64_SUM,
                (ReducerSource(ReducerSourceKind.LAUNCH_INDEX),),
                metadata("primitive.signed_value"),
                event_identity_sources=(
                    ReducerSource(ReducerSourceKind.LAUNCH_INDEX),
                    ReducerSource(ReducerSourceKind.PRIMITIVE_INDEX),
                ),
                output_capacity=2,
            ),
        )
        with self.assertRaisesRegex(TriangleReductionError, "metadata_binding_coverage"):
            verify_triangle_reduction_schema(cb, bad_schema, target=target())

        keyed = CheckedReducerSpec(
            ReducerAlgebra.CHECKED_KEYED_I64_SUM,
            (ReducerSource(ReducerSourceKind.LAUNCH_INDEX),),
            ReducerSource(ReducerSourceKind.METADATA, semantic_id="value"),
            event_identity_sources=(
                ReducerSource(ReducerSourceKind.LAUNCH_INDEX),
                ReducerSource(ReducerSourceKind.PRIMITIVE_INDEX),
            ),
            output_capacity=2,
        )
        duplicate = {"launch_index": 0, "primitive_index": 1, "value": 4}
        with self.assertRaisesRegex(TriangleReductionError, "duplicate_event_identity"):
            execute_checked_reducer(keyed, (duplicate, duplicate))
        with self.assertRaisesRegex(TriangleReductionError, "signed_i64_overflow"):
            execute_checked_reducer(keyed, (
                {"launch_index": 0, "primitive_index": 1, "value": (1 << 63) - 1},
                {"launch_index": 0, "primitive_index": 2, "value": 1},
            ))
        with self.assertRaisesRegex(TriangleReductionError, "output_capacity"):
            execute_checked_reducer(keyed, (
                {"launch_index": 0, "primitive_index": 1, "value": 1},
                {"launch_index": 1, "primitive_index": 1, "value": 1},
                {"launch_index": 2, "primitive_index": 1, "value": 1},
            ))

        dedup = dataclasses.replace(keyed, duplicate_policy=DuplicatePolicy.KEYED_IDENTICAL_DEDUP)
        self.assertEqual(execute_checked_reducer(dedup, (duplicate, duplicate)), (((0,), 4),))
        with self.assertRaisesRegex(TriangleReductionError, "conflicting_duplicate_event"):
            execute_checked_reducer(dedup, (duplicate, {**duplicate, "value": 5}))
        excluded = {**duplicate, "include": 0}
        dedup_with_include = dataclasses.replace(
            dedup, include_source=ReducerSource(
                ReducerSourceKind.METADATA, semantic_id="include"))
        with self.assertRaisesRegex(TriangleReductionError, "conflicting_duplicate_event"):
            execute_checked_reducer(dedup_with_include, (
                {**duplicate, "include": 1}, excluded))

        u64_sum = CheckedReducerSpec(
            ReducerAlgebra.CHECKED_U64_SUM, (), output("count"), output_capacity=1)
        count_cb = callback()
        authority = verify_triangle_reduction_schema(
            count_cb,
            TriangleReductionSchema(
                count_cb.ir_sha256, count_cb.effect_digest, (), (), u64_sum),
            target=target(),
        )
        with self.assertRaisesRegex(TriangleReductionError, "authority_reverification"):
            compile_triangle_reduction_abi(
                dataclasses.replace(authority, authority_nonce="c" * 64),
                any_hit_proof_authority=proof(authority.callback),
            )

        with self.assertRaisesRegex(TriangleReductionError, "unsigned_overflow"):
            execute_checked_reducer(u64_sum, ({"count": (1 << 64) - 1}, {"count": 1}))

    def test_product_core_has_no_consumer_identity_dispatch(self):
        text = (ROOT / "src/rtdsl/v4_triangle_reduction.py").read_text(encoding="utf-8").lower()
        for forbidden in ("raydb", "triangle_counting", "triangle counting", "paper-reproduction"):
            self.assertNotIn(forbidden, text)

    def test_current_typed_schema_authority_is_not_modified_by_successor_module(self):
        path = ROOT / "src/rtdsl/v4_typed_physical_schema.py"
        import hashlib
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            # Goal5831/5832 current authority.  This supersedes the pre-large-
            # NumPy-validation Goal5758 source identity without changing the
            # Goal5758 result artifact itself.
            "f1b093da9aa10465767beec8f22f804e080a6691abd7ec1873de231328cc7e5d",
        )


if __name__ == "__main__":
    unittest.main()
