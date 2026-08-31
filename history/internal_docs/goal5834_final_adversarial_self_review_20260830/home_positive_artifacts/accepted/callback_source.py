
@optix.payload
class FirstContactPayload:
    hit: u32
    toi: f32
    application_id: u32

@optix.record
class MotionSegment:
    start: vec3f32
    end: vec3f32

@optix.output
class FirstContactOutput:
    hit: u32
    toi: f32
    application_id: u32

@optix.program(payload=FirstContactPayload, output=FirstContactOutput, attributes=(), max_trace_depth=1, max_callable_depth=0)
class StaticRoundLinearCurveFirstContact:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[MotionSegment]) -> TraceRequest:
        query = queries[launch_id]
        direction = query.end - query.start
        initial = FirstContactPayload(hit=ZERO_U32, toi=ONE_F32, application_id=U32_MAX)
        return optix.trace_request(origin=query.start, direction=direction, tmin=ZERO_F32, tmax=ONE_F32, payload=initial)

    @optix.closest_hit
    def closest_hit(hit: Hit, payload: FirstContactPayload, application_ids: ReadOnlyView[u32]) -> FirstContactPayload:
        updated = FirstContactPayload(hit=ONE_U32, toi=hit.t, application_id=application_ids[ZERO_U32])
        return optix.payload(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: FirstContactPayload) -> FirstContactPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: FirstContactPayload) -> FirstContactOutput:
        result = FirstContactOutput(hit=payload.hit, toi=payload.toi, application_id=payload.application_id)
        return optix.output(value=result)
