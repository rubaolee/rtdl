# Goal1886 Segment/Polygon Prepared Partner Reuse

Date: 2026-05-13

Status: implementation-ready; pod timing pending

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

## Boundaries

This goal does not change the native ABI and does not authorize broad RT-core speedup wording.

Allowed wording after pod evidence:

- exact segment/polygon prepared partner-device hitcount timing rows;
- exact road-hazard prepared partner-device priority timing rows;
- reusable prepared scene plus reusable witness output buffers.

Not allowed:

- v2.0 release readiness;
- whole-app speedup;
- broad RT-core speedup;
- package-install claims.

## Next Validation

Next validation requires the NVIDIA pod:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1886_segment_polygon_prepared_partner_reuse_test tests.goal1863_segment_polygon_hitcount_v2_partner_perf_test tests.goal1865_road_hazard_partner_priority_flags_test
```

Then extend or add a timing runner that compares:

- v1.8 one-shot native OptiX rows;
- v1.8 reused prepared native OptiX rows;
- Goal1863 v2.0 unprepared partner device count columns;
- Goal1886 v2.0 prepared partner device count columns with reusable witness outputs.
