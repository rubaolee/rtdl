# Goal 110: v0.2 Segment-Polygon-Hitcount Closure

Date: 2026-04-05
Status: accepted

## Goal

Close one additional in-scope workload family for RTDL v0.2.

For v0.2, the chosen family is:

- `segment_polygon_hitcount`

This is the first release-defining workload bet beyond the v0.1 RayJoin-heavy
slice.

## Why this family

This workload satisfies the Goal 108 charter better than the nearest plausible
alternatives:

- it is a real spatial filter/refine workload, not a novelty demo
- it expands RTDL beyond the v0.1 join-centered story without reopening the
  full RayJoin `lsi` surface
- it has cleaner semantics than nearest-distance workloads:
  - exact `segment_id`
  - exact `hit_count`
- it already has visible runtime hooks across the current backend stack
- current local evidence is stronger than for `point_nearest_segment`

## Explicit non-choice

Goal 110 does **not** choose:

- broader `lsi` as the flagship v0.2 family
- a general “distance workloads” bucket
- ranking/counting demos
- generate-only mode

Those may still matter later, but they do not define the first v0.2 closure.

## Required outputs

- one accepted workload-family statement for `segment_polygon_hitcount`
- one correctness boundary
- one dataset set for authored, fixture-backed, and derived cases
- one backend closure plan
- one critique/rebuttal pass on whether this is really the right flagship

## Acceptance boundary

Goal 110 is accepted only if all of the following become true:

1. `segment_polygon_hitcount` is documented as a first-class RTDL workload
   family
2. one authored minimal case is parity-clean across:
   - `cpu_python_reference`
   - `cpu`
   - `embree`
   - `optix`
3. one deterministic fixture-backed county-derived case is parity-clean across:
   - `cpu_python_reference`
   - `cpu`
   - `embree`
   - `optix`
4. one deterministic derived case beyond the basic county fixture is
   parity-clean across:
   - `cpu_python_reference`
   - `cpu`
   - `embree`
   - `optix`
   and changes at least one structural property relative to the basic county
   fixture:
   - scale
   - overlap density
   - output-count regime
   - or a documented deterministic transformation recipe that materially
     changes the interaction pattern
5. emitted rows are compared using:
   - exact `segment_id`
   - exact `hit_count`
6. prepared-path checks exist for Embree and OptiX on at least the authored and
   fixture-backed cases
7. one explicit technical comparison against `lsi` exists and explains why
   `segment_polygon_hitcount` is the better first v0.2 closure target
8. one significance check exists beyond parity closure:
   - one deterministic derived case must either increase probe/build scale by
     at least `4x` over the basic county fixture or produce a materially
     denser output-count regime than the basic county fixture
   - the final package must state explicitly which of those two significance
     proofs it satisfied
9. one user-facing example and one release-facing report exist

## Backend note

Primary closure backends:

- Embree
- OptiX

Support-only backend for this goal:

- Vulkan

Vulkan may be included if it helps, but it is not required to define the Goal
110 family closure.

## Important honesty note

Current local documentation still places:

- `lsi`
- `segment_polygon_hitcount`
- `point_nearest_segment`

in the audited `native_loop` local bucket rather than the BVH-oriented Embree
path.

So Goal 110 must not overclaim RT-backed closure before the implementation and
evidence actually justify it.

If Goal 110 closes without moving the family beyond the current local
`native_loop` contract, the final package must describe it as workload-family
closure, not as proof of RT-backed maturity.

## Datasets and evidence shape

The accepted cases are:

- `authored_segment_polygon_minimal`
- one deterministic fixture-backed county-derived case
- one deterministic derived case beyond the basic fixture

The goal is not a paper-scale benchmark at first.
The goal is to close one additional workload family honestly and with stronger
evidence than a smoke package.

## Accepted closure note

Goal 110 closes as:

- workload-family closure
- semantic/backend closure

It does **not** close as a proof of RT-backed maturity for this family.

The current accepted package is explicit that `segment_polygon_hitcount`
remains under the audited local `native_loop` honesty boundary for this phase,
even though the family is now parity-clean and prepared-path clean across the
accepted backends and datasets.
