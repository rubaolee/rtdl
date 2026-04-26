# Goal598: Apple RT Segment-Intersection Break-Even Analysis

Date: 2026-04-19

Status: proposed, pending external review

## Purpose

Goal598 evaluates whether to optimize Apple RT 2D `segment_intersection`.

The current implementation is correct but loops over every right segment:

```text
for each right segment:
    build one MPS quadrilateral acceleration structure
    dispatch any-hit for all left segments
    analytic-refine candidates
```

This costs:

```text
right_count AS builds + right_count dispatches
```

## MPS Constraint

`MPSIntersectionTypeAny` can answer whether a ray hit something, but MPS
documents primitive index as undefined for `Any`. Exact RTDL
`segment_intersection` needs the right-segment id for every output row.

Therefore, a faster exact path cannot use `Any` over a multi-primitive AS. It
must use nearest-hit with primitive index and enumerate hits.

## Candidate Strategy

Use the same exactness-preserving mask idea accepted for Goal597:

1. Partition right segments into chunks of at most 32 primitives.
2. Extrude each right segment in a chunk into a quadrilateral.
3. Build one MPS quadrilateral AS per chunk.
4. Assign one primitive-mask bit per right segment inside the chunk.
5. Use `MPSRayDataTypeOriginMaskDirectionMaxDistance`.
6. Enable primitive masks.
7. For each chunk, initialize each left-ray mask to all chunk bits set.
8. Run nearest-hit with primitive index.
9. Analytic-refine the returned left/right pair.
10. If the analytic segment intersection is valid, emit that row and clear the
    right-segment bit from that left ray.
11. Repeat until no hits remain or all chunk bits are cleared.

This preserves same-distance intersections because double-count prevention is
mask-based, not distance-epsilon-based.

## Cost Model

Let:

```text
L = left segment count
R = right segment count
C = chunk size, max 32
D = maximum number of true hits for any left segment within one chunk
```

Current path:

```text
AS builds: R
dispatches: R
candidate identity: known from outer loop
```

Masked chunk path:

```text
AS builds: ceil(R / C)
dispatches: sum(max passes needed per chunk)
          <= R
```

Best case:

```text
AS builds: ceil(R / 32)
dispatches: ceil(R / 32)
```

This happens when most chunks have no hit or one hit depth per left ray.

Dense all-pair case:

```text
AS builds: ceil(R / 32)
dispatches: R
```

This is still better on AS builds, but not on dispatch count.

## Existing Dense Fixture

Goal595 local dense fixture:

```text
left=128
right=128
rows=16384
```

Current Apple RT median in the latest Goal597 post-change harness:

```text
0.092515083 s
```

Embree median:

```text
0.007795938 s
```

Apple / Embree ratio:

```text
11.867x
```

The dense fixture is the worst structural case for output volume: every left
segment intersects every right segment.

## Decision

Proceed with implementation only if it is framed as a bounded exactness
experiment:

- It can reduce AS builds by up to 32x.
- It cannot reduce worst-case nearest-hit dispatches below `R` for dense
  all-pair outputs.
- It must preserve left-major output ordering.
- It must keep analytic refinement after MPS candidate discovery.
- It must not become public performance wording unless Goal595-style stability
  and parity gates pass.

## Required Tests If Implemented

- One left segment with zero intersections.
- One left segment with one intersection.
- One left segment with multiple intersections in a single 32-primitive chunk.
- Intersections across more than 32 right segments.
- Multiple right segments crossing at the same point/distance.
- Left-major output ordering.
- Parity against CPU reference and current Apple RT behavior.

## Codex Verdict

ACCEPT implementation as a bounded v0.9.2 experiment. The same masked chunked
nearest-hit design that made Goal597 exact can be applied to segment
intersection. The likely benefit is lower AS-build overhead, not a guaranteed
dense-case dispatch reduction. If implementation fails parity or does not
improve the measured median, keep the current path and record a technical stop.
