# Goal3197: RayJoin Compact Grouped-Count Reference Route

Date: 2026-06-03

## Purpose

Goal3193 added generic compact grouped-count device columns. Goal3195 showed
that this primitive path avoids large exact-row materialization when the app only
needs per-left segment counts.

Goal3197 exposes that primitive as an app-facing reference route in the Spatial
RayJoin benchmark app:

`prepared_optix_compact_grouped_count`

## What Changed

- Added:
  `run_rayjoin_prepared_optix_compact_grouped_count_workload(...)`.
- Wired CLI execution route:
  `--execution-route prepared_optix_compact_grouped_count`.
- Scope is intentionally narrow: LSI workload only.
- The route remaps left segment IDs densely in Python before calling RTDL,
  because the generic grouped-count primitive uses direct-address key capacity.
- It calls:
  `candidate_device_columns(...).grouped_count_by_left_id_compact_device_columns(...)`.
- It can optionally copy compact `(group_key, count)` columns to host for
  validation or display, but the primitive output is CUDA-resident.

## Boundary

This is an app-facing reference route, not a native app-specific extension.

The native engine still sees only:

- generic segment-pair candidate columns,
- generic compact grouped-count columns.

RayJoin workload interpretation and left-ID remapping stay in Python.
For this reference route, left-ID remapping stays in Python.

It does:

- expose a usable reference path for the LSI grouped-count workload,
- keep compact group_key/count columns remain CUDA-resident,
- preserve false public claim flags.

It does not:

- implement full RayJoin paper reproduction,
- implement overlay or PIP compact grouped-count routes,
- prove a public speedup claim,
- prove true zero-copy,
- authorize release.

This route is not a public speedup claim.

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Local validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3197_rayjoin_compact_grouped_count_route_test
```

Status: local source validation passed.

Pod validation artifact:

- `docs/reports/goal3197_rayjoin_compact_grouped_count_route_pod_2026-06-03.json`
- Commit under test: `71812e99`
- Focused pod tests: passed.
- App route smoke:
  `run_rayjoin_prepared_optix_compact_grouped_count_workload("lsi", include_rows=True)`
- Fixture result: `row_count = 1`, `compact_row_count = 1`, and returned count
  sum equals `row_count`.
- Compact grouped-count columns reported
  `output_residency = device_resident_compact_grouped_count_columns`.
- Claim flags remained false.

This fixture is intentionally small. It proves route correctness and metadata
shape, not performance.
