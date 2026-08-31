
@optix.payload
class AnyContactPayload:
    hit: u32

@optix.record
class MotionSegment:
    start: vec3f32
    end: vec3f32

@optix.output
class AnyContactOutput:
    hit: u32

@optix.program(payload=AnyContactPayload, output=AnyContactOutput, attributes=(), max_trace_depth=1, max_callable_depth=0)
class StaticRoundLinearCurveAnyContact:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[MotionSegment]) -> TraceRequest:
        query = queries[launch_id]
        direction = query.end - query.start
        initial = AnyContactPayload(hit=ZERO_U32)
        return optix.trace_request(origin=query.start, direction=direction, tmin=ZERO_F32, tmax=ONE_F32, payload=initial)

    @optix.closest_hit
    def closest_hit(hit: Hit, payload: AnyContactPayload, application_ids: ReadOnlyView[u32]) -> AnyContactPayload:
        updated = AnyContactPayload(hit=ONE_U32)
        return optix.payload(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: AnyContactPayload) -> AnyContactPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: AnyContactPayload) -> AnyContactOutput:
        result = AnyContactOutput(hit=payload.hit)
        return optix.output(value=result)
