# Goal3181: Geometry Relation Row-View Typed Producer Metadata

Date: 2026-06-03

## Purpose

Goal3180 added v2.8 typed producer metadata for generic 3-D ray/triangle hit
streams. That was useful for graph-style ray/triangle candidate rows, but it
was not the exact producer family used by the current Spatial RayJoin prepared
OptiX route.

Spatial RayJoin currently lowers to app-agnostic 2-D geometry relation outputs:

| Generic row schema | Producer primitive |
| --- | --- |
| `point_id`, `shape_id`, `membership` | `point_closed_shape_membership_2d` |
| `left_id`, `right_id`, `intersection_point_x`, `intersection_point_y` | `segment_pair_intersection_2d` |
| `left_polygon_id`, `right_polygon_id`, `requires_lsi`, `requires_pip` | `shape_pair_relation_flags_2d` |

Goal3181 adds v2.8 typed producer metadata for those generic relation-row
schemas and exposes it from `OptixRowView`.

## Code Changes

- Added `src/rtdsl/v2_8_geometry_relation_typed_stream.py`.
- Added `make_v2_8_geometry_relation_typed_stream_contract(...)`.
- Added `make_v2_8_geometry_relation_typed_producer_metadata(...)`.
- Added `geometry_relation_typed_stream_metadata_for_row_view(...)`.
- Added `OptixRowView.to_v2_8_typed_result_stream_metadata()`.
- Exported the new helpers and constants from `rtdsl`.
- Refreshed the Spatial RayJoin runtime-gap row so it names generic 2-D
  relation-row typed producer metadata instead of treating the 3-D
  ray/triangle hit-stream contract as a proxy.

## Boundary

This goal is intentionally a metadata step over host row views. It does not move
the prepared point/shape, segment-pair, or shape-pair outputs to native
device-resident relation-row columns.

Remaining Spatial RayJoin work:

- device-resident relation-row output,
- parity/count grouping over resident rows,
- boundary-witness ownership at serious scale,
- pod performance evidence after the app adopts the resident route.

In short, device-resident relation-row output remains future work.

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Local validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3181_geometry_relation_row_view_typed_producer_metadata_test tests.goal3180_ray_triangle_hit_stream_typed_producer_metadata_test tests.goal3172_v2_8_runtime_gap_compact_mask_refresh_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Pod validation is the next required step before this report records current
NVIDIA evidence.
