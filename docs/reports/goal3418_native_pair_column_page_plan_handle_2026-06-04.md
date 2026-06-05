# Goal3418 - Native Pair-Column Page Plan Handle

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3417 introduced a runtime page-plan object. Goal3418 adds the first native
page-plan handle:

```text
rtdl_optix_prepare_point_closed_shape_membership_exact_device_columns_page_plan_2d
rtdl_optix_produce_point_closed_shape_membership_exact_device_columns_page_2d
rtdl_optix_destroy_point_closed_shape_membership_exact_device_columns_page_plan_2d
```

The Python surface is:

```python
native_plan = prepared.exact_device_columns_native_page_plan(
    points,
    page_size=2048,
    initial_max_rows=100,
)
page = native_plan.produce_page(0)
native_plan.close()
```

The native plan owns a copied host point buffer and page metadata, so page
production no longer receives the point buffer on each call.

## Boundary

This is still not the final device-resident paged stream ABI. The native plan
does implement a handle and destroy function, but it still does not implement:

- device-only exact predicates,
- page-local device lifecycle callbacks,
- automatic retry,
- hidden dispatch,
- true zero-copy,
- public speedup claims,
- RT-core speedup claims,
- RayJoin reproduction claims,
- release authorization.

The exact rows still come from the existing host-refined exact bridge before
upload to device pair columns.

## Pod Probe

The probe script is:

`scripts/goal3418_native_page_plan_handle_probe.py`

The pod artifact will be:

`docs/reports/goal3418_native_page_plan_handle_probe_2026-06-04.json`

It was produced on commit `c0bedc29` with an NVIDIA RTX A5000 and driver
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

The artifact confirms that page production uses the native page-plan handle and
that the native destroy function is present. It also confirms the remaining
boundary: the native plan owns a host point copy and exact predicates are not
device-only yet.

## Next Target

The remaining native graduation shape is narrowed to:

```text
device-resident exact predicate -> page-local consume/release callbacks
```
