# Goal4985 Result: v2.14.3 Final Bounded Performance Matrix

Date: 2026-07-04

## Verdict

```text
completed_v2_14_3_bounded_performance_matrix__fresh_primary_no_author_ratio_on_top4
```

Goal4985 records the final bounded v2.14.3 performance matrix after the Goal4984 correctness/genericity gate.

This matrix is deliberately conservative:

- fresh and warm/diagnostic routes are separated;
- no warm-only headline is used;
- top4 author overlay-compute ratio is not reported because no top4 author compute timing was measured in the current evidence set;
- the County×Soil `0.0421s` author number is not reused as a denominator for top4.

## Workload

```text
top4_county_zipcode_arcgis_same_source
```

Input scale:

| Side | Chains | Points | Edges |
|---|---:|---:|---:|
| County top4 | 1,612 | 1,706,639 | 1,705,027 |
| Zipcode top4 | 10,144 | 9,993,104 | 9,982,960 |

Structural anchors:

```text
lsi_row_count = 428322
xsect_sorted_counts side0/map0 = 428322
xsect_sorted_counts side1/map1 = 428322
vertex_positive_counts side0_in_side1 = 812721
vertex_positive_counts side1_in_side0 = 4527305
downstream descriptor pairs = 15014
downstream total groups = 428974
downstream total point rows = 5902562
```

## Primary Matrix

| Route | Time | Status | Meaning |
|---|---:|---|---|
| RTDL text route, public primitives | `77.37s` route elapsed | correctness anchor | Produces AuthorOfficial-byte-equal paper text output; includes writer/text sink |
| RTDL Numba text route | `70.17s` route elapsed | correctness anchor + app-layer Numba | Byte-equal paper text output; still writer/text dominated |
| Normal writer-free binary route | `7.851s` | superseded baseline | Public LSI rows + device-columnar downstream before exact LSI device columns / fast pack |
| Exact LSI device-column route | `5.904s` | superseded intermediate | Generic pair-id device columns; improves LSI route but still has host pack floor |
| Fast scaled-point pack route | `4.220s` | primary cold/fresh v2.14.3 one-shot evidence | LSI included; carrier may include first-large-call state |
| Current repeated full route, LSI included | median `3.669s` | secondary steady-process evidence | LSI still fresh (`~2.7s`); carrier warm-state `~0.10-0.11s` |
| Prepared/cached LSI replay routes | diagnostic only | not a primary result | Not comparable to fresh overlay; cannot be used as headline |

## Current Best Bounded Claim

The honest v2.14.3 performance claim is:

```text
On the top4 County×Zipcode representative input, the writer-free binary route
improved from 7.851s to 4.220s cold/fresh evidence, with repeated full-route
steady-process runs around 3.62-3.67s while still including LSI production.
```

This is a meaningful improvement over the earlier writer-free top4 route:

```text
7.851s -> 4.220s  = 1.86x improvement
7.851s -> 3.669s  = 2.14x improvement, secondary steady-process evidence
```

But the primary result remains bounded:

```text
v2.14.3 does not claim author-performance parity.
```

## Run Provenance And Matrix Boundary

This matrix is assembled from the validated v2.14.3 evidence chain, not from one single same-POD same-session sweep.

That matters because repeated representative runs showed non-trivial variance. The selected baseline `7.851s` is the lower normal-route baseline from the available evidence, so the `1.86x` improvement is not inflated by choosing a slower baseline. Still, it should be read as a bounded point estimate, not as a statistically stable benchmark distribution.

Release-stage wording must preserve this boundary:

```text
7.851s -> 4.220s is a bounded evidence-chain comparison.
It is not a same-session benchmark suite result.
```

If a publication-grade performance table is required, the normal route, exact-LSI route, fast-pack route, and repeated full route should be rerun in one POD session with the same environment and reported as a fresh distribution.

## Why There Is No Author Ratio For top4

The currently available author overlay-compute timing:

```text
0.0421s
```

belongs to a smaller County×Soil/public-sample context, not the top4 County×Zipcode representative input.

The top4 matrix contains an `author_official` output artifact, but it was reused as a correctness comparator and does not provide an author compute timing for this top4 run.

Therefore Goal4985 explicitly states:

```text
top4 author overlay-compute ratio: not measured
```

This satisfies the closeout review requirement: either measure the top4 author baseline or state its absence. Goal4985 chooses the honest absence statement.

## Fresh/Warm Boundary

Goal4983 policy applies:

- fresh one-shot numbers keep the LSI producer cost;
- warm/diagnostic routes are never headlined alone;
- the invalid `0.000000s` LSI repeat diagnostic is not used;
- prepared/cached replay is useful only as a diagnostic, not as a primary product claim.

Goal4982 evidence shows:

| Component | Current evidence |
|---|---:|
| LSI producer in repeated full route | `2.69-2.76s` |
| grouped carrier warm-state | `0.10-0.11s` |
| native launch inside LSI extended timing | about `0.0023s` |

The remaining major cost is LSI producer setup/ensure work, not native launch and not carrier side-order.

## What v2.14.3 Achieved

v2.14.3 achieved:

- writer-free binary route framing;
- generic exact LSI pair-id device-column route;
- point-location device face-column route;
- fast scaled-point host pack route;
- compiled grouped carrier construction with diagnostic decomposition;
- honest fresh/warm boundary;
- local correctness and genericity gate before matrix.

It did not achieve:

- author-performance parity;
- full device-resident overlay without host CPU carrier construction;
- valid top4 author compute ratio;
- Layer 4 in-traversal fusion;
- a proven product warm route that removes LSI producer from fresh.

## Claim Boundary

Authorized:

- bounded v2.14.3 top4 writer-free binary route matrix;
- `7.851s -> 4.220s` cold/fresh improvement;
- statement that the matrix is assembled from separated validated runs, not one same-session sweep;
- repeated full-route steady-process median around `3.669s`, with LSI included;
- no top4 author ratio measured;
- carrier first-large-call is not the remaining primary floor;
- LSI producer remains the primary unresolved performance target.

Not authorized:

- no author parity claim;
- no warm-only headline;
- no reuse of County×Soil `0.0421s` as top4 denominator;
- no public high-performance claim beyond this bounded internal matrix;
- no claim that prepared replay is fresh overlay;
- no claim that v2.14.3 completed true device-resident overlay.

## Next Step

Proceed to Goal4986:

- update internal/user-facing v2.14.3 release notes and RayJoin paper-reproduction docs;
- keep public docs free of internal goal numbers;
- state the binary route as a bounded paper-reproduction engineering app capability, not a broad RTDL speed claim.
