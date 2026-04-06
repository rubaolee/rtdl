# RTDL v0.2 So Far

Date: 2026-04-06
Status: current technical report

## Executive summary

RTDL v0.2 is no longer just a roadmap exercise.

So far, it has achieved three real things:

1. a disciplined scope and roadmap
2. one technically strong new workload family beyond the v0.1 RayJoin-heavy
   slice
3. one narrow but technically real generate-only product line

The strongest concrete v0.2 technical result so far is:

- `segment_polygon_hitcount`

That feature now has:

- explicit semantics
- authored, fixture, and derived deterministic cases
- large deterministic PostGIS validation
- user-facing examples
- generate-only output support
- strong Linux large deterministic performance on the audited rows across CPU,
  Embree, OptiX, and Vulkan

## What changed from v0.1

Compared with the archived v0.1 baseline, v0.2 now adds:

- a closed new workload family:
  - `segment_polygon_hitcount`
- a narrow generate-only path that emits runnable RTDL Python artifacts
- a stronger feature-product surface for user-facing examples and handoff
- a deeper backend/performance story for that new workload family

## Planning layer

The planning layer is in place:

- [v0_2_roadmap.md](../v0_2_roadmap.md)
- [v0_2_workload_scope_charter.md](../v0_2_workload_scope_charter.md)

That planning work matters because it kept v0.2 from turning into:

- random demos
- uncontrolled codegen sprawl
- performance work without a release-defining feature

## Feature line: `segment_polygon_hitcount`

This feature progressed through several stages:

- Goal 110:
  - workload-family closure
- Goal 114:
  - large deterministic correctness validation against PostGIS
- Goal 115 and 117:
  - productization and clearer usage surface
- Goal 116 and 118:
  - backend audit and Linux large-scale reporting
- Goal 121:
  - bounded bbox-prefilter attempt
- Goal 122:
  - candidate-index redesign for CPU/Embree/Vulkan
- Goal 123:
  - OptiX alignment with the same candidate-reduction strategy

Current practical result:

- correctness is strong
- large deterministic PostGIS parity is strong
- Linux large deterministic performance on the audited rows is now strong
  across:
  - CPU
  - Embree
  - OptiX
  - Vulkan

Important honesty boundary:

- this is a strong feature/product/performance result
- it is **not** the same thing as proving a mature RT-core-native traversal
  story for every backend

## Generate-only line

The generate-only work also moved from idea to reality:

- Goal 111:
  - narrow generate-only MVP
- Goal 113:
  - stronger handoff-bundle style output

Current honest state:

- useful enough to keep
- still intentionally narrow
- not yet broad code generation

## Best current technical statement

The best concise technical statement for v0.2 so far is:

- RTDL has moved beyond the v0.1 proof surface and now has one new closed
  workload family with strong correctness and strong Linux deterministic
  audited-row backend performance, plus one narrow kept generate-only feature.

## What remains weak

The main weak area is not the core `segment_polygon_hitcount` feature anymore.

The weak area is process/completeness:

- external Gemini/Claude review backfill is still pending
- later v0.2 goals need a cleaner saved review trail

## Final read

v0.2 so far is technically promising and materially stronger than “early
planning only.”

It is still not a finished v0.2 release.
But it is already a real technical branch with one strong feature line and one
credible secondary product line.
