from __future__ import annotations

import argparse
import dataclasses
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import tarfile
from typing import Mapping, Sequence

from rtdsl.v4_callback_frontend import compile_callback_source, parse_callback_source
from rtdsl.v4_callback_interpreter import execute_callback_role
from rtdsl.v4_callback_ir import (
    F32,
    U32,
    U64,
    AnyHitDeliveryContract,
    CallbackModuleManifest,
    CallbackRole,
    CallbackVerificationError,
    FrozenConstant,
    GeometryAdmission,
    GeometryContract,
    LinkageMechanism,
    NumericContract,
    ResourceBudget,
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
)
from rtdsl.v4_typed_physical_schema import (
    BUILTIN_TRIANGLE_CONTRACT,
    BufferAccess,
    BufferDomain,
    BufferFieldSchema,
    BufferSemantic,
    CountRelation,
    GasSchema,
    GasUpdatePolicy,
    GeometryFamily,
    HitChannelProducer,
    HitChannelSchema,
    HitChannelSemantic,
    PhysicalSchemaError,
    PhysicalValueType,
    ReferenceTargetProfile,
    TypedPhysicalSchemaV1,
    default_reference_templates,
    lower_canonical_reference_plan,
    verify_callback_program_for_geometry,
    verify_typed_physical_schema,
)

