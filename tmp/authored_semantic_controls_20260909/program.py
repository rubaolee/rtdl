"""Two independently authored source strings for a bounded semantic experiment."""
from pathlib import Path
import hashlib

TEMPLATE = r'''
@optix.payload
class WeightedPayload:
    weighted_value: u32
    hit_flag: u32
    semantic_tag: u32

@optix.record
class Query:
    origin: vec3f32
    direction: vec3f32
    tmax: f32

@optix.output
class WeightedOutput:
    weighted_value: u32
    hit_flag: u32
    semantic_tag: u32

@optix.program(payload=WeightedPayload, output=WeightedOutput, attributes=(), max_trace_depth=1, max_callable_depth=0)
class WeightedMetadata:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[Query]) -> TraceRequest:
        query = queries[launch_id]
        initial = WeightedPayload(weighted_value=U32_MAX, hit_flag=MISS_FLAG, semantic_tag=MISS_TAG)
        return optix.trace_request(origin=query.origin, direction=query.direction, tmin=0.0, tmax=query.tmax, payload=initial)

    @optix.closest_hit
    def closest_hit(hit: TriangleHit, payload: WeightedPayload, first_metadata: ReadOnlyView[u32], second_metadata: ReadOnlyView[u32]) -> WeightedPayload:
        p = hit.primitive_index
        value = WEIGHTED_EXPRESSION
        updated = WeightedPayload(weighted_value=value, hit_flag=HIT_FLAG, semantic_tag=HIT_TAG)
        return optix.payload(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: WeightedPayload) -> WeightedPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: WeightedPayload) -> WeightedOutput:
        result = WeightedOutput(weighted_value=payload.weighted_value, hit_flag=payload.hit_flag, semantic_tag=payload.semantic_tag)
        return optix.output(value=result)
'''


def source(power):
    if power not in (2, 3):
        raise ValueError("only frozen P2 and P3 are defined")
    expression = " + ".join(["first_metadata[p]"] + ["second_metadata[p]"] * power)
    return TEMPLATE.replace("WEIGHTED_EXPRESSION", expression)


def manifest():
    from rtdsl import v4
    constants = (("U32_MAX", 0xFFFFFFFF), ("HIT_FLAG", 1), ("MISS_FLAG", 0),
                 ("HIT_TAG", 0xA11CE001), ("MISS_TAG", 0xA11CE000),
                 ("FRONT_HIT_KIND", 0xFE), ("BACK_HIT_KIND", 0xFF))
    return v4.CallbackModuleManifest(
        name="weighted_metadata_semantic_control",
        payload_record="WeightedPayload", output_record="WeightedOutput",
        attribute_types=(),
        constants=tuple(v4.FrozenConstant(k, v4.U32, value) for k, value in constants),
        numeric=v4.NumericContract(), resources=v4.ResourceBudget(),
        geometry=v4.GeometryContract(v4.GeometryAdmission.OPTIX_BUILTIN_SEMANTICS,
                                     v4.BUILTIN_TRIANGLE_CONTRACT, False),
        any_hit_delivery=None,
        selected_linkage=v4.LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason="bounded public-source and metadata-binding experiment")


def physical_plan(verified, binding):
    from rtdsl import v4
    if binding not in ("normal", "swapped"):
        raise ValueError("only normal and swapped are defined")
    orientation = v4.BuiltinTriangleOrientationDeclaration(
        contract_name="weighted_metadata_ccw_v1",
        independent_cpu_oracle_sha256=hashlib.sha256(
            Path(__file__).with_name("oracle.py").read_bytes()).hexdigest(),
        winding_policy=v4.TriangleWindingPolicy.CCW_IS_FRONT,
        front_hit_kind=0xFE, back_hit_kind=0xFF,
        callback_front_hit_kind_constant="FRONT_HIT_KIND",
        callback_back_hit_kind_constant="BACK_HIT_KIND",
        front_hit_selects=v4.AdjacencySide.FRONT,
        back_hit_selects=v4.AdjacencySide.BACK)
    fields = v4.BuiltinTriangleU32x3FieldIds(
        vertex_positions="positions", triangle_indices="triangles",
        first_primitive_values="column_f", second_primitive_values="column_b",
        queries="queries", outputs="weighted_rows", status="status")
    return v4.build_builtin_triangle_u32x3_physical_plan(
        verified, field_ids=fields, orientation=orientation,
        first_metadata_argument_index=2 if binding == "normal" else 3,
        second_metadata_argument_index=3 if binding == "normal" else 2)
