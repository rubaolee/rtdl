# Goal3280 Spatial Order Points 2D Generic Helper

Date: 2026-06-03

## Summary

Goal3278 showed that query-point order affects the prepared OptiX
point/closed-shape membership path. On the public CDB PIP slice, Morton/Z-order
query ordering improved the RTDL PIP median from `0.326065 ms` to `0.286076 ms`
and improved the native count-pass median from `0.256134 ms` to `0.207583 ms`,
while preserving the exact count `1430`.

This goal factors that app-local ordering logic into a generic Python RTDL
helper:

```python
rtdsl.spatial_order_points_2d(points, mode="morton_xy")
```

Supported modes are `natural`, `x_then_y`, `y_then_x`, and `morton_xy`.

## Boundary

This is a generic preparation/layout hint. It reorders caller-owned 2-D point
records before packing while preserving caller IDs. It does not add RayJoin,
PIP, closed-shape-membership, spatial-join, or app-specific semantics to the
native engine.

No new native ABI was added. The helper is intentionally a Python/runtime
surface first because Goal3278 shows a useful locality effect, but not a large
enough or broad enough win to justify a native contract by itself.

## Code Changes

- Added `src/rtdsl/spatial_order.py`.
- Exported `spatial_order_points_2d` and `SPATIAL_POINT_ORDER_MODES_2D`.
- Added the contract to the `dir(rtdsl)` learner-facing surface.
- Added primitive-discovery metadata node
  `execution.spatial_order_points_2d`.
- Regenerated `docs/rtdl_primitive_catalog.md`.
- Rewired the RayJoin benchmark app's `_order_points_for_locality` wrapper to
  delegate to `rtdsl.spatial_order_points_2d`.

## Validation

Focused local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3280_spatial_order_points_2d_generic_helper_test `
  tests.goal3278_rayjoin_pip_point_order_locality_probe_test `
  tests.goal3070_v2_7_primitive_discovery_core_test `
  tests.goal3090_v2_7_discovery_metadata_backfill_test `
  tests.goal3073_v2_7_generated_primitive_catalog_test
```

Result: `27` tests passed.

## Claim Boundary

- Release authorized: `false`
- RayJoin reproduction claim authorized: `false`
- RTDL beats RayJoin claim authorized: `false`
- Broad RT-core speedup claim authorized: `false`
- True zero-copy claim authorized: `false`

The accepted claim is narrow: RTDL now exposes the locality-ordering step from
Goal3278 as a reusable, app-agnostic helper and discoverable primitive node.
