# Goal 112: Segment-Polygon Performance Maturation

Date: 2026-04-05
Status: accepted

## Goal

Improve and document real performance behavior for the newly closed
`segment_polygon_hitcount` workload family on accepted capable backends.

Goal 112 exists to support the release-defining v0.2 workload-family expansion
from Goal 110. It is not a free-floating tuning loop.

## Why this goal now

Goal 110 closed `segment_polygon_hitcount` as:

- workload-family closure
- semantic/backend closure

But Goal 110 was explicit that this family still sits under the current
audited `native_loop` honesty boundary, not a mature RT-backed traversal story.

So the next honest performance question is:

- what can we improve or characterize meaningfully for this family on current
  accepted hardware, without overclaiming RT-core maturity?

## Scope

Primary focus:

- `segment_polygon_hitcount`
- Embree
- OptiX

Reference baselines:

- `cpu_python_reference`
- `cpu`

Out of scope for this goal:

- reopening the full v0.1 RayJoin performance package
- broad Vulkan tuning
- claiming RT-backed maturity unless the evidence really changes
- arbitrary performance work that does not help the Goal 110 family directly

## Candidate performance targets

Goal 112 may improve one or more of:

1. cold-start behavior
2. prepared-path behavior
3. repeated-run stability
4. obvious unnecessary packing or setup overhead
5. evaluation/reporting quality for this family

## Acceptance boundary

Goal 112 is accepted only if all of the following become true:

1. one explicit performance matrix exists for `segment_polygon_hitcount` on:
   - authored minimal
   - fixture-backed county case
   - derived tiled county case
2. the matrix includes at least:
   - `cpu`
   - `embree`
   - `optix`
3. one prepared/cold-path explanation exists for Embree and OptiX
4. one concrete outcome is documented honestly:
   - either one measured fix
   - or one clearly justified “no fix worth taking now” conclusion tied to a
     specific bottleneck
5. the final package states clearly whether the family’s performance story is:
   - meaningfully improved
   - only better characterized
   - or still too weak to promote

## Important honesty note

Goal 112 must not silently slide from:

- “performance maturation for a closed family”

to:

- “proof that this family is now RT-core mature”

unless the lowering/runtime story actually changes and the evidence supports
that stronger claim.

## Required outputs

- one performance plan
- one explicit measurement contract
- one measured artifact set
- one performance report
- one critique/rebuttal pass on whether the improvement is real
- one final honest judgment on the family’s current performance position
