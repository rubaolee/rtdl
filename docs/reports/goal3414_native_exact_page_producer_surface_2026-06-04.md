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
into the native ABI. The probe prepares that packed point buffer once and reuses
it across every native page call. It is the first migration step from
Python-windowed orchestration toward a real native paged stream contract.

## Boundary

This is not yet the full native paged stream ABI. It does not implement a page
plan handle, a page release function, page-local lifecycle callbacks, automatic
retry, hidden dispatch, device-only exact predicates, true zero-copy, public
speedup claims, RT-core speedup claims, RayJoin reproduction claims, or release
authorization.

The exact rows still come from the existing host-refined bridge before being
uploaded to device pair columns. Goal3414 only moves page selection into the
native entry point.

## Pod Evidence

The probe artifact is:

`docs/reports/goal3414_native_exact_page_producer_probe_2026-06-04.json`

It was produced on commit `a50494bc` with an NVIDIA RTX A5000 and driver
`580.126.09`.

| Measure | Value |
| --- | ---: |
| points | 16545 |
| shapes | 15700 |
| page size | 2048 |
| pages | 9 |
| overflowed pages | 9 |
| retried pages | 9 |
| host exact rows | 47262 |
| device grouped source rows | 47262 |
| host groups | 16476 |
| device groups | 16476 |
| missing/extra/mismatched groups | 0/0/0 |

Every page was produced through the native page symbol with explicit
`page_start` and `page_count`, using one reused packed point buffer. The native
page boundary still records that no page-plan handle, page release function, or
device-only exact predicate exists yet.

## Next Target

The remaining native graduation shape is:

```text
prepare -> page_plan -> produce_page(page_index) -> consume_page -> release_page
```
