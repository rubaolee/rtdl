# Goal5013 - Point-Location Locator Prepare Cost Probe

Date: 2026-07-05

## Purpose

Goal5012 reduced the prepared-base / same-domain distinct-query overlay body from
about `1.48s/query` to about `1.22s/query` by reusing the constant right-vertex
query-point batch.  The remaining largest single cost was preparing the
query-specific left point-location locator:

```text
prepare left point-location locator ~= 0.445s/query
```

Goal5013 asks whether that cost is:

- a first-call / JIT artifact;
- reusable through existing prepared query-point assets;
- an input-size-dependent locator build floor that must be paid for each
  distinct left geometry.

This is a measurement goal only.  It does not add RTDL core semantics and does
not change the RayJoin app route.

## Method

Probe:

```text
history/internal_docs/goal5013_point_location_locator_prepare_probe.py
```

POD artifact:

```text
history/internal_docs/goal5013_point_location_locator_prepare_artifacts_2026-07-05/rtdl_goal5013_point_location_locator_prepare.json
```

Input:

```text
top4 County x Zipcode
left segments:  1,705,027
left points:    1,706,639
right segments: 9,982,960
right points:   9,993,104
```

The probe ran three checks:

1. Prepare the same left locator repeatedly.
2. Prepare three distinct same-domain left query variants.
3. Prepare prefix-sized locators at 12.5%, 25%, 50%, and 100% of left segments.

## Results

### Same Input Re-Prepare

```text
iteration 1: 1.550688s
iteration 2: 0.459273s
iteration 3: 0.460924s
iteration 4: 0.489678s

after-first median: 0.460924s
```

The first prepare includes a large one-time cost, but after that the repeated
same-geometry locator prepare remains about `0.46-0.49s`.  Therefore the
steady cost is not merely first-call JIT.

### Distinct Same-Domain Query Variants

```text
batch 1: 0.459797s
batch 2: 0.484862s
batch 3: 0.473011s

median: 0.473011s
```

Distinct same-domain left geometries pay the same steady locator prepare cost
as repeated same input after first-call warmup.

### Segment-Count Scaling

```text
12.5% segments: 213,128   -> median 0.037734s
25.0% segments: 426,257   -> median 0.098345s
50.0% segments: 852,514   -> median 0.220020s
100%  segments: 1,705,027 -> median 0.461880s
```

The cost scales with locator segment count.  That strongly indicates a
per-locator construction / packing / acceleration-structure preparation floor,
not a small Python bookkeeping artifact.

## Interpretation

Goal5013 answers the immediate question:

```text
The ~0.445-0.47s/query left point-location locator prepare cost is real,
steady after first-call warmup, and scales with input segment count.
```

Existing prepared query-point reuse does not remove this cost, because the cost
belongs to preparing a new locator for a distinct left geometry, not to preparing
the right-side query points.

This means the current prepared-base / same-domain query-many route has a
durable per-query floor:

```text
LSI query                      ~0.12-0.14s
left point-location locator    ~0.46-0.47s
remaining downstream           ~0.55-0.60s
current body                   ~1.22s/query
```

The route is about `3.4x` faster than the `~4.22s` warm-process fresh fast-pack
baseline, but it is not on a credible path to `0.42s/query` without removing or
fundamentally changing the per-query locator build.

## Claim Boundary

Authorized:

- `prepare_left_point_location_locator` is a measured, steady, segment-count
  dependent cost on this top4 workload.
- Existing prepared query-point reuse is insufficient to remove this cost.
- The current prepared-base / same-domain distinct-query route remains around
  `~1.2s/query`, not `~0.42s/query`.

Not authorized:

- Claiming the route is close to a 10x target.
- Claiming full device-resident or zero-copy execution.
- Claiming this cost is just a first-call artifact.
- Promoting a RayJoin-specific locator shortcut into RTDL core.

## Next Decision

There are only two honest next directions:

1. Accept `~1.2s/query` as the v2.14.3 prepared-base / same-domain query-many
   floor and close this performance line for now.
2. Open a larger generic RTDL product goal for reusable / resident directed
   point-location locator construction.  That goal must be generic, measured on
   a non-RayJoin shape as well, and should not be sold as a small app-level
   optimization.

Recommended exit label:

```text
completed_goal5013_locator_prepare_is_steady_segment_scaled_floor
```
