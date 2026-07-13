# Call For Review - Goal5013 Point-Location Locator Prepare Cost Probe

Date: 2026-07-05

Please review:

```text
history/internal_docs/goal5013_point_location_locator_prepare_result_2026-07-05.md
```

Artifact:

```text
history/internal_docs/goal5013_point_location_locator_prepare_artifacts_2026-07-05/rtdl_goal5013_point_location_locator_prepare.json
```

Probe:

```text
history/internal_docs/goal5013_point_location_locator_prepare_probe.py
```

## Context

Goal5012 left the prepared-base / same-domain distinct-query overlay body at
about `~1.22s/query`.  The largest remaining single cost was preparing the
query-specific left point-location locator, about `~0.445s/query`.

Goal5013 tests whether that cost is a first-call artifact, a reusable prepared
asset, or a per-input locator build floor.

## Review Questions

1. Does the same-input re-prepare evidence show that only the first call is
   unusually expensive, while the steady cost remains about `~0.46s`?
2. Do the distinct same-domain variants show that each distinct left geometry
   still pays about `~0.47s` to prepare its point-location locator?
3. Does the segment-count scaling evidence support classifying this as an
   input-size-dependent locator construction floor?
4. Is it correct to say existing prepared query-point reuse does not remove
   this cost, because the cost belongs to preparing the locator, not preparing
   the query points?
5. Does the report avoid claiming 10x, zero-copy, full device-resident
   execution, or author-performance parity?
6. Does the report preserve the generic-system boundary by refusing a
   RayJoin-specific point-location locator shortcut?
7. Should the current line close with
   `completed_goal5013_locator_prepare_is_steady_segment_scaled_floor`, unless
   the owner explicitly opens a larger generic RTDL point-location locator
   construction product goal?

Requested verdict label:

```text
approve_goal5013_locator_prepare_is_steady_segment_scaled_floor
```
