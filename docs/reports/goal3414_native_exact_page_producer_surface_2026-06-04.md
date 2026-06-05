# Goal3414 - Native Exact Pair-Column Page Producer Surface

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3413 made paged pair-column recovery explicit and reusable, but the page
itself was still produced by Python slicing a point sequence before calling the
existing exact device-column bridge.

Goal3414 adds a narrow native page producer surface:

```text
rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_page_2d
```

The Python method is:

```python
prepared.exact_device_columns_page(
    points,
    page_start=...,
    page_count=...,
    max_rows=...,
)
```

This lets a caller pass one full packed point buffer plus an explicit page range
into the native ABI. It is the first migration step from Python-windowed
orchestration toward a real native paged stream contract.

## Boundary

This is not yet the full native paged stream ABI. It does not implement a page
plan handle, a page release function, page-local lifecycle callbacks, automatic
retry, hidden dispatch, device-only exact predicates, true zero-copy, public
speedup claims, RT-core speedup claims, RayJoin reproduction claims, or release
authorization.

The exact rows still come from the existing host-refined bridge before being
uploaded to device pair columns. Goal3414 only moves page selection into the
native entry point.

## Next Target

The remaining native graduation shape is:

```text
prepare -> page_plan -> produce_page(page_index) -> consume_page -> release_page
```
