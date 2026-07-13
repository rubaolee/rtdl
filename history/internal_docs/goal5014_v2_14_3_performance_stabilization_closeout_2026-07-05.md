# Goal5014 - v2.14.3 RayJoin Performance Stabilization Closeout

Date: 2026-07-05

## Purpose

This closeout stabilizes the v2.14.3 RayJoin writer-free binary-overlay
performance line after Goals 4997-5013.

The goal is not to create another optimization target.  The goal is to freeze
the honest performance state, clean up the measurement framing, and prevent the
next round from reusing favorable regimes as product results.

## Canonical Performance State

The v2.14.3 performance story has three valid regimes.

### 1. OS-process-cold CLI one-shot

Observed in Goal5005:

```text
~11.6s median, high variance
```

Meaning:

- This is what a user may see when launching a fresh Python process for a single
  run.
- It includes Python startup, CUDA/OptiX runtime setup, first-call compilation,
  and route execution.
- The Goal5005 session was noisy, so this number should be disclosed as
  cold-process evidence, not used as a precise benchmark headline.

Allowed claim:

```text
Cold one-shot CLI can be much slower than the warmed route; observed median was
about 11.6s in a noisy POD session.
```

### 2. Warm long-lived-process fresh overlay

Canonical v2.14.3 headline:

```text
~4.22s per fresh top4 overlay
```

Meaning:

- Same top4 County x Zipcode workload.
- Warm process, but a fresh overlay computation.
- Fast-pack route, not the device-resident-carrier experiment.
- Includes fresh LSI producer cost.
- Excludes the final paper-text writer because this is the writer-free binary
  operator route.

This is the main v2.14.3 product-facing performance number.

Allowed claim:

```text
The v2.14.3 writer-free binary route runs the top4 representative overlay in
about 4.22s per fresh overlay in a warm long-lived process.
```

Forbidden claim:

```text
Do not call 4.22s a cold CLI one-shot result.
Do not compare it to an author baseline unless the same top4 author baseline is
measured.
```

### 3. Prepared-base / same-domain distinct-query route

Best measured state after Goal5012 and Goal5013:

```text
~1.22s/query
```

Meaning:

- Prepared right/base.
- Same scale/domain.
- Distinct query batches.
- Reuses the constant right-vertex query-point batch.
- Still pays the query-specific left point-location locator construction cost.

Goal5013 established the main remaining floor:

```text
left point-location locator prepare ~= 0.46-0.47s/query
```

Allowed claim:

```text
For prepared-base / same-domain distinct-query batches, the best measured body
is about 1.22s/query, roughly 3.4x faster than the 4.22s warm-process fresh
baseline.
```

Forbidden claim:

```text
Do not call this 10x.
Do not call it author parity.
Do not call it full device-resident or zero-copy.
Do not use same-input replay numbers as query-many evidence.
```

## Stopped Performance Tracks

### Device-resident carrier as v2.14.3 performance track

Status:

```text
stopped_for_v2_14_3
```

Reason:

- It was slower in the fresh product regime:

```text
fast-pack fresh:          ~4.22s
device-resident fresh:    ~5.0s
```

- Its advantage appeared only in prepared replay / diagnostic regimes.
- Payoff was not demonstrated on a true product workload.

Allowed use:

- Keep behind explicit flags as experimental architecture work.
- Reopen only after a real payoff gate is met:

```text
distinct-query product regime, same structural anchors, end-to-end faster than
fast-pack.
```

### 10x target

Status:

```text
not_achieved_in_v2_14_3
```

Reason:

- The original 10x target from `~4.22s` means `~0.42s/query`.
- Goal5013 showed a stable locator prepare floor of about `~0.46-0.47s/query`
  by itself.
- Therefore `~0.42s/query` is not credible on the current app-layer path.

Allowed conclusion:

```text
v2.14.3 reaches about 3.4x in the prepared-base / same-domain route, not 10x.
```

## What v2.14.3 Actually Improved

The useful work was not fake; it just has a bounded result.

1. It separated paper-text reproduction from writer-free binary overlay.
2. It established the warm-process fresh fast-pack route as the canonical
   product-facing performance path.
3. It proved real prepared-base / same-domain query-many behavior for LSI.
4. It reused right-side query points and reduced full overlay query-many body
   from about `~1.48s/query` to about `~1.22s/query`.
5. It identified the next true floor: query-specific left point-location locator
   construction.

## Current Bottleneck

The current bottleneck is not LSI replay, not text writer, and not a trivial
Numba boundary.

The current bottleneck for the best prepared route is:

```text
per-query left point-location locator construction
```

Measured by Goal5013:

```text
same input after first prepare:       ~0.461s
distinct same-domain median:          ~0.473s
100% segment-prefix median:           ~0.462s
50% segment-prefix median:            ~0.220s
25% segment-prefix median:            ~0.098s
12.5% segment-prefix median:          ~0.038s
```

Interpretation:

```text
This is a segment-count-scaled locator construction floor.
```

## Cleanup Decision

Pure transient artifacts may be removed:

- `__pycache__/`
- Python bytecode
- temporary scratch files

Project evidence must be retained:

- Goal reports
- call-for-review files
- probes
- JSON artifacts
- tests
- app code

The current reports and probes are project state, not cache.

## Release/Closeout Recommendation

Close the v2.14.3 RayJoin performance line with this label:

```text
v2_14_3_rayjoin_performance_stabilized__fresh_4_22s__prepared_same_domain_1_22s__10x_not_achieved
```

Recommended owner-facing statement:

```text
v2.14.3 stabilizes the RayJoin writer-free binary route at about 4.22s for
warm-process fresh top4 overlay and about 1.22s/query for prepared-base,
same-domain distinct-query batches.  The 10x target is not achieved in this
version because the remaining point-location locator construction cost is a
steady, segment-count-scaled floor.
```

## Next Product Decision

Do not continue app-level micro-optimization in v2.14.3.

If the owner wants to continue toward 10x, open a new generic RTDL product goal:

```text
resident_or_reusable_directed_point_location_locator_construction
```

That future goal must:

- stay generic;
- include a non-RayJoin validation shape;
- measure fresh and prepared regimes separately;
- prove correctness before performance;
- avoid RayJoin-specific core shortcuts.