from scripts.goal5757_lane_probe_framework import validate_lane_probe
from scripts.goal5757_semantic_coverage import (
    LaneSemanticCoverageError,
    fragment_capabilities,
    require_complete_lane,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_BASE = ROOT / "history/internal_docs/goal5757_pre_support_lane_contract_freeze_20260811.json"
CONTRACT_A1 = ROOT / "history/internal_docs/goal5757_pre_support_lane_contract_freeze_amendment_a1_20260811.json"
CORE_FREEZE = ROOT / "history/internal_docs/goal5757_v4_core_freeze_manifest_20260811.json"
CAPABILITY_VOCABULARY = ROOT / "history/internal_docs/goal5757_frozen_v4_capability_vocabulary_20260811.json"
GOAL5756_RESULT = ROOT / "history/internal_docs/goal5756_builtin_triangle_runtime_and_home_result_20260811.json"
OUTPUT_ROOT = ROOT / "history/internal_docs/goal5757_lane_probe_evidence_20260811"
ARCHIVE = ROOT / "history/internal_docs/goal5757_lane_probe_evidence_20260811.tar.gz"
ARCHIVE_TWIN = ROOT / "history/internal_docs/goal5757_lane_probe_evidence_twin_20260811.tar.gz"

SCHEMA = "rtdl.goal5757.executable_lane_probe_matrix.v1"
CONTRACT_FREEZE_SHA256 = hashlib.sha256(CONTRACT_A1.read_bytes()).hexdigest()
U32_MAX = 0xFFFFFFFF


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_json(value: object) -> str:
    return _sha_bytes(_canonical(value))


def _write(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return _sha_bytes(data)


def _write_json(path: Path, value: object) -> str:
    return _write(path, _canonical(value))


def _build_archive(path: Path) -> None:
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as archive:
                for source in sorted(item for item in OUTPUT_ROOT.rglob("*") if item.is_file()):
                    payload = source.read_bytes()
                    name = "goal5757_lane_probe_evidence/" + source.relative_to(OUTPUT_ROOT).as_posix()
                    info = tarfile.TarInfo(name)
                    info.size = len(payload)
                    info.mtime = 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mode = 0o644
                    archive.addfile(info, io.BytesIO(payload))


def _target() -> ReferenceTargetProfile:
    return ReferenceTargetProfile(
        provider="optix",
        optix_sdk="9.0.0",
        compute_capability="6.1",
        native_sha256="9c9ffd91e02a53aba7a2b399e65985ce3cb76d1620a2b3960b845efddb7bc5cd",
        supports_custom_aabb=True,
        supports_builtin_triangle=True,
    )


def _plan_dict(plan) -> dict[str, object]:
    return {
        "template_id": plan.template_id.value,
        "schema_sha256": plan.schema_sha256,
        "callback_ir_sha256": plan.callback_ir_sha256,
        "effect_digest": plan.effect_digest,
        "target_sha256": plan.target_sha256,
        "role_topology": list(plan.role_topology),
        "ordered_buffer_semantics": [item.value for item in plan.ordered_buffer_semantics],
        "authority_nonce": plan.authority_nonce,
        "executable": plan.executable,
        "plan_sha256": plan.plan_sha256,
    }


BOX_SOURCE = r'''
@optix.payload
class BoxPayload:
    hit_count: u32
    minimum_id: u32

@optix.record
class BoxPrimitive:
    lower: vec3f32
    upper: vec3f32
    item_id: u32

@optix.record
class BoxQuery:
    lower: vec3f32
    upper: vec3f32

@optix.output
class BoxOutput:
    hit_count: u32
    minimum_id: u32

@optix.program(
    payload=BoxPayload,
    output=BoxOutput,
    attributes=(u32,),
    max_trace_depth=1,
    max_callable_depth=0,
)
class BoxOverlapProgram:
    @optix.bounds
    def bounds(primitive: BoxPrimitive) -> Aabb3f:
        return optix.aabb(lower=primitive.lower, upper=primitive.upper)

    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[BoxQuery]) -> TraceRequest:
        query = queries[launch_id]
        initial = BoxPayload(hit_count=0, minimum_id=U32_MAX)
        return optix.trace_request(
            origin=query.lower,
            direction=query.upper,
            tmin=0.0,
            tmax=1.0,
            payload=initial,
        )

    @optix.intersection
    def intersection(ray: Ray3f, primitive: BoxPrimitive) -> IntersectionEffect:
        overlap = primitive.lower.x <= ray.direction.x and primitive.upper.x >= ray.origin.x and primitive.lower.y <= ray.direction.y and primitive.upper.y >= ray.origin.y
        if overlap:
            return optix.hit(t=0.0, hit_kind=primitive.item_id, attributes=(primitive.item_id,))
        else:
            return optix.no_hit()

    @optix.any_hit
    def any_hit(hit: Hit, payload: BoxPayload) -> AnyHitEffect:
        updated_count = payload.hit_count + 1
        updated_id = hit.hit_kind if hit.hit_kind < payload.minimum_id else payload.minimum_id
        updated = BoxPayload(hit_count=updated_count, minimum_id=updated_id)
        return optix.accept_continue(payload=updated)

    @optix.closest_hit
    def closest_hit(hit: Hit, payload: BoxPayload) -> BoxPayload:
        return optix.payload(payload=payload)

    @optix.miss
    def miss(ray: Ray3f, payload: BoxPayload) -> BoxPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: BoxPayload) -> BoxOutput:
        value = BoxOutput(hit_count=payload.hit_count, minimum_id=payload.minimum_id)
        return optix.output(value=value)
'''


SEGMENT_SOURCE = r'''
@optix.payload
class SegmentPayload:
    best_t: f32
    feature_id: u32

@optix.record
class SegmentPrimitive:
    a: vec3f32
    b: vec3f32
    feature_id: u32

@optix.record
class PointQuery:
    point: vec3f32
    tmax: f32

@optix.output
class LocationOutput:
    segment_id: u32
    face_id: u32

@optix.program(
    payload=SegmentPayload,
    output=LocationOutput,
    attributes=(u32,),
    max_trace_depth=1,
    max_callable_depth=0,
)
class DirectedSegmentPointLocation:
    @optix.bounds
    def bounds(primitive: SegmentPrimitive) -> Aabb3f:
        lower = vec3f32(optix.min(primitive.a.x, primitive.b.x), optix.min(primitive.a.y, primitive.b.y), -Z_EPSILON)
        upper = vec3f32(optix.max(primitive.a.x, primitive.b.x), optix.max(primitive.a.y, primitive.b.y), Z_EPSILON)
        return optix.aabb(lower=lower, upper=upper)

    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[PointQuery]) -> TraceRequest:
        query = queries[launch_id]
        initial = SegmentPayload(best_t=query.tmax, feature_id=U32_MAX)
        return optix.trace_request(
            origin=query.point,
            direction=vec3f32(0.0, 1.0, 0.0),
            tmin=0.0,
            tmax=query.tmax,
            payload=initial,
        )

    @optix.intersection
    def intersection(ray: Ray3f, primitive: SegmentPrimitive) -> IntersectionEffect:
        dx = primitive.b.x - primitive.a.x
        if optix.abs(dx) > DENOM_EPSILON:
            u = (ray.origin.x - primitive.a.x) / dx
            y = primitive.a.y + u * (primitive.b.y - primitive.a.y)
            t = y - ray.origin.y
            if u >= 0.0 and u <= 1.0 and t >= ray.tmin and t <= ray.tmax:
                return optix.hit(t=t, hit_kind=primitive.feature_id, attributes=(primitive.feature_id,))
            else:
                return optix.no_hit()
        else:
            return optix.no_hit()

    @optix.any_hit
    def any_hit(hit: Hit, payload: SegmentPayload) -> AnyHitEffect:
        better = hit.t < payload.best_t or (hit.t == payload.best_t and hit.hit_kind < payload.feature_id)
        if better:
            updated = SegmentPayload(best_t=hit.t, feature_id=hit.hit_kind)
            return optix.accept_continue(payload=updated)
        else:
            return optix.accept_continue(payload=payload)

    @optix.closest_hit
    def closest_hit(hit: Hit, payload: SegmentPayload) -> SegmentPayload:
        updated = SegmentPayload(best_t=hit.t, feature_id=hit.hit_kind)
        return optix.payload(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: SegmentPayload) -> SegmentPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: SegmentPayload) -> LocationOutput:
        value = LocationOutput(segment_id=payload.feature_id, face_id=payload.feature_id)
        return optix.output(value=value)
'''


TRIANGLE_COUNT_SOURCE = r'''
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


FRONTEND_GAP_SOURCES = {
    "cross_launch_keyed_i64_reduce": TRIANGLE_COUNT_SOURCE.replace(
        "value = CountOutput(count=payload.count)",
        "reduced = optix.checked_group_reduce(payload.count)\n        value = CountOutput(count=reduced)",
    ),
    "bounded_ranked_row_emit": BOX_SOURCE.replace(
        "value = BoxOutput(hit_count=payload.hit_count, minimum_id=payload.minimum_id)",
        "emitted = optix.emit_bounded(payload.hit_count)\n        value = BoxOutput(hit_count=emitted, minimum_id=payload.minimum_id)",
    ),
    "global_argmax_witness": BOX_SOURCE.replace(
        "value = BoxOutput(hit_count=payload.hit_count, minimum_id=payload.minimum_id)",
        "winner = optix.global_argmax(payload.hit_count)\n        value = BoxOutput(hit_count=winner, minimum_id=payload.minimum_id)",
    ),
    "spatial_union_components": BOX_SOURCE.replace(
        "value = BoxOutput(hit_count=payload.hit_count, minimum_id=payload.minimum_id)",
        "component = optix.union_components(payload.hit_count)\n        value = BoxOutput(hit_count=component, minimum_id=payload.minimum_id)",
    ),
    "multi_stage_frontier_continuation": BOX_SOURCE.replace(
        "value = BoxOutput(hit_count=payload.hit_count, minimum_id=payload.minimum_id)",
        "frontier = optix.trace_frontier(payload.hit_count)\n        value = BoxOutput(hit_count=frontier, minimum_id=payload.minimum_id)",
    ),
}


def _custom_manifest(name: str, payload: str, output: str, *, attributes=(U32,), constants=()) -> CallbackModuleManifest:
    return CallbackModuleManifest(
        name=name,
        payload_record=payload,
        output_record=output,
        attribute_types=attributes,
        constants=tuple(constants),
        numeric=NumericContract(),
        resources=ResourceBudget(),
        geometry=GeometryContract(GeometryAdmission.TESTED_USER_GEOMETRY, name + "_geometry_v1", False),
        any_hit_delivery=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason="Goal5757 frozen local coverage probe; no production authority minted",
    )


def _box_manifest() -> CallbackModuleManifest:
    return _custom_manifest(
        "box_overlap_fragment", "BoxPayload", "BoxOutput",
        constants=(FrozenConstant("U32_MAX", U32, U32_MAX),),
    )


def _segment_manifest() -> CallbackModuleManifest:
    return _custom_manifest(
        "directed_segment_point_location_fragment", "SegmentPayload", "LocationOutput",
        constants=(
            FrozenConstant("U32_MAX", U32, U32_MAX),
            FrozenConstant("Z_EPSILON", F32, 1.0e-6),
            FrozenConstant("DENOM_EPSILON", F32, 1.0e-12),
        ),
    )


def _triangle_manifest() -> CallbackModuleManifest:
    return CallbackModuleManifest(
        name="triangle_per_ray_count_fragment",
        payload_record="CountPayload",
        output_record="CountOutput",
        attribute_types=(),
        constants=(),
        numeric=NumericContract(),
        resources=ResourceBudget(),
        geometry=GeometryContract(GeometryAdmission.OPTIX_BUILTIN_SEMANTICS, BUILTIN_TRIANGLE_CONTRACT, False),
        any_hit_delivery=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason="Goal5757 frozen built-in triangle per-ray fragment",
    )


def _custom_schema(callback) -> TypedPhysicalSchemaV1:
    return TypedPhysicalSchemaV1(
        callback.ir_sha256,
        callback.effect_digest,
        GeometryFamily.CUSTOM_AABB,
        (
            BufferFieldSchema(
                "primitives", BufferSemantic.CUSTOM_PRIMITIVE_DATA,
                BufferDomain.PRIMITIVE, PhysicalValueType.OPAQUE_RECORD,
                BufferAccess.READ_ONLY, CountRelation.PRIMITIVE_COUNT, 16,
            ),
        ),
        (
            HitChannelSchema(
                HitChannelSemantic.CUSTOM_HIT_KIND, PhysicalValueType.U32,
                HitChannelProducer.VERIFIED_INTERSECTION_EFFECT,
                (CallbackRole.ANY_HIT, CallbackRole.CLOSEST_HIT),
            ),
        ),
        (),
        GasSchema(GeometryFamily.CUSTOM_AABB, (BufferSemantic.CUSTOM_PRIMITIVE_DATA,), GasUpdatePolicy.STATIC, 1, 1),
    )


def _triangle_schema_without_adjacency(callback) -> TypedPhysicalSchemaV1:
    ro = BufferAccess.READ_ONLY
    buffers = (
        BufferFieldSchema("positions", BufferSemantic.VERTEX_POSITIONS, BufferDomain.VERTEX, PhysicalValueType.VEC3F32, ro, CountRelation.VERTEX_COUNT, 16),
        BufferFieldSchema("indices", BufferSemantic.TRIANGLE_INDICES, BufferDomain.PRIMITIVE, PhysicalValueType.VEC3U32, ro, CountRelation.PRIMITIVE_COUNT, 16),
    )
    roles = (CallbackRole.ANY_HIT,)
    channels = (
        HitChannelSchema(HitChannelSemantic.PRIMITIVE_INDEX, PhysicalValueType.U32, HitChannelProducer.OPTIX_BUILTIN, roles),
        HitChannelSchema(HitChannelSemantic.TRIANGLE_FRONT_BACK_HIT_KIND, PhysicalValueType.U32, HitChannelProducer.OPTIX_BUILTIN, roles),
        HitChannelSchema(HitChannelSemantic.TRIANGLE_BARYCENTRICS, PhysicalValueType.VEC2F32, HitChannelProducer.OPTIX_BUILTIN, roles),
        HitChannelSchema(HitChannelSemantic.PRIMITIVE_METADATA, PhysicalValueType.U32, HitChannelProducer.COMPILER_METADATA_LOOKUP, roles),
    )
    return TypedPhysicalSchemaV1(
        callback.ir_sha256, callback.effect_digest, GeometryFamily.BUILTIN_TRIANGLE,
        buffers, channels, (),
        GasSchema(GeometryFamily.BUILTIN_TRIANGLE, (BufferSemantic.VERTEX_POSITIONS, BufferSemantic.TRIANGLE_INDICES), GasUpdatePolicy.STATIC, 1, 1),
        triangle_winding=None,
        triangle_orientation_authority_sha256=None,
    )


def _program_evidence(source: str, manifest: CallbackModuleManifest, family: GeometryFamily) -> tuple[object, dict[str, object]]:
    if family is GeometryFamily.CUSTOM_AABB:
        callback = compile_callback_source(source, manifest)
    else:
        callback = verify_callback_program_for_geometry(
            parse_callback_source(source, manifest, schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION),
            family,
        )
    return callback, {
        "source_sha256": callback.program.source_sha256,
        "callback_ir_sha256": callback.ir_sha256,
        "effect_digest": callback.effect_digest,
        "roles": sorted(item.role.value for item in callback.program.functions if item.role is not None),
    }


def _box_cpu(callback) -> dict[str, object]:
    cases = []
    for primitive, ray, expected in (
        ({"lower": (0.0, 0.0, 0.0), "upper": (2.0, 2.0, 0.0), "item_id": 7}, {"origin": (1.0, 1.0, 0.0), "direction": (3.0, 3.0, 0.0), "tmin": 0.0, "tmax": 1.0}, True),
        ({"lower": (4.0, 4.0, 0.0), "upper": (5.0, 5.0, 0.0), "item_id": 9}, {"origin": (1.0, 1.0, 0.0), "direction": (3.0, 3.0, 0.0), "tmin": 0.0, "tmax": 1.0}, False),
    ):
        result = execute_callback_role(callback, CallbackRole.INTERSECTION, {"ray": ray, "primitive": primitive})
        observed = result.effect.kind.value == "hit"
        cases.append({"observed": observed, "expected": expected, "semantic_sha256": result.semantic_sha256})
    return {"case_count": len(cases), "mismatch_count": sum(item["observed"] != item["expected"] for item in cases), "cases": cases}


def _sphere_cpu(callback) -> dict[str, object]:
    cases = []
    primitive = {"center": (5.0, 0.0, 0.0), "radius": 1.0, "item_id": 3}
    for ray, expected_hit, expected_t in (
        ({"origin": (0.0, 0.0, 0.0), "direction": (1.0, 0.0, 0.0), "tmin": 0.0, "tmax": 100.0}, True, 4.0),
        ({"origin": (0.0, 3.0, 0.0), "direction": (1.0, 0.0, 0.0), "tmin": 0.0, "tmax": 100.0}, False, None),
    ):
        result = execute_callback_role(callback, CallbackRole.INTERSECTION, {"ray": ray, "primitive": primitive})
        observed_hit = result.effect.kind.value == "hit"
        observed_t = float(result.effect.field("t")) if observed_hit else None
        cases.append({"observed_hit": observed_hit, "observed_t": observed_t, "expected_hit": expected_hit, "expected_t": expected_t, "semantic_sha256": result.semantic_sha256})
    mismatches = sum((item["observed_hit"] != item["expected_hit"] or item["observed_t"] != item["expected_t"]) for item in cases)
    return {"case_count": len(cases), "mismatch_count": mismatches, "cases": cases}


def _segment_cpu(callback) -> dict[str, object]:
    cases = []
    primitive = {"a": (0.0, 2.0, 0.0), "b": (2.0, 4.0, 0.0), "feature_id": 5}
    for ray, expected_hit, expected_t in (
        ({"origin": (1.0, 0.0, 0.0), "direction": (0.0, 1.0, 0.0), "tmin": 0.0, "tmax": 10.0}, True, 3.0),
        ({"origin": (3.0, 0.0, 0.0), "direction": (0.0, 1.0, 0.0), "tmin": 0.0, "tmax": 10.0}, False, None),
    ):
        result = execute_callback_role(callback, CallbackRole.INTERSECTION, {"ray": ray, "primitive": primitive})
        observed_hit = result.effect.kind.value == "hit"
        observed_t = float(result.effect.field("t")) if observed_hit else None
        cases.append({"observed_hit": observed_hit, "observed_t": observed_t, "expected_hit": expected_hit, "expected_t": expected_t, "semantic_sha256": result.semantic_sha256})
    mismatches = sum((item["observed_hit"] != item["expected_hit"] or item["observed_t"] != item["expected_t"]) for item in cases)
    return {"case_count": len(cases), "mismatch_count": mismatches, "cases": cases}


def _triangle_cpu(callback) -> dict[str, object]:
    cases = []
    for before, after in ((0, 1), (7, 8)):
        result = execute_callback_role(callback, CallbackRole.ANY_HIT, {
            "hit": {"t": 1.0, "primitive_index": 3, "hit_kind": 0xFE, "barycentrics": (0.25, 0.25)},
            "payload": {"count": before},
        })
        observed = int(result.effect.field("payload").field("count"))
        cases.append({"observed": observed, "expected": after, "semantic_sha256": result.semantic_sha256})
    return {"case_count": len(cases), "mismatch_count": sum(item["observed"] != item["expected"] for item in cases), "cases": cases}


def _paper_contracts() -> list[dict[str, object]]:
    base = json.loads(CONTRACT_BASE.read_text(encoding="utf-8"))
    a1 = json.loads(CONTRACT_A1.read_text(encoding="utf-8"))
    lanes = [item for item in base["lanes"] if item["qualification"] == "AUTHORIZED_PAPER_APP"]
    lanes.append(a1["promoted_known_regression_lane"])
    if len(lanes) != 13:
        raise RuntimeError(f"expected 13 authorized lanes, got {len(lanes)}")
    for lane in lanes:
        for relative, expected in lane["source_pins"]:
            observed = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            if observed != expected:
                raise RuntimeError(f"source pin drift: {relative}: {observed} != {expected}")
    return lanes


def _paper_evidence(lane: Mapping[str, object]) -> str:
    return _sha_json({
        "app_id": lane["app_id"], "lane_id": lane["lane_id"],
        "paper_algorithm": lane["paper_algorithm"],
        "input_contract": lane["input_contract"], "output_contract": lane["output_contract"],
        "author_contract": lane["author_contract"], "oracle_contract": lane["oracle_contract"],
        "source_pins": lane["source_pins"],
    })


def _probe_payload(lane: Mapping[str, object], classification: str, **changes) -> dict[str, object]:
    payload = {
        "schema": "rtdl.goal5757.lane_probe_result.v1",
        "app_id": lane["app_id"], "lane_id": lane["lane_id"],
        "qualification": "AUTHORIZED_PAPER_APP", "classification": classification,
        "contract_freeze_sha256": CONTRACT_FREEZE_SHA256,
        "callback_source_sha256": None, "callback_ir_sha256": None,
        "cpu_oracle_sha256": None, "cpu_differential_case_count": 0,
        "cpu_differential_mismatch_count": 0, "typed_schema_sha256": None,
        "canonical_plan_sha256": None, "canonical_plan_count": 0,
        "partner_preflight_sha256": None, "target_compile_preflight_sha256": None,
        "forbidden_identity_dispatch_hits": 0, "fail_closed_stage": None,
        "fail_closed_code": None, "minimal_counterexample_sha256": None,
        "required_missing_contract": None,
        "paper_semantic_evidence_sha256": None,
        "existing_composition_insufficient_reason": None,
        "cross_app_reuse_candidates": [],
    }
    payload.update(changes)
    validate_lane_probe(payload)
    return payload


def _actual_frontend_failure(source: str, manifest: CallbackModuleManifest) -> tuple[str, str]:
    try:
        compile_callback_source(source, manifest)
    except CallbackVerificationError as error:
        return error.code, str(error)
    raise RuntimeError("expected frontend failure did not occur")


def _triangle_schema_failure(callback) -> tuple[str, str, str]:
    schema = _triangle_schema_without_adjacency(callback)
    try:
        verify_typed_physical_schema(callback, schema, target=_target(), orientation_authorities={})
    except PhysicalSchemaError as error:
        match = re.search(r"rejected: ([a-z0-9_]+)@", str(error))
        code = match.group(1) if match else "physical_schema_error"
        return code, str(error), schema.schema_sha256
    raise RuntimeError("expected typed-schema failure did not occur")


def _write_source(name: str, source: str) -> str:
    return _write(OUTPUT_ROOT / "sources" / f"{name}.py", source.strip().encode("utf-8") + b"\n")


def _generate_fragment_evidence() -> dict[str, dict[str, object]]:
    from tests.goal5750_v4_callback_ir_test import SOURCE as SPHERE_SOURCE, manifest as sphere_manifest
    from tests.goal5755_v4_typed_physical_schema_test import (
        TRIANGLE_SOURCE as PARTICLE_SOURCE,
        admitted as particle_admitted,
        verified_callback as particle_callback,
    )
    fragments: dict[str, dict[str, object]] = {}
    specifications = (
        ("sphere_nearest", SPHERE_SOURCE, sphere_manifest(), GeometryFamily.CUSTOM_AABB, _sphere_cpu),
        ("box_overlap", BOX_SOURCE, _box_manifest(), GeometryFamily.CUSTOM_AABB, _box_cpu),
        ("directed_segment", SEGMENT_SOURCE, _segment_manifest(), GeometryFamily.CUSTOM_AABB, _segment_cpu),
        ("triangle_count", TRIANGLE_COUNT_SOURCE, _triangle_manifest(), GeometryFamily.BUILTIN_TRIANGLE, _triangle_cpu),
    )
    for name, source, manifest, family, cpu_runner in specifications:
        source_sha = _write_source(name, source)
        callback, program = _program_evidence(source, manifest, family)
        _write_json(OUTPUT_ROOT / "fragments" / f"{name}_callback_ir.json", {
            "program": callback.program.to_dict(),
            "verified": callback.to_dict(),
            "geometry_family": family.value,
        })
        cpu = cpu_runner(callback)
        cpu_sha = _write_json(OUTPUT_ROOT / "fragments" / f"{name}_cpu.json", cpu)
        schema_sha = None
        fragment_plan_sha = None
        schema_failure = None
        if family is GeometryFamily.CUSTOM_AABB:
            schema = _custom_schema(callback)
            authority = verify_typed_physical_schema(callback, schema, target=_target())
            plan = lower_canonical_reference_plan(authority, default_reference_templates())
            schema_sha = schema.schema_sha256
            fragment_plan_sha = plan.plan_sha256
            _write_json(OUTPUT_ROOT / "fragments" / f"{name}_schema.json", schema.to_dict())
            _write_json(OUTPUT_ROOT / "fragments" / f"{name}_fragment_plan.json", _plan_dict(plan))
        else:
            code, detail, attempted_schema_sha = _triangle_schema_failure(callback)
            schema_failure = {"code": code, "detail": detail, "attempted_schema_sha256": attempted_schema_sha}
            _write_json(OUTPUT_ROOT / "fragments" / f"{name}_schema_failure.json", schema_failure)
        fragments[name] = {
            **program, "source_file_sha256": source_sha, "cpu_sha256": cpu_sha,
            "cpu_case_count": cpu["case_count"], "cpu_mismatch_count": cpu["mismatch_count"],
            "typed_schema_sha256": schema_sha, "fragment_plan_sha256": fragment_plan_sha,
            "schema_failure": schema_failure,
        }

    particle = particle_callback()
    particle_authority = particle_admitted()
    particle_plan = lower_canonical_reference_plan(particle_authority, default_reference_templates())
    particle_source_sha = _write_source("particle_tracking", PARTICLE_SOURCE)
    goal5756 = json.loads(GOAL5756_RESULT.read_text(encoding="utf-8"))
    particle_cpu = {
        "case_count": int(goal5756["functional_result"]["query_count"]),
        "mismatch_count": 0,
        "basis": "Goal5756 exact CPU-device differential over the registered functional query set",
        "goal5756_result_sha256": hashlib.sha256(GOAL5756_RESULT.read_bytes()).hexdigest(),
        "goal5756_callback_ir_sha256": particle.ir_sha256,
        "cpu_device_differential_exact": goal5756["functional_result"]["cpu_device_differential_exact"],
    }
    particle_cpu_sha = _write_json(OUTPUT_ROOT / "fragments/particle_tracking_cpu.json", particle_cpu)
    _write_json(OUTPUT_ROOT / "fragments/particle_tracking_schema.json", particle_authority.schema.to_dict())
    _write_json(OUTPUT_ROOT / "fragments/particle_tracking_plan.json", _plan_dict(particle_plan))
    _write_json(OUTPUT_ROOT / "fragments/particle_tracking_callback_ir.json", {
        "program": particle.program.to_dict(),
        "verified": particle.to_dict(),
        "geometry_family": GeometryFamily.BUILTIN_TRIANGLE.value,
    })
    fragments["particle_tracking"] = {
        "source_sha256": particle.program.source_sha256,
        "source_file_sha256": particle_source_sha,
        "callback_ir_sha256": particle.ir_sha256,
        "effect_digest": particle.effect_digest,
        "cpu_sha256": particle_cpu_sha, "cpu_case_count": particle_cpu["case_count"], "cpu_mismatch_count": 0,
        "typed_schema_sha256": particle_authority.schema.schema_sha256,
        "fragment_plan_sha256": particle_plan.plan_sha256,
    }
    return fragments


LANE_DISPOSITIONS = {
    ("rtnn", "point_selection.spatial_bounded.v1"): ("sphere_nearest", "canonical_plan", "canonical_plan_missing_bounded_multi_round_topk", "bounded multi-round K<=64 ranked-row emission with exact distance/U32 tie order", "single per-ray nearest callback and one custom-AABB plan cannot represent iterative refit, K-ranked bounded emission, or row cardinality"),
    ("raydb", "ray_triangle.keyed_i64_sum.v1"): ("triangle_count", "typed_schema", "required_semantic", "generic built-in-triangle primitive metadata plus checked keyed signed-I64 aggregation", "built-in triangle schema v1 mandates particle front/back adjacency and has no generic signed-I64 primitive metadata contract"),
    ("librts", "aabb_index.prepared_query_2d.v1"): ("box_overlap", "canonical_plan", "canonical_plan_missing_bounded_candidate_rows", "bounded variable-length canonical candidate-row emission", "custom-AABB callback can test overlap and count hits but the sole plan returns one fixed output record per launch"),
    ("librts", "aabb_overlap.filter_bounded_emit_2d.v1"): ("box_overlap", "canonical_plan", "canonical_plan_missing_bounded_pair_emit", "bounded canonical intersecting-pair emission", "custom-AABB fragment expresses closed overlap but cannot emit the variable-length pair relation"),
    ("x_hd", "nearest_state.cell_mbr_exact_witness.v1"): ("sphere_nearest", "canonical_plan", "canonical_plan_missing_global_argmax_witness", "cross-query global directed-Hausdorff argmax with deterministic source/target witness", "one nearest output per launch does not implement the required global maximizing reduction and witness tie policy"),
    ("rt_dbscan", "fixed_radius.prepared_spatial_components.v1"): ("sphere_nearest", "canonical_plan", "canonical_plan_missing_radius_graph_components", "bounded radius-neighbor row emission plus deterministic union/component reduction", "single per-ray nearest custom-AABB plan cannot produce a radius graph or component closure"),
    ("rayjoin", "planar_map.directed_segment_point_location_2d.v1"): ("directed_segment", "canonical_plan", "canonical_plan_missing_exact_sos_point_location", "scaled-integer exact directed point-location with simulation-of-simplicity degeneracy policy", "the f32 Ray3f fragment handles nondegenerate crossings only; it cannot prove the paper exact scaled-integer SoS contract"),
    ("rayjoin", "logical_events.grouped_i64x2_count_sum.v1"): ("frontend:cross_launch_keyed_i64_reduce", "frontend", "call_forbidden", "cross-launch grouped I64x2 count plus checked signed-I64 sum", "Callback IR v1 exposes neither global/grouped effect nor writable/atomic cross-launch state"),
    ("rayjoin", "planar_map.segment_pair_grouped_range_exact_count_2d.v1"): ("directed_segment", "canonical_plan", "canonical_plan_missing_grouped_exact_segment_pairs", "exact-degeneracy segment-pair intersection plus grouped range count", "nondegenerate f32 segment callback cannot represent exact degeneracy policy or cross-pair grouped count"),
    ("rt_barneshut", "aggregate_hierarchy.frontier_reduce.v1"): ("frontend:multi_stage_frontier_continuation", "frontend", "call_forbidden", "multi-stage hierarchy frontier continuation with aggregate force reduction", "Callback IR v1 has trace depth one, no callable recursion, no dynamic frontier and no cross-launch reduction"),
    ("triangle_counting", "ray_triangle_scalar.all_hit_count_value.v1"): ("triangle_count", "typed_schema", "required_semantic", "generic built-in-triangle all-hit scalar plus checked cross-ray U64 reduction", "triangle schema v1 is hard-bound to front/back adjacency and partner composition lacks the paper scalar reduction"),
    ("triangle_counting", "ray_triangle_scalar.any_hit_weighted_value.v1"): ("triangle_count", "typed_schema", "required_semantic", "generic built-in-triangle weighted any-hit scalar plus checked cross-ray U64 reduction", "triangle schema v1 is hard-bound to front/back adjacency and cannot bind paper weights"),
}


def generate() -> dict[str, object]:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True)
    lanes = _paper_contracts()
    fragments = _generate_fragment_evidence()
    results = []
    support_files = []

    for lane in lanes:
        key = (lane["app_id"], lane["lane_id"])
        paper_sha = _paper_evidence(lane)
        _write_json(OUTPUT_ROOT / "paper_contracts" / f"{lane['app_id']}__{lane['lane_id'].replace('.', '_')}.json", {
            "lane": lane, "paper_semantic_evidence_sha256": paper_sha,
        })
        if key == ("particle_tracking", "tetrahedral_face_point_location_and_boundary_detection"):
            fragment = fragments["particle_tracking"]
            goal5756 = json.loads(GOAL5756_RESULT.read_text(encoding="utf-8"))
            partner_receipt = {
                "schema": "rtdl.goal5757.inherited_partner_target_preflight.v1",
                "goal5756_result_sha256": hashlib.sha256(GOAL5756_RESULT.read_bytes()).hexdigest(),
                "callback_ir_sha256": fragment["callback_ir_sha256"],
                "typed_schema_sha256": fragment["typed_schema_sha256"],
                "canonical_plan_sha256": fragment["fragment_plan_sha256"],
                "native_library_sha256": goal5756["source_identity"]["native_library_sha256"],
                "device_compiler_and_wrapper_preflight": goal5756["verification"],
                "functional_result": goal5756["functional_result"],
                "core_frozen_after_goal5756": True,
                "performance_claimed": False,
            }
            partner_sha = _write_json(OUTPUT_ROOT / "partner" / "particle_tracking_partner_preflight.json", partner_receipt)
            target_claim_sha = _sha_json({
                "target": goal5756["target"], "compiler_identity": goal5756["compiler_identity"],
                "native_library_sha256": goal5756["source_identity"]["native_library_sha256"],
                "behavioral_executor": goal5756["functional_result"]["behavioral_executor"],
            })
            target_sha = _write_json(OUTPUT_ROOT / "partner" / "particle_tracking_target_compile_preflight.json", {
                "target_compile_claim_sha256": target_claim_sha,
                "source": "Goal5756 exact Home target compile and behavioral launch evidence",
                "goal5756_result_sha256": hashlib.sha256(GOAL5756_RESULT.read_bytes()).hexdigest(),
            })
            payload = _probe_payload(
                lane, "SUPPORTED_NOW",
                callback_source_sha256=fragment["source_file_sha256"],
                callback_ir_sha256=fragment["callback_ir_sha256"],
                cpu_oracle_sha256=fragment["cpu_sha256"],
                cpu_differential_case_count=fragment["cpu_case_count"],
                cpu_differential_mismatch_count=fragment["cpu_mismatch_count"],
                typed_schema_sha256=fragment["typed_schema_sha256"],
                canonical_plan_sha256=fragment["fragment_plan_sha256"],
                canonical_plan_count=1,
                partner_preflight_sha256=partner_sha,
                target_compile_preflight_sha256=target_sha,
            )
        else:
            fragment_name, stage, fail_code, required, reason = LANE_DISPOSITIONS[key]
            if fragment_name.startswith("frontend:"):
                gap_name = fragment_name.split(":", 1)[1]
                source = FRONTEND_GAP_SOURCES[gap_name]
                if gap_name == "multi_stage_frontier_continuation":
                    manifest = _box_manifest()
                else:
                    manifest = _triangle_manifest()
                actual_code, detail = _actual_frontend_failure(source, manifest)
                if actual_code != fail_code:
                    raise RuntimeError(f"unexpected frontend code for {key}: {actual_code}")
                source_sha = _write_source(f"failure__{lane['app_id']}__{lane['lane_id'].replace('.', '_')}", source)
                counterexample = {"stage": stage, "code": actual_code, "detail": detail, "source_sha256": source_sha, "required_missing_contract": required}
                counterexample_sha = _write_json(OUTPUT_ROOT / "counterexamples" / f"{lane['app_id']}__{lane['lane_id'].replace('.', '_')}.json", counterexample)
                payload = _probe_payload(
                    lane, "MISSING_GENERIC_SEMANTIC",
                    callback_source_sha256=source_sha,
                    fail_closed_stage=stage, fail_closed_code=actual_code,
                    minimal_counterexample_sha256=counterexample_sha,
                    required_missing_contract=required,
                    paper_semantic_evidence_sha256=paper_sha,
                    existing_composition_insufficient_reason=reason,
                    cross_app_reuse_candidates=["generic_global_effect_and_checked_reduce_contract"],
                )
            else:
                fragment = fragments[fragment_name]
                coverage_failure = None
                if stage == "canonical_plan":
                    try:
                        require_complete_lane(
                            str(lane["lane_id"]),
                            fragment_capabilities(
                                geometry_family="custom_aabb",
                                has_any_hit="any_hit" in fragment["roles"],
                            ),
                        )
                    except LaneSemanticCoverageError as error:
                        if error.code != fail_code:
                            raise RuntimeError(f"semantic coverage code mismatch for {key}: {error.code}")
                        coverage_failure = {"code": error.code, "missing": list(error.missing), "detail": str(error)}
                    else:
                        raise RuntimeError(f"full lane unexpectedly covered: {key}")
                counterexample = {
                    "stage": stage, "code": fail_code,
                    "required_missing_contract": required,
                    "existing_fragment": fragment_name,
                    "fragment_callback_ir_sha256": fragment["callback_ir_sha256"],
                    "fragment_typed_schema_sha256": fragment["typed_schema_sha256"],
                    "fragment_plan_sha256": fragment["fragment_plan_sha256"],
                    "reason_full_lane_cannot_be_promoted": reason,
                }
                if coverage_failure is not None:
                    counterexample["actual_semantic_coverage_failure"] = coverage_failure
                if stage == "typed_schema":
                    actual = fragment["schema_failure"]
                    if actual is None or actual["code"] != fail_code:
                        raise RuntimeError(f"typed schema failure mismatch for {key}: {actual}")
                    counterexample["actual_core_failure"] = actual
                counterexample_sha = _write_json(OUTPUT_ROOT / "counterexamples" / f"{lane['app_id']}__{lane['lane_id'].replace('.', '_')}.json", counterexample)
                payload = _probe_payload(
                    lane, "MISSING_GENERIC_SEMANTIC",
                    callback_source_sha256=fragment["source_file_sha256"],
                    callback_ir_sha256=fragment["callback_ir_sha256"],
                    cpu_oracle_sha256=fragment["cpu_sha256"],
                    cpu_differential_case_count=fragment["cpu_case_count"],
                    cpu_differential_mismatch_count=fragment["cpu_mismatch_count"],
                    typed_schema_sha256=fragment["typed_schema_sha256"] if stage == "canonical_plan" else None,
                    canonical_plan_count=0,
                    fail_closed_stage=stage, fail_closed_code=fail_code,
                    minimal_counterexample_sha256=counterexample_sha,
                    required_missing_contract=required,
                    paper_semantic_evidence_sha256=paper_sha,
                    existing_composition_insufficient_reason=reason,
                    cross_app_reuse_candidates=[f"fragment:{fragment_name}"],
                )
        result_name = f"{lane['app_id']}__{lane['lane_id'].replace('.', '_')}.json"
        result_sha = _write_json(OUTPUT_ROOT / "results" / result_name, payload)
        results.append({"app_id": lane["app_id"], "lane_id": lane["lane_id"], "classification": payload["classification"], "result_sha256": result_sha, "result_file": f"results/{result_name}"})

    counts = {name: sum(item["classification"] == name for item in results) for name in ("SUPPORTED_NOW", "PARTNER_ONLY_GAP", "MISSING_GENERIC_SEMANTIC")}
    matrix = {
        "schema": SCHEMA,
        "goal": 5757,
        "status": "COMPLETE_LOCAL_COVERAGE_PROBE__NO_PRODUCT_CHANGE",
        "core_freeze_sha256": hashlib.sha256(CORE_FREEZE.read_bytes()).hexdigest(),
        "capability_vocabulary_sha256": hashlib.sha256(CAPABILITY_VOCABULARY.read_bytes()).hexdigest(),
        "contract_freeze_sha256": CONTRACT_FREEZE_SHA256,
        "paper_app_count": len({item["app_id"] for item in results}),
        "lane_count": len(results),
        "classification_counts": counts,
        "results": results,
        "claim_boundary": {
            "core_native_or_paper_app_changed": False,
            "new_primitive_added": False,
            "app_named_dispatch_added": False,
            "pod_or_performance_used": False,
            "held_out_generalization_claimed": False,
            "production_public_submission_claimed": False,
            "goal5753_relabelled": False,
        },
    }
    _write_json(OUTPUT_ROOT / "MATRIX.json", matrix)
    payloads = []
    for path in sorted(item for item in OUTPUT_ROOT.rglob("*") if item.is_file() and item.name != "MANIFEST.json"):
        payloads.append({"path": path.relative_to(OUTPUT_ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest = {"schema": "rtdl.goal5757.lane_probe_evidence_manifest.v1", "payload_count": len(payloads), "payload_bytes": sum(item["bytes"] for item in payloads), "payloads": payloads}
    _write_json(OUTPUT_ROOT / "MANIFEST.json", manifest)
    _build_archive(ARCHIVE)
    _build_archive(ARCHIVE_TWIN)
    if ARCHIVE.read_bytes() != ARCHIVE_TWIN.read_bytes():
        raise RuntimeError("deterministic evidence twin mismatch")
    return matrix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print", action="store_true")
    arguments = parser.parse_args()
    matrix = generate()
    if arguments.print:
        print(json.dumps(matrix, indent=2, sort_keys=True))
    else:
        print(f"Goal5757 lane probes: {matrix['paper_app_count']} apps / {matrix['lane_count']} lanes / {matrix['classification_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
