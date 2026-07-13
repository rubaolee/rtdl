# RTDL v2.14.3 Internal Release Packet

Date: 2026-07-05

Status:

```text
internal_release_staged
```

This is an internal release packet for the v2.14.3 RayJoin writer-free binary
operator performance line.  It is not an external/public release announcement.

## Release Scope

v2.14.3 stabilizes the RayJoin paper-reproduction engineering app after the
writer-free binary operator and prepared-query performance work.

The release scope is:

- Section 5.7 writer-free binary overlay route.
- Top4 County x Zipcode representative performance evidence.
- Prepared-base / same-domain distinct-query measurement evidence.
- Generic RTDL route boundaries for LSI and point-location front doors.
- Internal reports, probes, JSON artifacts, and tests needed to reproduce the
  performance claims.

The release scope is not:

- full author-performance parity;
- a 10x performance release;
- full device-resident or zero-copy execution;
- same-input replay as query-many;
- a public claim that top4 author ratio was measured;
- a promise that the current app route reaches `~0.42s/query`.

## Canonical Numbers

The canonical number file is:

```text
history/internal_docs/v2_14_3_rayjoin_performance_canonical_numbers_2026-07-05.json
```

Canonical numbers:

```text
OS-process-cold CLI one-shot:        ~11.6s median, noisy, disclose only
warm-process fresh fast-pack:        ~4.22s, primary v2.14.3 number
prepared same-domain distinct query: ~1.22s/query, best measured prepared route
left locator prepare floor:          ~0.46-0.47s/query
```

The internal release label is:

```text
v2_14_3_rayjoin_performance_stabilized__fresh_4_22s__prepared_same_domain_1_22s__10x_not_achieved
```

## Main Engineering Result

v2.14.3 separates the paper-text reproduction route from the writer-free binary
operator route.

The important product result is not a win over the author implementation.  The
important result is a stable, bounded RTDL app route:

```text
generic RTDL primitives + app-layer RayJoin workflow + measured performance boundaries
```

The route is useful because it keeps the RTDL core generic while giving the
RayJoin app a binary intermediate form that avoids the paper-text writer when
the overlay is used as a pipeline operator.

## Performance Interpretation

### Product-facing route

The product-facing v2.14.3 number is:

```text
~4.22s warm-process fresh fast-pack top4 overlay
```

This number assumes a warm long-lived process.  It is not a cold CLI one-shot
number.

### Prepared-query route

The best prepared-base / same-domain distinct-query body is:

```text
~1.22s/query
```

This is a real route with distinct query batches.  It is not same-input replay.

### Why 10x is not claimed

The requested 10x target from `~4.22s` would require about:

```text
~0.42s/query
```

Goal5013 showed that the left point-location locator prepare cost alone is
about:

```text
~0.46-0.47s/query
```

Therefore the current app-layer path cannot credibly claim 10x.  Reaching that
target requires a larger generic RTDL product effort around reusable or resident
directed point-location locator construction.

## Stopped Track

Device-resident carrier is stopped as a v2.14.3 performance track.

Reason:

```text
fast-pack fresh:        ~4.22s
device-resident fresh:  ~5.0s
```

It remains allowed as experimental architecture behind explicit flags, but it
is not the v2.14.3 performance headline.

## Internal Evidence Inventory

The v2.14.3 evidence chain includes:

- Goal4955-4997: binary route construction, LSI/PIP columnar paths, final
  bounded matrix setup.
- Goal4998-5005: device-resident carrier experiment, owner correction, stopped
  track decision.
- Goal5006-5013: 10x preconditions, true query-many checks, point-location reuse
  checks, locator prepare floor.
- Goal5014: final performance stabilization closeout.

Important artifacts:

```text
history/internal_docs/goal5014_v2_14_3_performance_stabilization_closeout_2026-07-05.md
history/internal_docs/v2_14_3_rayjoin_performance_canonical_numbers_2026-07-05.json
history/internal_docs/goal5013_point_location_locator_prepare_result_2026-07-05.md
history/internal_docs/goal5010_5012_point_location_query_many_result_2026-07-05.md
history/internal_docs/goal5009_distinct_query_many_overlay_body_result_2026-07-05.md
history/internal_docs/goal5008_distinct_query_many_lsi_regime_result_2026-07-05.md
history/internal_docs/goal5005_owner_directive_fresh_headline_and_device_resident_gate_2026-07-05.md
```

## Cleanup State

Transient cleanup performed:

```text
__pycache__ directories removed: 0 in the final cleanup pass
```

Public-surface leak scan:

```text
README.md docs examples tutorials Paper-reproduction-apps/rayjoin-paper/README.md
patterns: Goal[0-9]+, Claude, Gemini, Antigravity, call_for_review, verdict,
          V3.0, V4.0, exp-project, internal_docs
result: no matches
```

Working tree state:

```text
dirty_by_design_for_internal_release
```

The dirty tree includes project state:

- v2.14.3 app route code;
- native/runtime support code;
- tests;
- probes;
- reports;
- JSON artifacts;
- review records.

These are not transient cache and should not be deleted during cleanup.

## Internal Release Boundary

Allowed internal statement:

```text
v2.14.3 internally stabilizes the RayJoin writer-free binary route at about
4.22s warm-process fresh top4 overlay and about 1.22s/query for prepared-base,
same-domain distinct-query batches.  The 10x target is not achieved; the current
floor is point-location locator construction.
```

Forbidden statement:

```text
v2.14.3 reaches author parity, 10x, full zero-copy, full device-resident
execution, or measured top4 author ratio.
```

## Recommended Next Product Decision

Do not continue v2.14.3 app-layer micro-optimization.

If performance work continues, make it a new generic RTDL product goal:

```text
resident_or_reusable_directed_point_location_locator_construction
```

That next goal must be generic, must include a non-RayJoin validation shape, and
must keep fresh / prepared / cold-process regimes separate.

## Final Internal Release Label

```text
internal_release_v2_14_3_staged_with_bounded_rayjoin_performance
```
