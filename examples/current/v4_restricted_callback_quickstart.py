#!/usr/bin/env python3
"""CPU-only RTDL V4 restricted-callback quickstart.

The callback text below is parsed, verified, and interpreted.  It is never
imported or executed as Python.  GPU compilation is a separate target-bound
step described in docs/v4/tutorial.md.
"""

from __future__ import annotations

import json

from rtdsl.v4 import (
    F32,
    U32,
    AnyHitDeliveryContract,
    CallbackModuleManifest,
    CallbackRole,
    FrozenConstant,
    GeometryAdmission,
    GeometryContract,
    LinkageMechanism,
    NumericContract,
    ResourceBudget,
    compile_callback_abi,
    compile_callback_source,
    derive_compiler_recognized_any_hit_proof,
    execute_callback_role,
)


CALLBACK_SOURCE = r'''
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
        payload = SearchPayload(best_t=query.tmax, best_id=U32_MAX)
        return optix.trace_request(
            origin=query.origin,
            direction=vec3f32(1.0, 0.0, 0.0),
            tmin=0.0,
            tmax=query.tmax,
            payload=payload,
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
                return optix.hit(
                    t=selected_t,
                    hit_kind=primitive.item_id,
                    attributes=(primitive.item_id,),
                )
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
        value = SearchOutput(item_id=payload.best_id, distance=payload.best_t)
        return optix.output(value=value)
'''


def callback_manifest() -> CallbackModuleManifest:
    return CallbackModuleManifest(
        name="sphere_nearest_quickstart",
        payload_record="SearchPayload",
        output_record="SearchOutput",
        attribute_types=(U32,),
        constants=(FrozenConstant("U32_MAX", U32, 0xFFFFFFFF),),
        numeric=NumericContract(),
        resources=ResourceBudget(max_trace_depth=1, max_callable_depth=0),
        geometry=GeometryContract(
            GeometryAdmission.TESTED_USER_GEOMETRY,
            "quickstart_tested_sphere_v1",
            False,
        ),
        any_hit_delivery=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason="V4 trusted single-module callback composition",
    )


def run_quickstart() -> dict[str, object]:
    verified = compile_callback_source(CALLBACK_SOURCE, callback_manifest())
    any_hit_proof = derive_compiler_recognized_any_hit_proof(verified)
    abi = compile_callback_abi(verified, any_hit_proof_authority=any_hit_proof)
    bounds = execute_callback_role(verified, CallbackRole.BOUNDS, {
        "primitive": {"center": (5.0, 0.0, 0.0), "radius": 1.0, "item_id": 3},
    })
    intersection = execute_callback_role(verified, CallbackRole.INTERSECTION, {
        "ray": {
            "origin": (0.0, 0.0, 0.0),
            "direction": (1.0, 0.0, 0.0),
            "tmin": 0.0,
            "tmax": 100.0,
        },
        "primitive": {"center": (5.0, 0.0, 0.0), "radius": 1.0, "item_id": 3},
    })
    return {
        "status": "verified_cpu_semantics",
        "callback_ir_sha256": verified.ir_sha256,
        "callback_abi_sha256": abi.abi_sha256,
        "bounds": {
            "lower": tuple(float(value) for value in bounds.effect.field("lower")),
            "upper": tuple(float(value) for value in bounds.effect.field("upper")),
        },
        "first_hit": {
            "t": float(intersection.effect.field("t")),
            "item_id": int(intersection.effect.field("hit_kind")),
        },
        "user_source_executed_by_python": False,
        "gpu_execution_claimed": False,
    }


def main() -> None:
    print(json.dumps(run_quickstart(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
