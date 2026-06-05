# Goal3417 - Runtime Pair-Column Page Plan

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3414 added a native exact page producer with `page_start` and `page_count`.
Goal3417 adds the next runtime layer: an explicit page-plan object that owns one
packed point buffer, lists caller-visible page requests, and exposes
`produce_page(page_index)`.

The new Python surface is:

```python
page_plan = prepared.exact_device_columns_page_plan(
    points,
    page_size=2048,
    initial_max_rows=100,
)

first_page = page_plan.produce_page(0)
```

This is a runtime page plan, not a native page-plan handle.

## Boundary

The plan object records:

- `single_packed_point_buffer_reused = True`
- `native_page_producer_used_by_plan = True`
- `native_page_plan_handle_implemented = False`
- `native_page_release_function_implemented = False`
- `automatic_retry_authorized = False`
- `hidden_dispatch_authorized = False`
- `true_zero_copy_authorized = False`

The exact rows still come from the existing host-refined exact bridge before
upload to device pair columns.

## Pod Probe

The probe script is:

`scripts/goal3417_runtime_page_plan_probe.py`

The pod artifact will be:

`docs/reports/goal3417_runtime_page_plan_probe_2026-06-04.json`

It was produced on commit `15970d94` with an NVIDIA RTX A5000 and driver
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

The artifact confirms that the runtime page plan used one packed point buffer,
called `produce_page(...)`, and preserved all claim boundaries as false.

## Next Target

The remaining native graduation shape is still:

```text
prepare -> page_plan -> produce_page(page_index) -> consume_page -> release_page
```
