# Goal4845 Status - Section 5.2 LSI, County x Zipcode

Date: 2026-07-01

## Scope

Goal4845 is the Section 5.2 LSI comparison between AuthorPatch RayJoin and RTDL v2.14-line OptiX primitives.

This status covers the first controlled pair:

- Dataset: County x Zipcode same-source CDBs.
- Workload: LSI only.
- Baseline: AuthorPatch `query_exec -query=lsi -mode=rt`.
- RTDL route: OptiX segment-pair intersection count under `rayjoin_lsi` predicate mode.
- Not covered here: PIP, overlay, Section 5.7, Embree, whole-paper speedup claims.

## Key facts

AuthorPatch original command:

```text
poly1 = dtl_cnty_Point.cdb
poly2 = USAZIPCodeArea_Point.cdb
mode = rt
query = lsi
xsect_factor = 0.1
enlarge = 3.5
```

Observed AuthorPatch count:

```text
Intersections: 961165
```

The reversed AuthorPatch command:

```text
poly1 = USAZIPCodeArea_Point.cdb
poly2 = dtl_cnty_Point.cdb
```

Observed reversed AuthorPatch count:

```text
Intersections: 965844
```

This proved that Section 5.2 LSI direction matters and that RTDL's prepared-left route must be mapped carefully to the AuthorPatch `poly1`/`poly2` semantics.

## What went wrong during debugging

I initially spent time on count-level and timing-level probes before dumping the pair sets. That was inefficient.

The correct debugging method was:

1. Dump AuthorPatch LSI pair IDs.
2. Dump RTDL LSI pair IDs under the comparable direction.
3. Compute a set difference.
4. Build a minimal synthetic reproduction for the exact missing pair.
5. Patch only a generic candidate-generation defect if the minimal case proves one.

The earlier FMA-vs-multiply-add hypothesis was tested and rejected:

- Changing RayJoin LSI scaling from `std::fma(x, rx, delta)` to `x * rx + delta` changed the RTDL count from `961164` to `961168`.
- That did not match AuthorPatch `961165`.
- The hypothesis was reverted.

## Pair-level diagnosis

After pair dumps, the comparable RTDL route had:

```text
RTDL count before fix: 961164
AuthorPatch count:     961165
missing_count:         1
extra_count:           0
```

The missing AuthorPatch pair was:

```text
county edge zero-based id: 8480674
zipcode edge zero-based id: 5748176
```

The corresponding CDB edge records were:

```text
county file edge id 8480675
8480675 2 16961349 16961350 3008 3010
-7.8550846000e+01 3.9124448000e+01
-7.8552278000e+01 3.9125105000e+01

zipcode file edge id 5748177
5748177 2 11496353 11496354 8079 8091
-7.8551014500e+01 3.9124525200e+01
-7.8551021500e+01 3.9124528600e+01
```

A small diagnostic implementing the AuthorPatch `intersect_test` contract showed that this pair is a true hit under the author-style scaled integer predicate.

## Root cause

The zipcode edge is extremely short. Under the full County x Zipcode coordinate scale, both endpoints collapse to the same `float32` point for the OptiX ray candidate stage.

AuthorPatch computes ray ordering and direction from higher-precision endpoint values before the final float conversion. RTDL's prepared segment-pair route had already converted endpoints to `GpuSegment` float endpoints before ray ordering/direction. For this edge:

- exact/scaled segment: nonzero length
- float endpoint segment: collapsed to one point
- RTDL ray candidate: zero-length / wrong ordering basis
- exact predicate: never reached

So the defect was not Python, Numba, PIP, or overlay logic. It was a conservative-candidate-generation bug for nonzero exact segments that collapse in float candidate space.

## Product repair

In `src/native/optix/rtdl_optix_workloads.cpp`, the RayJoin LSI predicate-mode raygen paths now:

1. Use `RayjoinLsiScaledSegment` exact/scaled endpoints to decide the author-style edge direction.
2. If the float endpoint segment collapses but the exact/scaled segment is nonzero, extend the candidate ray by one `nextafterf` step in the exact direction.
3. Keep the exact `rayjoin_lsi_intersection_device` predicate as the final hit decision.

This is not a hard-coded RayJoin output patch. It is a conservative candidate-generation repair: exact geometry still decides whether the pair is counted.

## Validation

### Synthetic gate

Synthetic input:

- the one missing county edge
- the one missing zipcode edge
- two zero-length dummy segments preserving the full dataset scale

Before repair:

```text
direct count  = 0
grouped count = 0
expected      = 1
```

After repair:

```text
direct count  = 1
grouped count = 1
expected      = 1
```

### Full County x Zipcode gate

After repair:

```json
{
  "count": 961165,
  "expected_authorpatch_original_count": 961165,
  "delta_vs_authorpatch_original": 0,
  "prepare_sec": 4.9012961611151695,
  "count_wall_sec": 3.4825050979852676,
  "load_sec": 166.4394359961152
}
```

The Section 5.2 County x Zipcode LSI correctness gate now matches AuthorPatch exactly on count.

## Performance interpretation

No broad performance claim is authorized from this status.

The count hot path is now measurable, but the Python/CDB loading path dominates the current script wall time:

```text
load_sec ~= 166 s
native count_wall_sec ~= 3.48 s
```

Future Section 5.2 runs must separate:

- data loading / CDB preparation,
- RTDL prepare/build,
- native LSI query/count,
- AuthorPatch query time.

The current evidence is a correctness gate and a bounded timing smoke, not a final performance comparison.

## Exposed issues to record

1. Pair-level diff should have been used earlier. Count-only probing without pair diff wasted time.
2. Full CDB reloads are too expensive for debugging. Future work must use persistent runners, cached arrays, or minimal synthetic reproductions.
3. RTDL's RayJoin LSI candidate ray generation was not conservative for nonzero exact segments that collapse in float space.
4. `count_prepared_left` returned `OptiX error: Invalid value` on this large prepared-left route; the direct/grouped routes worked. This should remain recorded as a separate route robustness issue.
5. `/workspace` quota prevented large temporary dump writes; use `/tmp` for transient pair dumps and only persist compact summaries.

## Next steps

1. Add or preserve a regression test for the collapsed-float-ray synthetic pair.
2. Run the same Section 5.2 LSI AuthorPatch-vs-RTDL process on the next available dataset pair.
3. Keep Section 5.2 LSI separate from Section 5.7 overlay; do not use LSI count correctness as overlay correctness.
4. Only after correctness gates pass should performance tables be produced.
