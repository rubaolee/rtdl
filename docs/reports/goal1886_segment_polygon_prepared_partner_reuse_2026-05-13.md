# Goal1886 Segment/Polygon Prepared Partner Reuse

Date: 2026-05-13

Status: measured-with-boundary

## Summary

Goal1886 extends the v2.0 partner-device reuse pattern from fixed-radius to the segment/polygon hitcount and road-hazard path.

The native engine contract stays generic: `generic_ray_primitive_witness_pairs`. The Python partner layer owns the app meaning:

- segment/polygon hitcount is built from generic witness pairs with PyTorch/CuPy duplicate-pair reduction;
- road-hazard priority is a Python/PyTorch/CuPy threshold over those hit counts;
- native OptiX does not see road, hazard, polygon-hitcount, or app-specific semantics.

## What Changed

- Added `prepare_segment_polygon_anyhit_optix_partner_device_scene(...)` for reusable triangle-scene preparation from partner-owned triangle columns.
- Added `allocate_segment_polygon_witness_partner_device_output_columns(...)` for reusable witness output columns owned by the selected partner.
- Added `segment_polygon_hitcount_optix_prepared_partner_device_count_columns(...)`.
- Added `road_hazard_priority_flags_optix_prepared_partner_device_columns(...)`.
- Added Python-side witness output length guards so mismatched reusable buffers fail before the native call.

## Performance Intent

Goal1863 showed that v2.0 partner device count columns are faster than the v1.8 prepared native row path at 2048 synthetic rows, but still pay repeated triangle-scene preparation and witness-output allocation overhead. This goal removes those repeated-call costs from the partner path.

The expected win is the exact repeated-query subpath where one prepared triangle scene is reused for many ray batches.

## Pod Validation

Pod commands:

```powershell
$env:PYTHONPATH='src:.'
python3 scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py --count 512 --iterations 5 --partners cupy,torch --output docs/reports/goal1886_segment_polygon_prepared_reuse_pod_512.json
python3 scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py --count 2048 --iterations 5 --partners cupy,torch --output docs/reports/goal1886_segment_polygon_prepared_reuse_pod_2048.json
```

Hardware:

- Host: `213.192.2.116:40189`
- GPU: NVIDIA GeForce RTX 3090
- Driver: `580.126.20`
- Validation clone commit: `61a62ed3`

Artifacts:

- `docs/reports/goal1886_segment_polygon_prepared_reuse_pod_512.json`
- `docs/reports/goal1886_segment_polygon_prepared_reuse_pod_2048.json`

## Timing Results

The Goal1886 prepared partner reuse row improves the v2.0 unprepared partner path and beats the fair v1.8 prepared native row path at 2048 synthetic rows.

| Count | Partner | v1.8 prepared native rows | Goal1863 unprepared partner columns | Goal1886 prepared partner reuse | Speedup vs v1.8 prepared | Speedup vs unprepared partner |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 512 | CuPy | 0.000983399 s | 0.001503688 s | 0.001030499 s | 0.95x | 1.46x |
| 512 | Torch | 0.000983399 s | 0.001158919 s | 0.000722539 s | 1.36x | 1.60x |
| 2048 | CuPy | 0.003603125 s | 0.001586638 s | 0.001079589 s | 3.34x | 1.47x |
| 2048 | Torch | 0.003603125 s | 0.001283818 s | 0.000795269 s | 4.53x | 1.61x |

The one-shot v1.8 app-wall row remains much slower at 2048 rows, but the fair repeated-query comparison is the reused prepared native row above.

## Boundaries

This goal does not change the native ABI and does not authorize broad RT-core speedup wording.

Allowed wording:

- exact segment/polygon prepared partner-device hitcount timing rows;
- exact road-hazard prepared partner-device priority timing rows;
- reusable prepared scene plus reusable witness output buffers.

Not allowed:

- v2.0 release readiness;
- whole-app speedup;
- broad RT-core speedup;
- package-install claims.

## Next Validation

The timing row is now measured for segment/polygon hitcount. Road-hazard prepared priority flags reuse the same prepared hitcount path plus a partner tensor threshold; a separate road-hazard app timing row can be added if we need public wording for that app specifically.
