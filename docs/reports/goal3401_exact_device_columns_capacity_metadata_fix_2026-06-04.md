# Goal3401 - Exact Device Columns Capacity Metadata Fix

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3399's review correctly noticed that the exact device-column bridge could be
misread as allocating the full point-by-shape worst-case capacity. The successful
bridge path actually allocates only the exact relation rows after host refinement.
Goal3401 fixes the native status metadata so successful streams report allocated
capacity, not worst-case candidate capacity.

## Change

`rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_2d` now
sets:

```text
capacity = 0
```

for empty successful streams, and:

```text
capacity = exact_count
```

for non-empty successful exact streams. The overflow path still reports the
caller-requested `max_rows`, because that is the bounded capacity that failed
closed.

## Evidence

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit:
`3b09c58ab9750df289f4991437803bd67f8f5a53`

Artifacts:

- `docs/reports/goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json`
- `docs/reports/goal3398_full_br_county_exact_device_columns_2026-06-04.json`
- `docs/reports/goal3400_exact_device_columns_overflow_probe_2026-06-04.json`

| Probe | Exact rows | Reported capacity | Overflow | Expected |
| --- | ---: | ---: | --- | --- |
| 4096-chain slice | 11316 | 11316 | false | allocated exact rows |
| Full `br_county.cdb` | 47262 | 47262 | false | allocated exact rows |
| Forced `max_rows=100` | 11316 | 100 | true | caller bounded capacity |

The old misleading values are no longer present in the successful artifacts:

- 4096 slice no longer reports `15409152` capacity.
- Full `br_county.cdb` no longer reports `259756500` capacity.

## Boundary

This fixes metadata accuracy for the existing host-refined exact-device-column
bridge. It does not implement chunked overflow recovery, a device-only exact
predicate, true zero-copy, hidden dispatch, public speedup claims, RT-core
speedup claims, RayJoin paper reproduction claims, or release authorization.
