# Goal 110 Segment-Polygon-Hitcount Comparison And Significance

Date: 2026-04-05
Author: Codex
Status: accepted_local_supporting_report_pending_review

## Purpose

This report closes two non-host obligations from the Goal 110 acceptance rule:

- the explicit technical comparison against `lsi`
- the significance proof beyond parity closure

It does not replace the still-required capable-host Embree/OptiX evidence.

## Why `segment_polygon_hitcount` is the better first v0.2 closure target than `lsi`

Goal 110 is not trying to prove that `segment_polygon_hitcount` is more
important than `lsi` in every setting. It is choosing the better first v0.2
workload-family closure target.

For that narrower question, `segment_polygon_hitcount` is the stronger choice.

### 1. The output contract is cleaner

`segment_polygon_hitcount` emits:

- `segment_id`
- `hit_count`

That is a compact integer output contract. The correctness question is:

- did each segment receive the right count?

By contrast, `lsi` usually pulls the project back into a broader pairwise join
surface:

- which pairs intersect
- how candidate completeness is guaranteed
- how large result sets behave

That makes `lsi` valuable, but it is a harder first v0.2 closure target.

### 2. The parity surface is smaller and easier to audit

For `segment_polygon_hitcount`, parity means exact equality on:

- `segment_id`
- `hit_count`

There is no need to explain:

- pair ordering issues
- pair-materialization growth
- pair deduplication semantics
- broader join-style reporting

This makes the family easier to close honestly as a first post-v0.1 expansion.

### 3. It still fits the Goal 108 charter

The Goal 108 workload charter allows one new in-scope spatial filter/refine
family for v0.2. `segment_polygon_hitcount` satisfies that charter because it
is:

- a real spatial workload
- not a novelty demo
- useful as a screening/filter primitive
- clearly beyond the v0.1 RayJoin-heavy `pip` story

It expands RTDL without reopening the whole RayJoin-facing `lsi` surface.

### 4. It reduces semantic ambiguity for the first closure

The current semantic contract for `segment_polygon_hitcount` is already explicit
in tests:

- endpoint inside polygon counts as a hit
- boundary touch counts as a hit
- edge crossing counts as a hit
- zero-hit segments remain in output
- overlapping polygons count independently

That contract is narrower and easier to review than broad `lsi` closure as a
first v0.2 family.

### 5. It fits the current honesty boundary better

Both `segment_polygon_hitcount` and the current local `lsi` surface still sit
under the repo's audited local `native_loop` honesty boundary rather than a
cleanly demonstrated BVH-backed maturity story. That makes it even more
important to choose a first v0.2 family whose closure claim can stay narrow and
defensible.

`segment_polygon_hitcount` is the better fit for that.

## Significance proof

Goal 110 requires one significance proof beyond simple parity closure.

The accepted alternatives were:

- at least `4x` probe/build scale over the basic county fixture
- or a materially denser output-count regime than the basic county fixture

The current derived case satisfies the first criterion directly.

### Basic fixture

Dataset:

- `tests/fixtures/rayjoin/br_county_subset.cdb`

Observed under the Python reference path:

- segments: `10`
- polygons: `2`
- output rows: `10`
- total hit count: `11`
- nonzero rows: `10`

### Derived case

Dataset:

- `derived/br_county_subset_segment_polygon_tiled_x4`

Observed under the Python reference path:

- segments: `40`
- polygons: `8`
- output rows: `40`
- total hit count: `44`
- nonzero rows: `40`

### Conclusion

The derived case is an exact `4x` scale-up over the basic fixture on both:

- probe scale
- build scale

Specifically:

- segments: `10 -> 40`
- polygons: `2 -> 8`

So Goal 110's significance requirement is already satisfied by the accepted
derived dataset through the explicit `4x` scale criterion, even before any
additional density claim is needed.

## Final conclusion of this report

This report establishes two things:

1. `segment_polygon_hitcount` is the better first v0.2 workload-family closure
   target than reopening broad `lsi`
2. the current derived county-tiled case already satisfies Goal 110's required
   significance proof via exact `4x` scale over the basic county fixture

So after this report, the remaining Goal 110 blockers are no longer conceptual.
They are:

- capable-host Embree evidence
- capable-host OptiX evidence
- prepared-path evidence on those hosts
- final honesty framing for the closed package
