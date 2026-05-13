# Goal1881 Prepared Fixed-Radius Reusable Partner Outputs

Date: 2026-05-13

Status: measured-with-boundary

## Summary

Goal1881 adds a narrow v2.0 fixed-radius hot-path improvement: prepared OptiX partner-device-column calls can now reuse caller-owned partner output columns across repeated runs. In short, the prepared path now reuses partner-owned output columns instead of allocating the fixed-radius result buffers inside every call.

This does not change the native ABI. The native OptiX ABI is unchanged. The native engine still sees only the generic `generic_fixed_radius_count_threshold_2d_device_columns` contract. App semantics for service coverage and event hotspot screening remain in Python/PyTorch/CuPy.

## What Changed

- Added `allocate_fixed_radius_count_threshold_2d_partner_device_output_columns(query_count, partner=...)`.
- Extended `fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns(...)` with optional `output_columns`.
- Extended `service_coverage_gap_flags_optix_prepared_partner_device_columns(...)` and `event_hotspot_flags_optix_prepared_partner_device_columns(...)` with optional `fixed_radius_output_columns`.
- Added a Python-side reused-output length guard so mismatched buffers fail before entering the native OptiX call.
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

## Pod Validation

Pod command:

```powershell
$env:PYTHONPATH='src;.'
py -3 scripts\goal1878_fixed_radius_app_adapter_perf.py --sizes 256,1024,4096,16384 --repeat 7 --partner both --max-reference-pairs 16777216 --output docs\reports\goal1881_fixed_radius_reusable_outputs_pod.json
```

Hardware:

- Host: `213.192.2.116:40189`
- GPU: NVIDIA GeForce RTX 3090
- Driver: `580.126.20`
- Validation clone commit: `cf0c41a4` on the pod, equivalent to local Goal1881 plus the fair `v1_8_reused_prepared_optix` harness correction.

Local artifact:

- `docs/reports/goal1881_fixed_radius_reusable_outputs_pod.json`

The pod run passed the Goal1881/1879/1878 test slice and produced timing rows for Torch and CuPy at sizes 256, 1024, 4096, and 16384.

## Timing Results

The strongest exact-subpath result is at size 16384:

| Partner | App Adapter | v1.8 reused prepared OptiX median | v2.0 prepared partner-device reusable-output median | Speedup vs reused v1.8 | Speedup vs app-wall v1.8 |
| --- | --- | ---: | ---: | ---: | ---: |
| Torch | service coverage gaps | 0.036172174 s | 0.000294579 s | 122.8x | 148.5x |
| Torch | event hotspot screening | 0.033575908 s | 0.000220870 s | 152.0x | 452.9x |
| CuPy | service coverage gaps | 0.033959968 s | 0.000265950 s | 127.7x | 162.1x |
| CuPy | event hotspot screening | 0.033781507 s | 0.000229210 s | 147.4x | 460.4x |

For size 4096, the v2.0 prepared reusable-output path also beats both the reused v1.8 prepared OptiX path and the dense Torch/CuPy reference path:

| Partner | App Adapter | v1.8 reused prepared OptiX median | Dense partner reference median | v2.0 prepared reusable-output median |
| --- | --- | ---: | ---: | ---: |
| Torch | service coverage gaps | 0.008046330 s | 0.001129388 s | 0.000293410 s |
| Torch | event hotspot screening | 0.007920130 s | 0.002049197 s | 0.000209859 s |
| CuPy | service coverage gaps | 0.007904800 s | 0.001064489 s | 0.000270170 s |
| CuPy | event hotspot screening | 0.007886230 s | 0.001988027 s | 0.000229680 s |

At sizes 256 and 1024, the dense partner tensor reference remains slightly faster than the v2.0 prepared native path for some rows. This goal therefore supports a larger repeated prepared fixed-radius subpath claim, not an "always faster for every batch size" claim.

Dense partner-reference rows for size 16384 were intentionally skipped because they would materialize 134,217,728 or 268,435,456 pairwise distances. This is an explicit benchmark safety boundary, not a v2.0 claim expansion.

## Remaining Validation

The runner now prints progress regularly. If larger dense partner-reference rows become memory-bound, the report must keep marking those rows as skipped or bounded rather than hanging silently.
