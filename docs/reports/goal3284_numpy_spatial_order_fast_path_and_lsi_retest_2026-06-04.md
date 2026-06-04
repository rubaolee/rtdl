# Goal3284 NumPy Spatial Order Fast Path And LSI Retest

Date: 2026-06-04

## Summary

Goal3284 adds an optional NumPy fast path inside the generic helpers:

```python
rtdsl.spatial_order_points_2d(...)
rtdsl.spatial_order_segments_2d(...)
```

The public contract is unchanged. If NumPy is unavailable or the records cannot
be coerced, the helpers fall back to the deterministic pure-Python path.

This goal was motivated by Goal3282: segment locality can affect the RayJoin LSI
prepared-query lane, but standalone Python sorting was too expensive to be a
serious end-to-end path.

## Implementation

- Added NumPy `lexsort` ordering for `x_then_y`, `y_then_x`, and `morton_xy`.
- Added vectorized 16-bit Morton/Z-order code generation for the NumPy path.
- Tightened record field accessors so dataclass/object records use direct
  `getattr` reads with mapping fallback, avoiding repeated generic `hasattr`
  checks.
- Kept ordering stable by caller `id`.

No native ABI was added.

## Microdiagnostic On Pod

Dataset:

`br_county_start256_count512.cdb + br_soil_start256_count512.cdb`

Segment counts:

- left/query segments: `19987`
- right/static segments: `6825`

After the accessor patch at commit `bd3893c7`:

| Side | Mode | NumPy ms | Pure Python ms | Same order |
| --- | --- | ---: | ---: | --- |
| left | `x_then_y` | 38.590 | 46.152 | true |
| left | `y_then_x` | 39.121 | 52.000 | true |
| left | `morton_xy` | 38.131 | 96.831 | true |
| right | `x_then_y` | 13.684 | 12.649 | true |
| right | `y_then_x` | 13.504 | 17.821 | true |
| right | `morton_xy` | 13.252 | 34.970 | true |

The fast path materially helps Morton ordering and helps the larger left side,
but record extraction still dominates.

## Full Pod Retest

Source-clean pod artifacts are saved under:

`docs/reports/goal3284_accessor_lsi_segment_order_pod/`

All artifacts record `source_dirty: []` and preserve LSI count `269`.

| Segment order | RTDL LSI query ms | RayJoin query ms | RTDL/RayJoin | Query order ms | Static order ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| `natural` | 0.556655 | 0.244212 | 2.279x | 0.004990 | 0.000849 |
| `x_then_y` | 0.557600 | 0.234699 | 2.376x | 40.277125 | 14.190482 |
| `y_then_x` | 0.626929 | 0.248599 | 2.522x | 41.093670 | 14.105642 |
| `morton_xy` | 0.662375 | 0.248694 | 2.663x | 39.785178 | 13.872517 |

The same run also exercised PIP with `morton_xy` point ordering as a control
lane. PIP point-order overhead stayed low, around `1.19-1.27 ms`.

## Interpretation

This is a partial helper win and a negative LSI promotion result.

The helper itself is better: NumPy + faster accessors reduce segment-ordering
cost, especially for Morton order. But the LSI benchmark still does not get a
robust query-lane win, and the standalone ordering cost remains tens of
milliseconds for the public CDB slice.

Therefore, RTDL should not promote Python-side segment ordering as a RayJoin LSI
performance path. The next serious route is a packed/prepared layout primitive:
ordering must be fused into packing, cached in prepared handles, or performed
inside native/partner preprocessing so users do not pay a separate Python
record-sort pass.

## Validation

Local focused validation before pod:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3280_spatial_order_points_2d_generic_helper_test `
  tests.goal3282_spatial_order_segments_2d_lsi_probe_test `
  tests.goal3244_rayjoin_same_slice_repeated_count_runner_test `
  tests.goal3070_v2_7_primitive_discovery_core_test `
  tests.goal3090_v2_7_discovery_metadata_backfill_test `
  tests.goal3073_v2_7_generated_primitive_catalog_test
```

Result: `41` tests passed.

Pod focused validation:

```bash
python3 -m unittest \
  tests.goal3280_spatial_order_points_2d_generic_helper_test \
  tests.goal3282_spatial_order_segments_2d_lsi_probe_test \
  tests.goal3244_rayjoin_same_slice_repeated_count_runner_test \
  tests.goal3070_v2_7_primitive_discovery_core_test \
  tests.goal3090_v2_7_discovery_metadata_backfill_test \
  tests.goal3073_v2_7_generated_primitive_catalog_test
```

Result: `41` tests passed.

## Claim Boundary

- Release authorized: `false`
- RayJoin reproduction claim authorized: `false`
- RTDL beats RayJoin claim authorized: `false`
- Broad RT-core speedup claim authorized: `false`
- True zero-copy claim authorized: `false`

Accepted claim: RTDL has a faster generic spatial-order helper with source-clean
pod evidence, but LSI segment ordering remains a diagnostic, not a promoted
performance path.
