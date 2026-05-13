# Goal1881 Prepared Fixed-Radius Reusable Partner Outputs

Date: 2026-05-13

Status: implementation-ready; pod timing pending

## Summary

Goal1881 adds a narrow v2.0 fixed-radius hot-path improvement: prepared OptiX partner-device-column calls can now reuse caller-owned partner output columns across repeated runs. In short, the prepared path now reuses partner-owned output columns instead of allocating the fixed-radius result buffers inside every call.

This does not change the native ABI. The native OptiX ABI is unchanged. The native engine still sees only the generic `generic_fixed_radius_count_threshold_2d_device_columns` contract. App semantics for service coverage and event hotspot screening remain in Python/PyTorch/CuPy.

## What Changed

- Added `allocate_fixed_radius_count_threshold_2d_partner_device_output_columns(query_count, partner=...)`.
- Extended `fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns(...)` with optional `output_columns`.
- Extended `service_coverage_gap_flags_optix_prepared_partner_device_columns(...)` and `event_hotspot_flags_optix_prepared_partner_device_columns(...)` with optional `fixed_radius_output_columns`.
- Updated the Goal1878 timing harness so prepared v2.0 rows reuse the fixed-radius output buffers instead of allocating `query_ids`, `neighbor_counts`, and `threshold_flags` on every measured call.

## Performance Intent

The prior Goal1879 prepared path already avoids rebuilding the OptiX fixed-radius search GAS. This goal removes another repeated-call cost from the measured loop: partner tensor allocation for the output columns.

This should help the exact sub-path where a learner or app repeatedly asks the same prepared scene different fixed-radius questions. The expected gain is most visible in tight repeated-call loops and small-to-medium query batches, where Python/partner allocation overhead can obscure native traversal time.

## Boundaries

This goal does not change native traversal code, does not add a new native symbol, and does not authorize broad RT-core speedup wording.

The correct public wording remains narrow:

- allowed: prepared fixed-radius v2.0 partner-device calls can reuse partner-owned output buffers;
- allowed after pod evidence: exact timing rows for the prepared fixed-radius sub-path;
- not allowed: v2.0 release readiness;
- not allowed: whole-app speedup;
- not allowed: broad RT-core speedup.

## Next Validation

Next validation requires an NVIDIA pod with OptiX, PyTorch, and CuPy:

```powershell
$env:PYTHONPATH='src;.'
py -3 scripts\goal1878_fixed_radius_app_adapter_perf.py --sizes 256,1024,4096,16384 --repeat 7 --partner both --max-reference-pairs 16777216 --output docs\reports\goal1881_fixed_radius_reusable_outputs_pod.json
```

The runner should print progress regularly if expanded for long-size sweeps. If large dense partner-reference rows become memory-bound, the report must mark those rows as skipped or bounded rather than hanging silently.
