# Goal597: Apple RT Hit-Count Optimization Design Note

Date: 2026-04-19

Status: proposed, pending review before implementation

## Purpose

Goal597 investigates whether the current Apple Metal/MPS RT 3D
`ray_triangle_hit_count` path can be made materially faster while preserving
exact RTDL result semantics.

The current path is correct but slow because it loops over every triangle,
builds a one-triangle MPS acceleration structure, dispatches any-hit for all
rays, and increments the per-ray count.

## Required Correctness Contract

For each input ray, the result must equal the CPU reference count:

```text
for each ray:
    count every triangle intersected by that finite ray
```

This includes:

- multiple triangles hit by the same ray,
- triangles at very close distances,
- co-planar or stacked triangles at the same hit distance,
- stable one-row-per-ray output shape,
- no double-counting the same primitive.

## MPS API Facts Relevant To Hit Count

Apple MPS `MPSRayIntersector` supports:

- `MPSIntersectionTypeNearest`
- `MPSIntersectionTypeAny`

`Nearest` can return a primitive index when using
`MPSIntersectionDataTypeDistancePrimitiveIndex`.

`Any` cannot be used for exact all-hit enumeration because MPS documents the
primitive index as undefined for `Any`.

MPS also supports primitive and ray masks:

- a polygon acceleration structure can provide one `uint32_t` primitive mask per
  primitive,
- a ray can provide a `uint32_t` ray mask,
- the intersector can skip intersections based on the mask operator.

This gives only 32 directly addressable bit positions per ray mask.

## Rejected Naive Single-AS Strategy

Naive strategy:

1. Build one AS containing all triangles.
2. Run nearest-hit.
3. Count the returned primitive.
4. Advance `minDistance` just beyond the hit distance.
5. Repeat until no hit.

This is not exact for RTDL hit count in the general case.

Reason: if two or more triangles are hit at the same distance, advancing
`minDistance` past the first hit can skip the remaining same-distance triangles.
If the epsilon is too small, the same primitive can be returned repeatedly. If
the epsilon is too large, near-distance hits can be skipped.

Therefore a pure distance-advance loop cannot replace the current exact path.

## Implementable Candidate

The first implementable candidate is a **masked chunked nearest-hit path**:

1. Partition triangles into chunks of at most 32 primitives.
2. Build one MPS triangle AS per chunk, not one AS per triangle.
3. Assign each primitive a unique one-bit mask within its chunk.
4. Use `MPSRayDataTypeOriginMaskDirectionMaxDistance` for rays.
5. Enable `MPSRayMaskOptionPrimitive`.
6. For each chunk, initialize each ray mask to all chunk bits set.
7. Run nearest-hit with primitive index.
8. When a ray hits primitive `p`, increment that ray's count and clear bit `p`
   from that ray's mask.
9. Repeat for that chunk until no rays hit or all chunk bits are cleared.
10. Move to the next chunk.

This preserves same-distance hits inside a chunk because excluding a hit
primitive is mask-based, not distance-epsilon-based.

It reduces acceleration-structure rebuild count from `triangle_count` to
`ceil(triangle_count / 32)`.

## Epsilon Policy

The masked chunked candidate does not rely on distance advancement for
correctness. It should keep the same ray origin and finite `maxDistance` and use
mask clearing to avoid double-counting.

No `minDistance` epsilon should be used for correctness in the first
implementation. If a defensive `minDistance` is needed for an MPS-specific
infinite-loop bug, it must be:

```text
next_min = nextafterf(hit_distance, +infinity)
```

and the implementation must still use primitive-mask clearing as the primary
double-count prevention mechanism.

## Pass Ceiling

For each chunk:

```text
max_passes_per_chunk = min(32, chunk_triangle_count)
```

Total pass ceiling:

```text
max_total_passes = sum(max_passes_per_chunk for all chunks)
                 = triangle_count
```

This is the same worst-case hit depth as the current exact path, but with far
fewer AS builds. A pass that returns no hits for every ray terminates the chunk
early.

## Expected Performance Shape

Best case:

- many rays miss most chunks,
- early no-hit termination reduces passes,
- AS builds drop by up to 32x compared with the current one-triangle path.

Worst case:

- every ray hits every primitive,
- each chunk needs 32 nearest-hit passes,
- total dispatch count can still approach `triangle_count`.

Even in the worst case, AS rebuilds should still be lower than the current path.
Dispatch count may remain high.

## Fallback Rule

If the masked chunked path does not match CPU reference across dense,
same-distance, near-distance, miss, and mixed-hit fixtures, it must not replace
the current exact path.

If parity fails or performance is worse, v0.9.2 should keep the current exact
per-triangle path and record the masked chunked attempt as a technical stop for
v0.9.3.

## Required Test Fixtures

Goal597 implementation must include:

- one ray hitting zero triangles,
- one ray hitting one triangle,
- one ray hitting multiple separated triangles,
- one ray hitting stacked/co-planar triangles at the same distance,
- one ray hitting more than 32 triangles to force multiple chunks,
- invalid ray handling consistent with the existing path,
- parity against `ray_triangle_hit_count_cpu`.

## Codex Verdict

ACCEPT this as the only safe first implementation candidate. The naive
single-AS distance-advance approach is not exact enough for RTDL. The masked
chunked approach is more complex, but it is the first candidate that has a
credible exactness story under the MPS API.
