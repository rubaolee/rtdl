# Goal3295 RayJoin PIP Boundary-Selection Gap Diagnosis

Date: 2026-06-04

Status: diagnosis complete; implementation deferred to a future generic primitive.

## Purpose

Goal3294 narrowed the same-slice RayJoin comparison but did not close it:

- LSI tuned RTDL route: 0.333 ms versus RayJoin 0.236 ms, or 1.41x.
- PIP tuned RTDL route: 0.361 ms versus RayJoin 0.225 ms, or 1.61x.

The purpose of Goal3295 is to explain why the remaining PIP gap is not solved
by another small routing flag.

## What The Pod Evidence Says

Goal3294 already uses the best safe existing RTDL PIP route on the A5000 pod:

- `count_mode=device_filtered_validated`
- `device_filtered_boundary_mode=inclusive`
- `query_axis=z_point`
- `RTDL_OPTIX_POINT_PRIMITIVE_USE_SCALAR_COUNT_PIPELINE=1`

Native telemetry for the tuned PIP lane shows:

- `candidate_write_pass = 0.0`
- `candidate_download = 0.0`
- `exact_refine = 0.0`
- `mode = device_filtered_count`
- `emitted_count = 1430`

So the old row materialization/refinement problem is not the remaining timed
lane bottleneck. The remaining gap is in the traversal/count formulation.

## RayJoin Difference

A read of upstream RayJoin's PIP RT path on the pod shows a different generic
shape:

- RayJoin traces one upward ray per query point.
- The intersection program examines candidate edge ranges and keeps the best
  crossing boundary event in OptiX payload state.
- The output is a per-point closest/best edge id, later interpreted by the app.

That is not the same contract as RTDL's current generic
point/closed-shape-membership count. RTDL asks: "which closed shapes contain
this point, and how many positive memberships exist?" RayJoin's fast PIP path
asks: "what is the best upward boundary crossing for this point?"

Both are legitimate geometric contracts, but they are not identical execution
contracts.

## Design Conclusion

The next reusable primitive should be generic boundary selection, not a
RayJoin-specific native endpoint.

Candidate primitive family:

- `point_closed_shape_best_boundary_crossing_2d`
- `point_closed_shape_first_crossing_2d`

Expected generic outputs:

- query id
- shape id
- boundary or edge id
- crossing parameter
- tie-break status
- optional validity flag

Expected app-side responsibilities:

- RayJoin map-id interpretation
- simulation-of-simplicity policy choices
- polygon assignment interpretation
- overlay/output-chain logic

## Boundary

Do not put RayJoin-specific `closest_eid` semantics into the native ABI. The
engine should expose a generic prepared edge/range traversal and best-boundary
event contract. Benchmark apps can then adapt that event stream to RayJoin,
point-in-polygon, overlay, or other closed-shape membership policies.

This report does not authorize a release, RTDL-beats-RayJoin claim, public
speedup claim, RayJoin paper reproduction claim, true-zero-copy claim, or broad
RT-core speedup claim.

The future-version to-do list now records this as
`Generic Closed-Shape Boundary Selection`.
